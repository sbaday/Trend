"""
Celery Uygulaması
-----------------
Redis broker üzerinde görev kuyruğu yapılandırması.

Geliştirmeler:
- Sonuç backend'i (result backend) varsayılan olarak devre dışı (daha dayanıklı).
- Railway'de REDIS_URL yoksa otomatik senkron fallback için daha temiz loglama.
- Docker dışı (local) çalıştırmalar için localhost desteği.
"""

import os
import logging
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_redis_url():
    # 1. Öncelik: Sistem ortam değişkeni (Railway/Docker env)
    env_url = os.getenv('REDIS_URL')
    if env_url:
        return env_url

    # 2. Öncelik: config.yaml
    try:
        from config.loader import config as _cfg
        conf_url = _cfg.get('celery', {}).get('broker_url')
        if conf_url and "redis" in conf_url:
            # Eğer docker dışında isek ve 'redis' hostu varsa 'localhost'a çevir
            if "redis:6379" in conf_url and not os.path.exists("/.dockerenv"):
                return conf_url.replace("redis:6379", "localhost:6379")
            return conf_url
    except Exception:
        pass

    # 3. Öncelik: Güvenli varsayılanlar
    if os.path.exists("/.dockerenv"):
        return 'redis://redis:6379/0'
    return 'redis://localhost:6379/0'

broker_url = get_redis_url()

# URL'yi logla (şifreyi gizleyerek)
safe_url = broker_url
if "@" in broker_url:
    parts = broker_url.split("@")
    safe_url = f"redis://****@{parts[1]}"
print(f"  [Celery] Broker URL: {safe_url}")

# Uygulama başlatma
# include=['tasks'] ekleyerek worker'ın görevleri tanımasını sağlıyoruz.
app = Celery('trend_engine', broker=broker_url, include=['tasks'])

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Sonuçları saklama (Hata olasılığını azaltır)
    task_ignore_result=True,
    result_backend=None
)
