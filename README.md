# 🔥 POD Trend Engine V2

**Reddit + HackerNews + Google Trends → Gemini AI → Etsy Listing Otomatik Üretimi**

Trend sinyallerini toplar, TF-IDF ile anlamlı phrase'lere çevirir, Gemini ile skorlar ve doğrudan kullanılabilir Etsy listing + tasarım promptu üretir.

---

## ⚡ Hızlı Başlangıç

### 1. Kurulum

```bash
pip install -r requirements.txt
```

### 2. API Anahtarı

```bash
cp .env.example .env
```

`.env` dosyasını aç ve sadece bu satırı doldur:

```ini
GEMINI_API_KEY=AIza...   # https://aistudio.google.com/apikey
```

> Printify draft'ı otomatik oluşturmak istersen `PRINTIFY_API_TOKEN` ve `PRINTIFY_SHOP_ID` da doldur. Zorunlu değil.

### 3. Çalıştır

```bash
# Tek seferde tüm pipeline
python run_pipeline.py

# Veya adım adım
python run_pipeline.py --collect   # Veri topla (Reddit + HN + Google Trends)
python run_pipeline.py --extract   # Ham veriyi phrase'lere çevir (TF-IDF)
python run_pipeline.py --analyze   # Gemini ile skora
python run_pipeline.py --generate  # Etsy listing + tasarım promptu üret

# Otomatik haftalık zamanlayıcı
python run_pipeline.py --schedule
```

### 4. Dashboard

```bash
streamlit run ui/streamlit_app.py
```

---

## 📁 Proje Yapısı

```
Trend/
├── collectors/
│   ├── reddit_rss.py          # Reddit RSS (rising + hot + top, API key gerektirmez)
│   ├── hackernews.py          # HackerNews Firebase API
│   ├── google_trends.py       # pytrends — related queries keşfi
│   └── pinterest_collector.py # Pinterest (şimdilik pasif, 403 sorunu)
├── extraction/
│   └── phrase_extractor.py    # TF-IDF ile n-gram phrase çıkarımı
├── analyzer/
│   └── gemini_scoring.py      # Gemini ile POD potansiyeli puanlama
├── generator/
│   ├── generators.py          # Etsy listing + tasarım promptu + sosyal içerik
│   └── printify_api.py        # Printify draft oluşturucu (opsiyonel)
├── db/
│   └── database.py            # SQLite V2 şeması ve CRUD
├── prompts/                   # Dışsal AI prompt şablonları (.md)
├── ui/
│   └── streamlit_app.py       # Dashboard
├── models.py                  # Pydantic veri modelleri
├── run_pipeline.py            # Ana orkestratör
└── data/trends_v2.db          # SQLite (otomatik oluşur)
```

---

## 🗓 Haftalık Otomatik Zamanlama (`--schedule`)

| Gün | İş |
|---|---|
| Pazartesi, Salı, Perşembe | Veri toplama + phrase extraction |
| Cuma | Gemini scoring + listing üretimi |

---

## 📊 Skor Sistemi (Gemini)

```
ai_score = humor×0.35 + identity×0.25 + giftability×0.25 + design×0.15
```

| Skor | Karar |
|---|---|
| 8.0+ | 🔥 Hemen üret |
| 7.0–7.9 | 🟡 Üret, test et |
| < 7.0 | ⏭️ Atla |

---

## 🗄 Veritabanı Şeması (V2)

```
signals       → Ham sinyaller (Reddit, HN, Google Trends)
trends        → Normalize phrase'ler + AI skorları
trend_signals → Zaman serisi (momentum hesabı için)
outputs       → Etsy listing, tasarım promptu, sosyal içerik (JSON)
```

---

## 📝 Notlar

- Reddit: API key **gerekmez**, RSS feed kullanır. `rising + hot + top` üç endpoint çalışır.
- HackerNews: API key **gerekmez**, açık Firebase API kullanır.
- Google Trends: Rate limit için jitter ekli (1.5–3s bekleme).
- Gemini: `gemini-2.0-flash-exp` modeli kullanılır. 50 trend analizi ≈ $0.01 maliyet.
