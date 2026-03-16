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
import os
from datetime import datetime
from dotenv import load_dotenv
from config.loader import config

load_dotenv()

_sched_cfg    = config.get('scheduler', {})
_analysis_cfg = config.get('analysis', {})


from core.pipeline import (
    header, 
    run_collect, 
    run_extract, 
    run_analyze, 
    run_generate, 
    run_momentum
)


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def run_schedule():
    header("Zamanlayıcı Başlatılıyor")
    from apscheduler.schedulers.blocking import BlockingScheduler
    
    scheduler = BlockingScheduler()
    
    def job_full_cycle():
        logging.info("--- Tam Döngü Başlıyor ---")
        # Celery varsa asenkron, yoksa senkron çalış (graceful fallback)
        try:
            from tasks import dispatch_full_pipeline
            task_id = dispatch_full_pipeline()
            logging.info(f"Görevler asenkron kuyruğa gönderildi. ID: {task_id}")
        except Exception as celery_err:
            logging.warning(f"Celery kullanılamıyor ({celery_err}), senkron modda çalışıyor...")
            try:
                run_collect()
                run_extract()
                run_analyze()
                run_generate()
                logging.info("Senkron döngü başarıyla tamamlandı.")
            except Exception as e:
                logging.error(f"Döngü hatası: {e}")

    def job_momentum_check():
        logging.info("--- Günlük Momentum Doğrulama Job'ı Başlıyor ---")
        try:
            from tasks import momentum_task
            momentum_task.delay()
            logging.info("Momentum görevi kuyruğa gönderildi.")
        except Exception as celery_err:
            logging.warning(f"Celery kullanılamıyor ({celery_err}), senkron çalışıyor...")
            try:
                run_momentum()
                logging.info("Momentum doğrulaması tamamlandı.")
            except Exception as e:
                logging.error(f"Momentum doğrulaması sırasında hata: {e}")
        
    # Scheduler interval'i config'den al
    _interval_hours = _sched_cfg.get('full_cycle_interval_hours', 2)
    _momentum_time  = _sched_cfg.get('momentum_engine_time', '04:00')
    _m_hour, _m_min = [int(x) for x in _momentum_time.split(':')]

    # Her N saatte bir -> collect + extract + analyze + generate
    scheduler.add_job(job_full_cycle, 'interval', hours=_interval_hours)
    
    # Her gün momentum kontrolü
    scheduler.add_job(job_momentum_check, 'cron', hour=_m_hour, minute=_m_min)
    
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
    parser.add_argument("--schedule", action="store_true", help="Zamanlayıcıyı başlatır")
    parser.add_argument("--limit",    type=int, default=40, help="Gemini batch limiti")
    parser.add_argument("--min-mentions", type=int, default=3, help="Minimum mention eşiği")
    parser.add_argument("--rush",     action="store_true", help="Backlog temizleme modu (sadece extract+analyze)")
    args = parser.parse_args()

    start = datetime.now()
    print(f"\n🚀 POD Trend Engine V2 — {start.strftime('%Y-%m-%d %H:%M')}")

    if args.schedule:
        run_schedule()
        return

    if args.rush:
        header("RUSH MODE — Backlog Temizleniyor")
        run_extract()
        # Rush mode uses a larger batch if user confirms, or just 100 for safety
        run_analyze(limit=min(args.limit * 2, 100), min_mentions=args.min_mentions)
        return

    # Hiç bayrak yoksa full pipeline
    full = not (args.collect or args.extract or args.analyze or args.generate)

    if full or args.collect:
        run_collect()
    if full or args.extract:
        run_extract()
    if full or args.analyze:
        run_analyze(limit=args.limit, min_mentions=args.min_mentions)
    if full or args.generate:
        run_generate()

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ Tamamlandı — {elapsed}s")


if __name__ == "__main__":
    main()
