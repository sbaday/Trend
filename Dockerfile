# ── Build Stage ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları (psycopg2-binary için gerekli değil ama genel iyi pratik)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları önce kopyala (Docker layer cache'i için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Modüllerin doğru bulunması için PYTHONPATH ekle
ENV PYTHONPATH=/app

# Güvenlik: root olmayan kullanıcıyla çalış
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Varsayılan komut: zamanlayıcıyı başlat
CMD ["python", "run_pipeline.py", "--schedule"]
