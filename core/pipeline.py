"""
Core Pipeline Functions
-----------------------
Gerekli olan tüm pipeline adımları burada tanımlanır.
Bu modül sayesinde import döngüleri (circular imports) önlenir.
"""

import logging
from datetime import datetime
from config.loader import config

_analysis_cfg = config.get('analysis', {})

def header(text: str):
    print(f"\n{'─'*50}")
    print(f"  {text}")
    print(f"{'─'*50}")

def run_collect():
    header("ADIM 1/4 — Veri Toplama")

    print("\n[Reddit]")
    from collectors.reddit_rss import collect as collect_reddit
    n1 = collect_reddit(verbose=True)
    print(f"  Toplam: {n1} sinyal")

    print("\n[HackerNews]")
    from collectors.hackernews import collect as collect_hn
    nh = collect_hn(verbose=True)
    print(f"  Toplam: {nh} sinyal")

    print("\n[Google Trends]")
    from collectors.google_trends import discover_and_save, update_google_interest
    n2 = discover_and_save(verbose=True)
    print(f"  Yeni keşif: {n2} sinyal")

def run_extract():
    header("ADIM 2/4 — Veri Çıkarımı (Phrase Extraction)")
    from db.database import get_unprocessed_signals, upsert_trend, mark_signals_processed, get_connection
    from extraction.phrase_extractor import extract_phrases_tfidf
    
    rows = get_unprocessed_signals(limit=500)
    if not rows:
        print("  İşlenecek yeni sinyal yok.")
        return
        
    titles = [row[2] for row in rows]
    extracted = extract_phrases_tfidf(titles)
    
    conn = get_connection()
    cur = conn.cursor()
    saved = 0
    signal_ids = []
    
    try:
        for row in rows:
            # SELECT id, source, raw_title, url, engagement, captured_at, subsource
            sig_id, source, raw_title, url, engagement, captured_at, subsource = row
            phrase = extracted.get(raw_title, raw_title)
            upsert_trend(normalized_phrase=phrase, platform=source, engagement=engagement, cur=cur, subreddit=subsource)
            signal_ids.append(sig_id)
            saved += 1
            
        cur.execute("UPDATE signals SET processed = TRUE WHERE id = ANY(%s)", (signal_ids,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"  Extraction hatası: {e}")
    finally:
        cur.close()
        conn.close()
        
    print(f"  Toplam: {saved} sinyal tişört trendlerine (phrase) çıkarıldi.")

def run_analyze(limit: int = None, min_mentions: int = None):
    header("ADIM 3/4 — Gemini Analizi")
    from analyzer.gemini_scoring import analyze_batch
    _limit = limit if limit is not None else _analysis_cfg.get('default_limit', 40)
    _mentions = min_mentions if min_mentions is not None else _analysis_cfg.get('min_mentions', 3)
    n = analyze_batch(verbose=True, min_mentions=_mentions, limit=_limit)
    print(f"\n  Toplam analiz: {n} trend")

def run_generate():
    header("ADIM 4/4 — Output Üretimi")
    from generator.generators import run_output_pipeline
    n = run_output_pipeline(verbose=True)
    print(f"\n  Toplam üretilen: {n} içerik seti")

def run_momentum():
    header("MOMENTUM ENGINE — Viral Doğrulama")
    from validation.momentum import hybrid_validate
    from db.database import get_connection
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT normalized_phrase, total_mentions FROM trends WHERE total_mentions >= 20 ORDER BY total_mentions DESC")
    candidates = cur.fetchall()
    cur.close()
    conn.close()
    
    if not candidates:
        print("  Sistemde henüz eşiği (20 mention) aşan viral adayı yok.")
        return
        
    print(f"  {len(candidates)} aday kontrol ediliyor...")
    for phrase, count in candidates:
        res = hybrid_validate(phrase, count, threshold=20)
        ext = res["external_validation"]
        status = "✅ ONAYLANDI" if ext.get("valid") else "⏳ Beklemede"
        print(f"  → '{phrase}': {status} (Skor: {ext.get('score', 0)})")
