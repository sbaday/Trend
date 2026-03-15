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
    for row in rows:
        sig_id, source, raw_title, url, engagement, captured_at = row
        phrase = extracted.get(raw_title, raw_title)
        upsert_trend(normalized_phrase=phrase, platform=source, engagement=engagement)
        saved += 1
        
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


def run_schedule():
    header("Zamanlayıcı Başlatılıyor")
    from apscheduler.schedulers.blocking import BlockingScheduler
    
    scheduler = BlockingScheduler()
    
    def log_time(msg):
        print(f"\n\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {msg}")
        
    def job_full_cycle():
        log_time("Tam Döngü Başlıyor (Toplama + Çıkarma + Analiz)...")
        run_collect()
        run_extract()
        run_analyze()
        
    # Her 2 saatte bir -> collect + extract + analyze
    scheduler.add_job(job_full_cycle, 'interval', hours=2)
    
    print("Zamanlayıcı AGRESİF modda.")
    print("- Her 2 saatte bir: Veri Toplama + Phrase Extraction + Gemini Analizi")
    print("- Gece 23:00'te ekstra analiz job'ı kaldırıldı, her döngü analiz içeriyor.")
    print("Çıkmak için CTRL+C yapabilirsiniz.\n")

    # Başlangıçta hemen bir kez çalıştır (Railway deploy anında başlasın)
    job_full_cycle()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nZamanlayıcı durduruldu.")


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
