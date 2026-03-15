---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - README.md
  - run_pipeline.py
  - models.py
  - db/database.py
  - analyzer/gemini_scoring.py
  - generator/generators.py
  - collectors/reddit_rss.py
  - collectors/hackernews.py
  - collectors/google_trends.py
  - collectors/pinterest_collector.py
  - collectors/etsy_scraper.py
  - extraction/phrase_extractor.py
date: 2026-03-15
author: Doguk
---

# Product Brief: POD Trend Engine V2

## 1. Ürün Vizyonu

**POD Trend Engine V2**, Print-on-Demand (POD) satıcılarının internet genelindeki trend sinyallerini otomatik olarak keşfedip, yapay zeka desteğiyle pazar potansiyelini değerlendirerek **hazır Etsy listing, tasarım promptu ve sosyal medya içeriği** üretmesini sağlayan tam otomatik bir içerik ve ürün araştırma motorudur.

### Tek Cümle Vizyon
> Reddit, HackerNews ve Google Trends'ten gelen trendleri Gemini AI ile puanlayarak Etsy satıcılarına pazara hazır içerik üretmek.

---

## 2. Problem & Fırsat

### Temel Problem
POD satıcıları için trend araştırması son derece zaman alıcıdır:
- Her platform ayrı ayrı takip edilmeli (Reddit, HN, Google Trends, Pinterest)
- Hangi trendin gerçekten POD ürünü olarak işe yarayacağı subjektif bir değerlendirme gerektirir
- Etsy listing yazımı, tasarım brief oluşturma ve sosyal medya içeriği manuel emek ister
- Haftalık trend döngüsünü yakalamak için sürekli aktif olmak gerekir

### Fırsat
- Reddit RSS ve HackerNews API **ücretsiz ve API key gerektirmez** → düşük giriş engeli
- Gemini 2.5 Flash ile 50 trend analizi ≈ **$0.01 maliyet** → ölçeklenebilir ekonomi
- Printify API entegrasyonu ile **tek tıkla ürün taslağı** oluşturulabilir
- Tam otomatik haftalık zamanlama → sıfır manuel müdahale

---

## 3. Hedef Kullanıcılar

### Birincil Kullanıcı: Solo POD Girişimcisi
- **Kim:** Etsy'de tişört, kupalar, posterler satan bireysel satıcılar
- **Hedef:** Haftalık trend araştırmasından kurtularak içerik üretimine odaklanmak
- **Ağrı Noktası:** Hangi trendin ürüne dönüşeceğini bulmak için saatler harcıyor
- **Teknik Seviye:** Orta (Python çalıştırabilir, .env dosyası düzenleyebilir)

### İkincil Kullanıcı: Küçük POD Ajansı/Ekibi
- **Kim:** Birden fazla Etsy mağazası yöneten 2-5 kişilik ekipler
- **Hedef:** Aynı anda birden fazla niş için trend takibi yapmak
- **Ağrı Noktası:** Manuel süreç ölçeklenmiyor

---

## 4. Temel Özellikler (Mevcut V2 Durumu)

### 🔍 Veri Toplama Katmanı
| Kaynak | Yöntem | Durum |
|--------|--------|-------|
| Reddit | RSS Feed (rising + hot + top) | ✅ Aktif |
| HackerNews | Firebase API | ✅ Aktif |
| Google Trends | pytrends (related queries) | ✅ Aktif |
| Pinterest | Scraper | ⚠️ Pasif (403 hatası) |
| Etsy | Scraper | ⚠️ Keşif aşaması |

### 🧠 Analiz Katmanı
- **TF-IDF Phrase Extraction:** Ham başlıklardan anlamlı n-gram phrase'ler çıkarır
- **Gemini AI Skorlama:** Her phrase için 4 boyutlu puanlama:
  - Humor (eğlence/mizah potansiyeli) × 0.35
  - Identity (kimlik ifadesi, niş uyumu) × 0.25
  - Giftability (hediye ürünü uygunluğu) × 0.25
  - Design Simplicity (basit tasarım uygulanabilirliği) × 0.15
