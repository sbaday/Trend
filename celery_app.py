"""
Celery Uygulaması
-----------------
Redis broker üzerinde görev kuyruğu yapılandırması.

Başlatma:
    celery -A celery_app worker --loglevel=info --concurrency=2
"""

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Öncelik: REDIS_URL (Railway/Docker env) > config.yaml > default
_env_redis = os.getenv('REDIS_URL')

try:
    from config.loader import config as _cfg
    _cel = _cfg.get('celery', {})
    broker_url  = _env_redis or _cel.get('broker_url',  'redis://redis:6379/0')
    backend_url = _env_redis or _cel.get('backend_url', 'redis://redis:6379/1')
except Exception:
    broker_url  = _env_redis or 'redis://redis:6379/0'
    backend_url = _env_redis or 'redis://redis:6379/1'

app = Celery('trend_engine', broker=broker_url, backend=backend_url)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    # Görev başarısız olursa 60s bekle ve 3 kez tekrar dene
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
