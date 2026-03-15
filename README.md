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
# Tek seferde tüm pipeline (Collect -> Extract -> Analyze -> Generate)
python run_pipeline.py

# Veya adım adım
python run_pipeline.py --collect   # Veri topla (Reddit + HN + Google Trends)
python run_pipeline.py --extract   # Ham veriyi phrase'lere çevir (TF-IDF)
python run_pipeline.py --analyze   # Gemini ile skorla
python run_pipeline.py --generate  # Etsy listing + tasarım promptu üret

# Otonom Zamanlayıcı (Şu an aktif: Her 2 saatte bir full döngü)
python run_pipeline.py --schedule
```

### 4. Dashboard (Komuta Merkezi)

```bash
streamlit run ui/streamlit_app.py
```

- **Trend Feed:** Skorlanan trendleri filtrele ve incele.
- **Ürün Üretici:** Seçili trend için anında Etsy listing ve Tasarım promptu üret.
- **Haftalık Rapor:** Niş ve skor dağılımı grafiklerini incele, Etsy CSV export al.
- **Sistem İzleme:** Canlı logları (`pipeline.log`) takip et ve sunucu durumunu gör.

---

## 📁 Proje Yapısı

```
Trend/
├── ui/
│   └── streamlit_app.py       # Çok sekmeli gelişmiş Dashboard
├── db/
│   └── database.py            # PostgreSQL (Railway) entegrasyonu
├── generator/
│   └── generators.py          # AI içerik üretim motoru (Pydantic destekli)
├── tests/                     # Doğrulama testleri
├── run_pipeline.py            # Ana orkestratör & APScheduler (2h interval)
├── pipeline.log               # Tüm süreçlerin kalıcı kayıtları
└── .env                       # API anahtarları ve DB URL (Git-ignored)
```

---

## 🗓 Otonom Zamanlama (`--schedule`)

Sistem `APScheduler` kullanarak şu takvimle çalışır:

- **Her 2 Saatte Bir:** Tam veri akışı (Toplama + Çıkarma + Analiz + Üretim).
- **Her Gün 04:00:** Momentum Engine (Viral Doğrulama ve Trend Tazeleme).
- **Hata Yönetimi:** Her adım `try-except` blokları ve `logging` ile korunur.

---

## 📊 Skor Sistemi (Gemini 2.0 Flash)

```
ai_score = humor×0.35 + identity×0.25 + giftability×0.25 + design×0.15
```

| Skor | Karar | Aksiyon |
|---|---|---|
| 8.0+ | 🔥 Kritik | Hemen tasarıma ve mağazaya yükle. |
| 7.0–7.9 | 🟡 Potansiyel | Varyasyonlarla test et. |
| < 7.0 | ⏭️ Zayıf | Veritabanında sakla ama üretme. |

---

## 🗄 Veritabanı ve Loglama

- **PostgreSQL:** Railway üzerinde barındırılır, `DATABASE_URL` ile bağlanılır.
- **Logging:** `pipeline.log` dosyası tüm döngülerin başarısını ve hatalarını saklar, Dashboard üzerinden izlenebilir.

---

## 📝 Notlar

- Reddit: API key **gerekmez**, RSS feed kullanır. `rising + hot + top` üç endpoint çalışır.
- HackerNews: API key **gerekmez**, açık Firebase API kullanır.
- Google Trends: Rate limit için jitter ekli (1.5–3s bekleme).
- Gemini: `gemini-2.0-flash-exp` modeli kullanılır. 50 trend analizi ≈ $0.01 maliyet.
