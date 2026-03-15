import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trends_v2.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Tabloları V2 şemasına göre oluştur."""
    conn = get_connection()
    
    # 1. Ham Sinyaller (Collector'lardan gelen veriler)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            source          TEXT NOT NULL,          -- 'reddit_rss' | 'hackernews' | 'google_trends' | 'pinterest'
            subsource       TEXT,                   -- e.g. 'r/funny', 'topstories'
            raw_title       TEXT NOT NULL,
            url             TEXT,
            engagement      INTEGER DEFAULT 0,      -- upvote, view, vs.
            captured_at     TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_source_time ON signals(source, captured_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_title ON signals(raw_title)")

    # 2. Semantic Clusters
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trend_clusters (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            representative_phrase TEXT NOT NULL,
            niche                 TEXT,
            created_at            TEXT NOT NULL,
            last_updated          TEXT NOT NULL
        )
    """)

    # 3. Normalize Trendler
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trends (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            normalized_phrase TEXT NOT NULL,
            cluster_id        INTEGER REFERENCES trend_clusters(id),
            first_seen        TEXT NOT NULL,
            last_seen         TEXT NOT NULL,
            total_mentions    INTEGER DEFAULT 0,
            analyzed          INTEGER DEFAULT 0,      -- 0: analiz edilmedi, 1: edildi
            radar_score       REAL DEFAULT 0.0,       -- Momentum + Novelty skoru
            ai_score          REAL DEFAULT 0.0,       -- Gemini POD potansiyel skoru
            niche             TEXT DEFAULT 'general',
            humor             REAL DEFAULT 0.0,
            identity          REAL DEFAULT 0.0,
            giftability       REAL DEFAULT 0.0,
            design            REAL DEFAULT 0.0
        )
    """)
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_trends_phrase ON trends(normalized_phrase)")

    # 4. Zaman Serisi Sinyalleri (Momentum Hesabı İçin)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trend_signals (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_id        INTEGER REFERENCES trends(id),
            platform        TEXT NOT NULL,
            mentions        INTEGER DEFAULT 1,
            engagement_sum  INTEGER DEFAULT 0,
            captured_at     TEXT NOT NULL       -- YYYY-MM-DD
        )
    """)

    # 5. Embeddings
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trend_embeddings (
            trend_id        INTEGER REFERENCES trends(id),
            vector_blob     BLOB NOT NULL,
            dim             INTEGER DEFAULT 384,
            created_at      TEXT NOT NULL,
            PRIMARY KEY (trend_id)
        )
    """)

    # 6. Outputs (Pydantic şemalarından gelen JSON stringleri)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS outputs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_id        INTEGER REFERENCES trends(id),
            output_type     TEXT NOT NULL,          -- 'design_prompt' | 'etsy_listing' | 'social_content' | 'printify_draft'
            content         TEXT NOT NULL,          -- JSON string
            created_at      TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


# ── V2 Veritabanı API ────────────────────────────────────────────────────────

def insert_signal(source: str, raw_title: str, url: str = None, engagement: int = 0, subsource: str = None) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO signals (source, subsource, raw_title, url, engagement, captured_at) VALUES (?, ?, ?, ?, ?, ?)",
        (source, subsource, raw_title, url, engagement, datetime.utcnow().isoformat())
    )
    sig_id = cur.lastrowid
    conn.commit()
    conn.close()
    return sig_id


def get_unprocessed_signals(limit=100):
    """Extraction phase için henüz normalize edilmemiş sinyalleri getirir."""
    # Basitlik için: Bir sinyal trends tablosuna hiç yansımamış gibi düşünüp hepsini çeken veya ayrı bir queue yapısı kullanılabilecek flag eklenebilir. 
    # V2 mimarisinde ekstra bir parsed_flag eklenebilir veya en son çalışılan zaman üzerinden filtre denebilir.
    # Şimdilik son gelen sinyalleri getiriyoruz.
    conn = get_connection()
    rows = conn.execute("SELECT id, source, raw_title, url, engagement, captured_at FROM signals ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows


def upsert_trend(normalized_phrase: str, platform: str, engagement: int) -> int:
    """Trend tablosuna ekler veya var olanı günceller. Aynı zamanda time_series sinyali ekler."""
    conn = get_connection()
    now = datetime.utcnow()
    now_iso = now.isoformat()
    today_str = now.strftime('%Y-%m-%d')
    
    # 1. Trend Bul veya Yarat
    existing = conn.execute("SELECT id FROM trends WHERE normalized_phrase = ?", (normalized_phrase,)).fetchone()
    
    try:
        if existing:
            trend_id = existing[0]
            conn.execute(
                "UPDATE trends SET last_seen = ?, total_mentions = total_mentions + 1 WHERE id = ?",
                (now_iso, trend_id)
            )
        else:
            cur = conn.execute(
                "INSERT INTO trends (normalized_phrase, first_seen, last_seen, total_mentions) VALUES (?, ?, ?, ?)",
                (normalized_phrase, now_iso, now_iso, 1)
            )
            trend_id = cur.lastrowid
            
        # 2. Zaman Serisi Güncelleme (Gün Bazlı Agregasyon)
        ts_existing = conn.execute(
            "SELECT id FROM trend_signals WHERE trend_id = ? AND platform = ? AND captured_at = ?",
            (trend_id, platform, today_str)
        ).fetchone()
        
        if ts_existing:
            conn.execute(
                "UPDATE trend_signals SET mentions = mentions + 1, engagement_sum = engagement_sum + ? WHERE id = ?",
                (engagement, ts_existing[0])
            )
        else:
            conn.execute(
                "INSERT INTO trend_signals (trend_id, platform, mentions, engagement_sum, captured_at) VALUES (?, ?, ?, ?, ?)",
                (trend_id, platform, 1, engagement, today_str)
            )
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        
    return trend_id


def insert_output(trend_id: int, output_type: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO outputs (trend_id, output_type, content, created_at) VALUES (?,?,?,?)",
        (trend_id, output_type, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_outputs_for_trend(trend_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT output_type, content, created_at FROM outputs WHERE trend_id=? ORDER BY created_at",
        (trend_id,)
    ).fetchall()
    conn.close()
    return rows


def get_unanalyzed(limit=50, min_mentions=1):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, normalized_phrase, 'extracted' as source, '' as subreddit "
        "FROM trends WHERE analyzed=0 AND total_mentions >= ? "
        "ORDER BY total_mentions DESC LIMIT ?", 
        (min_mentions, limit)
    ).fetchall()
    conn.close()
    return rows


def update_scores(trend_id: int, humor: float, identity: float, giftability: float, design: float, score: float, niche: str):
    conn = get_connection()
    conn.execute(
        """UPDATE trends 
           SET analyzed=1, ai_score=?, humor=?, identity=?, giftability=?, design=?, niche=? 
           WHERE id=?""",
        (score, humor, identity, giftability, design, niche, trend_id)
    )
    conn.commit()
    conn.close()


def get_top_trends(limit=50, min_score=7.0):
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, normalized_phrase, 'extracted' as source, '' as subreddit, 
                  ai_score as trend_score, niche, humor, identity, giftability, design, first_seen as created_at
           FROM trends 
           WHERE analyzed=1 AND ai_score >= ? 
           ORDER BY ai_score DESC LIMIT ?""",
        (min_score, limit)
    ).fetchall()
    conn.close()
    return rows