- **Threshold:** 7.0+ skor → Otomatik output üretimi

### 📦 Output Katmanı (Score ≥ 7.0)
1. **Tasarım Promptu** → Midjourney/Kittl için hazır görsel açıklama
2. **Etsy Listing** → Başlık + Açıklama + 13 Tag (JSON formatında)
3. **Sosyal İçerik** → TikTok hook, Pinterest başlık, Instagram caption
4. **Printify Draft** → Opsiyonel, otomatik ürün taslağı (API key gerekli)

### 🗄 Veri Mimarisi (SQLite V2)
- `signals` → Ham sinyaller (kaynak, raw_title, engagement, captured_at)
- `trends` → Normalize phrase'ler + AI skorları + 4 boyutlu puanlar
- `trend_signals` → Zaman serisi (günlük momentum hesabı)
- `trend_clusters` → Semantik kümeleme (embedding hazır)
- `trend_embeddings` → Vektör tablosu (384 dim, gelecek özellik)
- `outputs` → Üretilen içerikler (JSON string)

### ⏰ Otomasyon
- **Pazartesi, Salı, Perşembe:** Veri toplama + Phrase Extraction
- **Cuma:** Gemini Skorlama + Output Üretimi

---

## 5. Teknik Mimari

```
Input Layer:          Reddit RSS | HackerNews API | Google Trends | Pinterest (pasif)
          ↓
Storage:              SQLite V2 → signals tablosu
          ↓
Extraction:           TF-IDF n-gram → trends tablosu
          ↓
AI Analysis:          Gemini 2.5 Flash → 4D scoring → trends güncelleme
          ↓
Output Gen:           Gemini 2.5 Flash → outputs tablosu (design/listing/social/printify)
          ↓
UI:                   Streamlit Dashboard (ui/streamlit_app.py)
```

**Ana Teknoloji Stack:**
- Python 3.x
- google-genai (Gemini API)
- pytrends (Google Trends)
- SQLite (yerel veritabanı)
- Pydantic (veri modelleri)
- APScheduler (haftalık otomasyon)
- Streamlit (dashboard)

---

## 6. Başarı Metrikleri

| Metrik | Beklenti |
|--------|----------|
| Haftalık toplanan sinyal sayısı | > 200 |
| Phrase extraction hassasiyeti | Anlamlı phrase oranı > %60 |
| AI skorlama maliyeti (haftalık) | < $0.10 |
| 7.0+ skor alan trend oranı | %10-20 |
| Pipeline çalışma süresi (tam) | < 5 dakika |
| Etsy listing kalitesi | Kullanılabilir, revision minimum |

---

## 7. Kapsam Dışı (V2)

- ❌ Gerçek zamanlı trend izleme (real-time streaming)
- ❌ Çok kullanıcılı/SaaS mimarisi
- ❌ Etsy API entegrasyonu (otomatik listing yükleme)
- ❌ Gelişmiş semantik kümeleme (embedding katmanı hazır ama aktif değil)
- ❌ A/B test ve satış performansı takibi

---

## 8. Riskler & Varsayımlar

### Riskler
| Risk | Etki | Azaltma |
|------|------|---------|
| Reddit RSS yapısı değişirse | Yüksek | RSS→API geçişi planı |
| Gemini API maliyet artışı | Orta | Token optimizasyonu, batch boyutu ayarı |
| Google Trends rate limiting | Orta | Jitter (1.5-3s) mevcut |
| Trend-Ürün uyumsuzluğu | Düşük | Çok boyutlu skor sistemi |

### Varsayımlar
- Kullanıcı `GEMINI_API_KEY` temin eder
- SQLite yeterli → PostgreSQL geçiş gerekmez (tek kullanıcı)
- Haftalık ritim POD satıcıları için yeterli
