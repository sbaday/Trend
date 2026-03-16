"""
Celery Görevleri
----------------
Her pipeline adımı bağımsız bir Celery task'ı olarak tanımlanır.
run_pipeline.py içindeki mevcut fonksiyonları sarmalar — değiştirmez.

Görev dizisi (chain):
    collect_task → extract_task → analyze_task → generate_task
"""

import logging
from celery import chain
from celery_app import app

logger = logging.getLogger(__name__)


# ── ADIM 1: Veri Toplama ──────────────────────────────────────────────────────
@app.task(name='tasks.collect', bind=True, max_retries=3, default_retry_delay=60)
def collect_task(self):
    try:
        from run_pipeline import run_collect
        run_collect()
    except Exception as exc:
        logger.error(f"collect_task hata: {exc}")
        raise self.retry(exc=exc)


# ── ADIM 2: Veri Çıkarımı ────────────────────────────────────────────────────
@app.task(name='tasks.extract', bind=True, max_retries=3, default_retry_delay=30)
def extract_task(self):
    try:
        from run_pipeline import run_extract
        run_extract()
    except Exception as exc:
        logger.error(f"extract_task hata: {exc}")
        raise self.retry(exc=exc)


# ── ADIM 3: Gemini Analizi ───────────────────────────────────────────────────
@app.task(name='tasks.analyze', bind=True, max_retries=2, default_retry_delay=120)
def analyze_task(self, limit=None, min_mentions=None):
    try:
        from run_pipeline import run_analyze
        run_analyze(limit=limit, min_mentions=min_mentions)
    except Exception as exc:
        logger.error(f"analyze_task hata: {exc}")
        raise self.retry(exc=exc)


# ── ADIM 4: İçerik Üretimi ───────────────────────────────────────────────────
@app.task(name='tasks.generate', bind=True, max_retries=2, default_retry_delay=60)
def generate_task(self):
    try:
        from run_pipeline import run_generate
        run_generate()
    except Exception as exc:
        logger.error(f"generate_task hata: {exc}")
        raise self.retry(exc=exc)


# ── Momentum Kontrolü ─────────────────────────────────────────────────────────
@app.task(name='tasks.momentum', bind=True, max_retries=2)
def momentum_task(self):
    try:
        from run_pipeline import run_momentum
        run_momentum()
    except Exception as exc:
        logger.error(f"momentum_task hata: {exc}")
        raise self.retry(exc=exc)


# ── Tam Döngü Yardımcısı ─────────────────────────────────────────────────────
def dispatch_full_pipeline(limit=None, min_mentions=None):
    """
    4 görevi sırayla kuyruğa gönderir (chain).
    Önceki adım başarısız olursa sonraki çalışmaz.
    """
    pipeline = chain(
        collect_task.si(),
        extract_task.si(),
        analyze_task.si(limit=limit, min_mentions=min_mentions),
        generate_task.si()
    )
    result = pipeline.apply_async()
    logger.info(f"Pipeline kuyruğa gönderildi. Task ID: {result.id}")
    return result.id
