"""
Config Loader
-------------
config.yaml dosyasını okur ve global `config` nesnesini oluşturur.
Hassas bilgiler (API anahtarları, DB URL) .env'den okunur ve config'e eklenir.

Kullanım:
    from config.loader import config
    threshold = config['scoring']['threshold']
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# config.yaml projenin ana dizininde olmalı
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    """config.yaml'i yükler, .env değerlerini hassas alanlara uygular."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Hassas değerleri .env'den al (YAML'daki placeholder'ları eze)
    # Bu sayede config.yaml'e asla secret yazmak gerekmez.
    if cfg.get("api_keys") is None:
        cfg["api_keys"] = {}
    cfg["api_keys"]["gemini"]   = os.getenv("GEMINI_API_KEY", "")
    cfg["api_keys"]["database"] = os.getenv("DATABASE_URL", "")
    cfg["api_keys"]["printify_token"] = os.getenv("PRINTIFY_API_TOKEN", "")
    cfg["api_keys"]["printify_shop"]  = os.getenv("PRINTIFY_SHOP_ID", "")
    
    # Celery için URL ezme (varsa)
    if os.getenv("REDIS_URL"):
        if "celery" not in cfg: cfg["celery"] = {}
        cfg["celery"]["broker_url"] = os.getenv("REDIS_URL")
        cfg["celery"]["backend_url"] = os.getenv("REDIS_URL")

    return cfg


# Tüm modüller bu nesneyi import eder
config = load_config()
