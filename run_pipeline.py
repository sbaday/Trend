"""
Pipeline Runner
---------------
Tüm sistemi sırayla çalıştırır:
  1. Reddit collector
  2. Google Trends collector
  3. Claude analyzer
  4. Output generators

Kullanım:
    python run_pipeline.py            # tam pipeline
    python run_pipeline.py --collect  # sadece veri toplama
    python run_pipeline.py --extract  # sadece phrase çıkarımı
    python run_pipeline.py --analyze  # sadece analiz
    python run_pipeline.py --generate # sadece output üretimi
"""

import sys
import argparse
from datetime import datetime


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

    # print("\n[Pinterest]")
    # from collectors.pinterest_collector import collect as collect_pinterest
    # np = collect_pinterest(verbose=True)
    # print(f"  Toplam: {np} sinyal")

    print("\n[Google Trends]")
    from collectors.google_trends import discover_and_save, update_google_interest
    n2 = discover_and_save(verbose=True)
    # update_google_interest(verbose=True) - skipping for signals step
    print(f"  Yeni keşif: {n2} sinyal")


def run_extract():
    header("ADIM 2/4 — Veri Çıkarımı (Phrase Extraction)")
    from db.database import get_unprocessed_signals, upsert_trend
    from extraction.phrase_extractor import extract_phrases_tfidf
    
    rows = get_unprocessed_signals(limit=500)
    if not rows:
        print("  İşlenecek yeni sinyal yok.")
        return
        
    titles = [row[2] for row in rows]
    extracted = extract_phrases_tfidf(titles)
    
    saved = 0
    signal_ids = []
    for row in rows:
        sig_id, source, raw_title, url, engagement, captured_at = row
        phrase = extracted.get(raw_title, raw_title)
        upsert_trend(normalized_phrase=phrase, platform=source, engagement=engagement)
        signal_ids.append(sig_id)
        saved += 1
        
    mark_signals_processed(signal_ids)
    print(f"  Toplam: {saved} sinyal tişört trendlerine (phrase) çıkarıldi.")


def run_analyze():
    header("ADIM 3/4 — Gemini Analizi")
    from analyzer.gemini_scoring import analyze_batch
    # Gürültü filtresi: en az 3 kez görülmüş phrase'leri gönder
    n = analyze_batch(verbose=True, min_mentions=3)
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
    # En az 20 kez görülmüş ama henüz kapsamlı doğrulanmamış veya her gün bir kez kontrol edilen adaylar
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


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

def run_schedule():
    header("Zamanlayıcı Başlatılıyor")
    from apscheduler.schedulers.blocking import BlockingScheduler
    
    scheduler = BlockingScheduler()
    
    def job_full_cycle():
        logging.info("--- Tam Döngü Başlıyor (Toplama + Çıkarma + Analiz + Üretim) ---")
        try:
            run_collect()
            run_extract()
            run_analyze()
            run_generate()
            logging.info("Tam döngü başarıyla tamamlandı.")
        except Exception as e:
            logging.error(f"Tam döngü sırasında kritik hata: {e}")

    def job_momentum_check():
        logging.info("--- Günlük Momentum Doğrulama Job'ı Başlıyor ---")
        try:
            run_momentum()
            logging.info("Momentum doğrulaması tamamlandı.")
        except Exception as e:
            logging.error(f"Momentum doğrulaması sırasında hata: {e}")
        
    # Her 2 saatte bir -> collect + extract + analyze + generate
    scheduler.add_job(job_full_cycle, 'interval', hours=2)
    
    # Her gün sabaha karşı 04:00 -> Momentum Doğrulama
    scheduler.add_job(job_momentum_check, 'cron', hour=4, minute=0)
    
    logging.info("Zamanlayıcı MODÜLER ve DAYANIKLI modda.")
    logging.info("- Her 2 saatte bir: Full Pipeline (ADIM 1-4)")
    logging.info("- Her gün 04:00   : Momentum Engine Viral Doğrulama")
    logging.info("Çıkmak için CTRL+C yapabilirsiniz.\n")

    # Başlangıçta hemen bir kez çalıştır (Railway/Docker deploy anında başlasın)
    job_full_cycle()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Zamanlayıcı durduruldu.")


def main():
    from db.database import init_db
    init_db()
    parser = argparse.ArgumentParser(description="POD Trend Engine Pipeline")
    parser.add_argument("--collect",  action="store_true", help="Sadece veri toplama")
    parser.add_argument("--extract",  action="store_true", help="Sadece çıkarım")
    parser.add_argument("--analyze",  action="store_true", help="Sadece analiz")
    parser.add_argument("--generate", action="store_true", help="Sadece output üretimi")
    parser.add_argument("--schedule", action="store_true", help="Zamanlayıcıyı başlatır")
    args = parser.parse_args()

    start = datetime.now()
    print(f"\n🚀 POD Trend Engine V2 — {start.strftime('%Y-%m-%d %H:%M')}")

    if args.schedule:
        run_schedule()
        return

    # Hiç bayrak yoksa full pipeline
    full = not (args.collect or args.extract or args.analyze or args.generate)

    if full or args.collect:
        run_collect()
    if full or args.extract:
        run_extract()
    if full or args.analyze:
        run_analyze()
    if full or args.generate:
        run_generate()

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Tamamlandı — {elapsed}s")


if __name__ == "__main__":
    main()
