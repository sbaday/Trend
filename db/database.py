import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Railway provides DATABASE_URL automatically
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set!")
    
    # Railway postgresql:// → postgres:// dönüşümü (psycopg2 uyumu için)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgres://", 1)
    
    # Prefix temizleme (DATABASE_URL= kısmı kazara eklenmişse)
    if url.startswith("DATABASE_URL="):
        url = url.replace("DATABASE_URL=", "", 1)
        
    return psycopg2.connect(url)


def init_db():
    """Tabloları PostgreSQL şemasına göre oluştur."""
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Ham Sinyaller (Migration: processed sütunu ekle)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id              SERIAL PRIMARY KEY,
            source          TEXT NOT NULL,
            subsource       TEXT,
            raw_title       TEXT NOT NULL,
            url             TEXT,
            engagement      INTEGER DEFAULT 0,
            processed       BOOLEAN DEFAULT FALSE,
            captured_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("ALTER TABLE signals ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_title ON signals(raw_title)")

    # 2. Semantic Clusters
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trend_clusters (
            id                    SERIAL PRIMARY KEY,
            representative_phrase TEXT NOT NULL,
            niche                 TEXT,
            created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Normalize Trendler
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trends (
            id                SERIAL PRIMARY KEY,
            normalized_phrase TEXT NOT NULL,
            cluster_id        INTEGER REFERENCES trend_clusters(id),
            first_seen        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_mentions    INTEGER DEFAULT 0,
            analyzed          INTEGER DEFAULT 0,
            radar_score       REAL DEFAULT 0.0,
            ai_score          REAL DEFAULT 0.0,
            niche             TEXT DEFAULT 'general',
            humor             REAL DEFAULT 0.0,
            identity          REAL DEFAULT 0.0,
            giftability       REAL DEFAULT 0.0,
            design            REAL DEFAULT 0.0
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trends_score ON trends(ai_score)")
    cur.execute("ALTER TABLE trends ADD COLUMN IF NOT EXISTS subreddit TEXT")

    # 4. Zaman Serisi (Günlük Agregasyon)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trend_signals (
            id              SERIAL PRIMARY KEY,
            trend_id        INTEGER REFERENCES trends(id),
            platform        TEXT NOT NULL,
            mentions        INTEGER DEFAULT 0,
            engagement_sum  INTEGER DEFAULT 0,
            captured_at     DATE NOT NULL,
            UNIQUE(trend_id, platform, captured_at)
        )
    """)

    # 6. Trend Embeddings (Pre-V3)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trend_embeddings (
            id              SERIAL PRIMARY KEY,
            trend_id        INTEGER REFERENCES trends(id) UNIQUE,
            embedding       REAL[], -- Array for semantic vectors
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # ── V2.1 Migrations: Sentiment & Longevity ───────────────────────────────
    cur.execute("ALTER TABLE trends ADD COLUMN IF NOT EXISTS sentiment_score REAL DEFAULT 0.0")
    cur.execute("ALTER TABLE trends ADD COLUMN IF NOT EXISTS longevity_days  INTEGER DEFAULT 0")
    cur.execute("ALTER TABLE signals ADD COLUMN IF NOT EXISTS first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    cur.execute("ALTER TABLE signals ADD COLUMN IF NOT EXISTS last_seen_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    conn.commit()
    cur.close()
    conn.close()


# ── V2 Veritabanı API ────────────────────────────────────────────────────────

def insert_signal(source: str, raw_title: str, subsource: str = None, url: str = None, engagement: int = 0):
    """Sinyal ekler. Daha önce eklendiyse last_seen_at günceller."""
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow()
    # Duplicate raw_title kaydı olmaması için: aynı title varsa sadece last_seen_at güncelle
    cur.execute(
        """
        INSERT INTO signals (source, subsource, raw_title, url, engagement, first_seen_at, last_seen_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (source, subsource, raw_title, url, engagement, now, now)
    )
    sig_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return sig_id


def get_unprocessed_signals(limit=500):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, source, raw_title, url, engagement, captured_at, subsource FROM signals WHERE processed = FALSE ORDER BY id ASC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def mark_signals_processed(signal_ids):
    if not signal_ids: return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE signals SET processed = TRUE WHERE id = ANY(%s)", (signal_ids,))
    conn.commit()
    cur.close()
    conn.close()


def upsert_trend(normalized_phrase: str, platform: str, engagement: int, cur=None, subreddit: str = None) -> int:
    """
    Trend tablosuna yazar veya günceller. 
    Batch işlemler için dışarıdan 'cur' (cursor) kabul eder.
    Yeni trendlerde otomatik olarak sentiment_score hesaplar.
    """
    external_cur = cur is not None
    conn = None
    if not external_cur:
        conn = get_connection()
        cur = conn.cursor()
        
    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')
    
    try:
        # 1. Trend Bul veya Yarat
        cur.execute("SELECT id, first_seen FROM trends WHERE normalized_phrase = %s", (normalized_phrase,))
        existing = cur.fetchone()
        
        if existing:
            trend_id, first_seen = existing
            longevity = (now - first_seen).days if first_seen else 0
            cur.execute(
                "UPDATE trends SET last_seen = %s, total_mentions = total_mentions + 1, longevity_days = %s, subreddit = COALESCE(subreddit, %s) WHERE id = %s",
                (now, longevity, subreddit, trend_id)
            )
        else:
            # Sentiment: yeni phrase için hesapla
            try:
                from analyzer.sentiment import score_sentiment
                sentiment = score_sentiment(normalized_phrase)
            except Exception:
                sentiment = 0.0

            cur.execute(
                "INSERT INTO trends (normalized_phrase, first_seen, last_seen, total_mentions, sentiment_score, longevity_days, subreddit) VALUES (%s, %s, %s, 1, %s, 0, %s) RETURNING id",
                (normalized_phrase, now, now, sentiment, subreddit)
            )
            trend_id = cur.fetchone()[0]
            
        # 2. Zaman Serisi Güncelleme
        cur.execute(
            "INSERT INTO trend_signals (trend_id, platform, mentions, engagement_sum, captured_at) "
            "VALUES (%s, %s, 1, %s, %s) "
            "ON CONFLICT (trend_id, platform, captured_at) DO UPDATE SET "
            "mentions = trend_signals.mentions + 1, "
            "engagement_sum = trend_signals.engagement_sum + EXCLUDED.engagement_sum",
            (trend_id, platform, engagement, today_str)
        )
            
        if not external_cur:
            conn.commit()
    except Exception as e:
        if not external_cur and conn:
            conn.rollback()
        raise e
    finally:
        if not external_cur:
            cur.close()
            conn.close()
    return trend_id


def insert_output(trend_id: int, output_type: str, content: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO outputs (trend_id, output_type, content) VALUES (%s, %s, %s)",
        (trend_id, output_type, content)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_outputs_for_trend(trend_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT output_type, content, created_at FROM outputs WHERE trend_id=%s ORDER BY created_at",
        (trend_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_unanalyzed(limit=50, min_mentions=1):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, normalized_phrase, 'extracted' as source, '' as subreddit, total_mentions "
        "FROM trends WHERE analyzed=0 AND total_mentions >= %s "
        "ORDER BY total_mentions DESC LIMIT %s", 
        (min_mentions, limit)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_scores(trend_id: int, humor: float, identity: float, giftability: float, design: float, score: float, niche: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE trends SET analyzed=1, ai_score=%s, humor=%s, identity=%s, giftability=%s, design=%s, niche=%s WHERE id=%s",
        (score, humor, identity, giftability, design, niche, trend_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_top_trends(limit=50, min_score=7.0, niches=None, start_date=None, end_date=None):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT id, normalized_phrase, 'extracted' as source, COALESCE(subreddit, '') as subreddit, 
        ai_score as trend_score, niche, humor, identity, giftability, design, first_seen as created_at 
        FROM trends 
        WHERE analyzed=1 AND ai_score >= %s
    """
    params = [min_score]
    
    if niches:
        query += " AND niche = ANY(%s)"
        params.append(niches)
    
    if start_date:
        query += " AND first_seen >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND first_seen <= %s"
        params.append(end_date)
        
    query += " ORDER BY ai_score DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
