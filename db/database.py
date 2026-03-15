import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

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
    
    # 1. Ham Sinyaller
    cur.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id              SERIAL PRIMARY KEY,
            source          TEXT NOT NULL,
            subsource       TEXT,
            raw_title       TEXT NOT NULL,
            url             TEXT,
            engagement      INTEGER DEFAULT 0,
            captured_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trends_phrase ON trends(normalized_phrase)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trends_score ON trends(ai_score)")

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

    # 5. Output Tablosu
    cur.execute("""
        CREATE TABLE IF NOT EXISTS outputs (
            id              SERIAL PRIMARY KEY,
            trend_id        INTEGER REFERENCES trends(id),
            output_type     TEXT NOT NULL,
            content         TEXT NOT NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()


# ── V2 Veritabanı API ────────────────────────────────────────────────────────

def insert_signal(source: str, raw_title: str, subsource: str = None, url: str = None, engagement: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO signals (source, subsource, raw_title, url, engagement) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (source, subsource, raw_title, url, engagement)
    )
    sig_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return sig_id


def get_unprocessed_signals(limit=100):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, source, raw_title, url, engagement, captured_at FROM signals ORDER BY id DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def upsert_trend(normalized_phrase: str, platform: str, engagement: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')
    
    try:
        # 1. Trend Bul veya Yarat
        cur.execute("SELECT id FROM trends WHERE normalized_phrase = %s", (normalized_phrase,))
        existing = cur.fetchone()
        
        if existing:
            trend_id = existing[0]
            cur.execute(
                "UPDATE trends SET last_seen = %s, total_mentions = total_mentions + 1 WHERE id = %s",
                (now, trend_id)
            )
        else:
            cur.execute(
                "INSERT INTO trends (normalized_phrase, first_seen, last_seen, total_mentions) VALUES (%s, %s, %s, 1) RETURNING id",
                (normalized_phrase, now, now)
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
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
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
        "SELECT id, normalized_phrase, 'extracted' as source, '' as subreddit "
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


def get_top_trends(limit=50, min_score=7.0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, normalized_phrase, 'extracted' as source, '' as subreddit, "
        "ai_score as trend_score, niche, humor, identity, giftability, design, first_seen as created_at "
        "FROM trends WHERE analyzed=1 AND ai_score >= %s "
        "ORDER BY ai_score DESC LIMIT %s",
        (min_score, limit)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
