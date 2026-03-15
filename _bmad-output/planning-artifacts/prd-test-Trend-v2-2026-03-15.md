---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-test-Trend-2026-03-15.md
  - README.md
  - run_pipeline.py
  - models.py
  - db/database.py
  - analyzer/gemini_scoring.py
  - generator/generators.py
  - collectors/reddit_rss.py
  - collectors/hackernews.py
  - collectors/google_trends.py
date: 2026-03-15
version: "1.0"
author: Doguk
status: taslak
---

# Ürün Gereksinimleri Dokümanı (PRD)
## POD Trend Engine V2

**Proje:** test Trend  
**Versiyon:** 2.0  
**Tarih:** 15 Mart 2026  
**Yazar:** Doguk  
**Durum:** Taslak

---

## Yönetici Özeti

POD Trend Engine V2, Print-on-Demand satıcıları için tasarlanmış **tam otomatik bir trend keşif ve içerik üretim motorudur**. Reddit RSS, HackerNews, Google Trends ve Pinterest gibi platformlardan trend sinyalleri toplar; TF-IDF ile anlamlı phrase'lere dönüştürür; Gemini 2.5 Flash ile Print-on-Demand potansiyelini puanlar ve yüksek potansiyelli trendler için otomatik Etsy listing, tasarım promptu ve sosyal medya içeriği üretir.

### Temel Değer Önermesi (V2 Odak: Kalite > Nicelik)
- **Hafifletilmiş Sinyal Filtresi:** Çok sayıda gürültülü sinyal yerine, Gemini'ın derinlikli skorlama yeteneği (humor, identity, vb.) ile yüksek kaliteli "niş" trendler önceliklendirilir.
- **Zaman Tasarrufu:** Haftalık trend araştırması saatlerden dakikalara iniyor.
- **Pazara Hazır Çıktı:** Tek pipeline ile Etsy listing + tasarım + sosyal içerik.

---

## 1. Ürün Genel Bakışı

### 1.1 Problem Tanımı

Manual niche and trend research for Print-on-Demand sellers can take 10–15 hours per week and often fails to detect early-stage viral trends. Sellers need an automated way to discover, evaluate, and generate content for high-potential trends before the market saturates.

### 1.2 Ürün Açıklaması

Sistem dört ana aşamadan oluşan bir otomatik boru hattıdır:

```
Toplama → Çıkarım → Puanlama → Üretim
(Collect)  (Extract)  (Analyze)  (Generate)
```

Her aşama bağımsız çalışabilir (`--collect`, `--extract`, `--analyze`, `--generate` bayrakları) veya tam pipeline olarak ardışık işlenir. APScheduler ile haftalık zamanlama otomasyonu mevcuttur.

### 1.2 Mimari Diyagramı

```
┌─────────────────────────────────────────────────┐
│               KOLLEKTÖR KATMANI                  │
│  Reddit RSS | HackerNews | Google Trends | Pin  │
└──────────────────────┬──────────────────────────┘
                       │ signals tablosu
┌──────────────────────▼──────────────────────────┐
│              ÇIKARım KATMANI                     │
│         TF-IDF n-gram Phrase Extraction          │
└──────────────────────┬──────────────────────────┘
                       │ trends tablosu
┌──────────────────────▼──────────────────────────┐
│              ANALİZ KATMANI                      │
│    Gemini 2.5 Flash → 4D POD Skorlama           │
│    (humor + identity + giftability + design)     │
└──────────────────────┬──────────────────────────┘
                       │ ai_score ≥ 7.0
┌──────────────────────▼──────────────────────────┐
│              ÜRETİM KATMANI                      │
│  Design Prompt | Etsy Listing | Social Content  │
│         Printify Draft (opsiyonel)               │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│         STREAMLIT DASHBOARD (UI)                 │
└─────────────────────────────────────────────────┘
```

---

## 2. Kullanıcı Hikayeleri & Kabul Kriterleri

### 2.1 Veri Toplama

**US-001: Reddit Trend Toplama**
```
Bir POD satıcısı olarak,
Reddit'ten yükselen ve popüler içeriklerin başlıklarını otomatik toplamak istiyorum,
Böylece elle takip etmek zorunda kalmadan viral trend adaylarını yakalayabilirim.
```

**Kabul Kriterleri:**
- [ ] Reddit RSS feed'lerinden rising + hot + top endpoint'leri okunur
- [ ] Her sinyal: `source`, `subsource`, `raw_title`, `url`, `engagement`, `captured_at` alanlarıyla `signals` tablosuna kaydedilir
- [ ] API key gerektirmez (RSS tabanlı)
- [ ] Çalıştırma: `python run_pipeline.py --collect`

---

**US-002: HackerNews Trend Toplama**
```
Bir POD satıcısı olarak,
HackerNews'teki yüksek puanlı gönderilerin başlıklarını toplamak istiyorum,
Böylece tech nişindeki trend sinyallerini yakalayabilirim.
```

**Kabul Kriterleri:**
- [ ] Firebase API üzerinden topstories endpoint'i okunur
- [ ] Engagement (puan) bilgisi `signals` tablosuna kaydedilir
- [ ] API key gerektirmez (açık Firebase API)
- [ ] Hata durumunda graceful handling ve log

---

**US-003: Google Trends Keşfi**
```
Bir POD satıcısı olarak,
Google Trends'te yükselen sorgu ve ilgili konuları otomatik keşfetmek istiyorum,
Böylece arama bazlı trend sinyallerini yakalayabilirim.
```

**Kabul Kriterleri:**
- [ ] `pytrends` kütüphanesi ile related queries çekilir
- [ ] Rate limit için 1.5-3 saniye jitter uygulanır
- [ ] Yeni keşfedilen sinyaller `signals` tablosuna kaydedilir
- [ ] API key gerektirmez

---

### 2.2 Phrase Extraction

**US-004: Ham Başlıklardan Anlamlı Phrase Çıkarımı**
```
Bir POD satıcısı olarak,
"I survived 2025 and all I got was this lousy t-shirt" gibi ham başlıklardan
"survived 2025" gibi tişört phrase'lerine dönüşüm istiyorum,
Böylece direk tasarıma uygulanabilir konseptler elde edeyim.
```

**Kabul Kriterleri:**
- [ ] TF-IDF algoritması ile n-gram phrase extraction yapılır
- [ ] Ham başlık → normalize edilmiş phrase dönüşümü gerçekleşir
- [ ] Phrase `trends` tablosuna `upsert` edilir (aynı phrase varsa `total_mentions` artar)
- [ ] Günlük zaman serisi `trend_signals` tablosuna kaydedilir
- [ ] Çalıştırma: `python run_pipeline.py --extract`

---

### 2.3 AI Skorlama

**US-005: Gemini ile POD Potansiyeli Puanlama**
```
Bir POD satıcısı olarak,
Her trend phrase'in tişört/POD ürünü olarak ne kadar işe yarayacağını
otomatik olarak puanlamak istiyorum,
Böylece hangi trendlere yatırım yapacağıma veri odaklı karar verebileyim.
```

**Kabul Kriterleri:**
- [ ] Gemini 2.5 Flash modeli kullanılır
- [ ] 4 boyutlu puanlama: humor (×0.35) + identity (×0.25) + giftability (×0.25) + design (×0.15)
- [ ] Her puan 1-10 arasında integer
- [ ] `final_score = round(humor×0.35 + identity×0.25 + giftability×0.25 + design×0.15, 2)`
- [ ] Skor ve niche bilgisi `trends` tablosuna yazılır (`analyzed=1` olarak işaretlenir)
- [ ] Minimum 3 mention şartı (gürültü filtresi) varsayılan olarak uygulanır
- [ ] Threshold: 7.0+ → output pipeline'a gönderilir

**Skor Karar Matrisi:**
| Skor | Karar | Aksiyon |
|------|-------|---------|
| 8.0+ | 🔥 Hemen üret | Direkt output pipeline |
| 7.0–7.9 | 🟡 Üret, test et | Output pipeline |
| < 7.0 | ⏭️ Atla | Output üretilmez |

---

### 2.4 Output Üretimi

**US-006: Etsy Listing Üretimi**
```
Bir Etsy satıcısı olarak,
Yüksek potansiyelli trendler için optimize edilmiş başlık, açıklama ve taglar istiyorum,
Böylece listing yazmaya zaman harcamadan doğrudan Etsy'ye yükleyebileyim.
```

**Kabul Kriterleri:**
- [ ] Skor ≥ 7.0 olan ve henüz output'u olmayan trendler işlenir
- [ ] Gemini ile başlık (≤140 karakter), açıklama ve 13 tag üretilir
- [ ] Çıktı `EtsyListingOutput` Pydantic modeline uygun JSON olarak `outputs` tablosuna kaydedilir
- [ ] `output_type = "etsy_listing"`

---

**US-007: Tasarım Promptu Üretimi**
```
Bir POD tasarımcısı olarak,
Her trend için Midjourney veya Kittl'e yapıştırabileceğim hazır görsel prompt istiyorum,
Böylece tasarım briefi yazmak için zaman harcamayayım.
```

**Kabul Kriterleri:**
- [ ] Gemini ile phrase ve niche bilgisinden detaylı görsel prompt üretilir
- [ ] `output_type = "design_prompt"` olarak `outputs` tablosuna kaydedilir
- [ ] Prompt Midjourney/Kittl formatına uygun (stil, renk, kompozisyon ipuçları)

---

**US-008: Sosyal Medya İçeriği Üretimi**
```
Bir POD satıcısı olarak,
Her trend için TikTok hooku, Pinterest başlığı ve Instagram caption istiyorum,
Böylece sosyal medya içerik üretimini otomatikleştirebileyim.
```

**Kabul Kriterleri:**
- [ ] TikTok hook, Pinterest title, Instagram caption üretilir
- [ ] `SocialContentOutput` modeline uygun JSON formatında kaydedilir
- [ ] `output_type = "social_content"`
- [ ] Platform bazlı ton farklılıkları uygulanır (TikTok enerjik, Pinterest estetik, Instagram storytelling)

---

**US-009: Printify Draft Oluşturma (Opsiyonel)**
```
Bir POD satıcısı olarak,
Listing taslağını Printify'a otomatik olarak yüklemek istiyorum,
Böylece manuel yükleme işleminden kurtulayım.
```

**Kabul Kriterleri:**
- [ ] `PRINTIFY_API_TOKEN` ve `PRINTIFY_SHOP_ID` tanımlıysa aktif olur
- [ ] Listing başlık, açıklama ve tagları kullanılarak Printify'da draft oluşturulur
- [ ] Başarı/hata durumu `outputs` tablosuna kaydedilir
- [ ] API key yoksa graceful skip edilir (sistem çalışmaya devam eder)

---

### 2.5 Otomasyon & Zamanlama

**US-010: Haftalık Otomatik Pipeline Çalıştırma**
```
Bir yoğun POD satıcısı olarak,
Sistemi bir kez kurarak haftalık bazda otomatik çalışmasını istiyorum,
Böylece manuel müdahale olmadan sürekli güncel trendleri yakalayabilirim.
```

**Kabul Kriterleri:**
- [ ] APScheduler ile cron-tabanlı zamanlama
- [ ] Pazartesi, Salı, Perşembe 09:00: Collect + Extract
- [ ] Cuma 09:00: Analyze + Generate
- [ ] `python run_pipeline.py --schedule` ile başlatılır
- [ ] `CTRL+C` ile graceful shutdown

---

### 2.6 Dashboard (UI)

**US-011: Streamlit Dashboard ile Trend İnceleme**
```
Bir POD satıcısı olarak,
Toplanan trendleri, skorları ve üretilen içerikleri görsel bir arayüzde görmek istiyorum,
Böylece hangi ürünleri önceliklendireceğime kolayca karar verebileyim.
```

**Kabul Kriterleri:**
- [ ] `streamlit run ui/streamlit_app.py` ile başlatılır
- [ ] Trend listesi (skor, niche, mention sayısı) görüntülenir
- [ ] Seçilen trend için Etsy listing, tasarım promptu ve sosyal içerik görüntülenir
- [ ] Filtreleme: skor eşiği, kaynak platform, tarih aralığı
- [ ] **Performans Metriği:** Dashboard should load the main trend table within 2 seconds for datasets under 10k signals.

---

## 3. Fonksiyonel Olmayan Gereksinimler

### 3.1 Performans

| Gereksinim | Hedef |
|-----------|-------|
| Tam pipeline çalışma süresi | < 5 dakika (ortalama veri hacminde) |
| Gemini API yanıt süresi (per trend) | < 3 saniye |
| Veritabanı sorgu süresi | < 100ms (SQLite, < 10k kayıt) |
| Google Trends rate limiting | 1.5-3s jitter (429 hatası önleme) |

### 3.2 Güvenilirlik

- Her kolektör bağımsız hata yönetimine sahip olmalı (bir kolektör başarısız olursa diğerleri çalışmaya devam eder)
- Gemini API hatalarında graceful skip (trend atlanır, log yazılır)
- SQLite transaction rollback desteği (upsert işlemlerinde)

### 3.3 Güvenlik

- API anahtarları `.env` dosyasında tutulur, kod repository'sine yazılmaz
- `.env.example` şablon olarak paylaşılır, gerçek key'ler paylaşılmaz
- Printify API token'ı isteğe bağlı, yokluğunda sistem çalışmaya devam eder

### 3.4 Sürdürülebilirlik

- Her bileşen bağımsız Python modülü olarak yapılandırılmıştır
- Pydantic modelleri (`models.py`) type safety sağlar
- Prompt şablonları dışarıda (`prompts/*.md`) tutulur → kod değişikliği olmadan güncellenir
- SQLite şeması V2 olarak versiyonlanmıştır

### 3.5 Ölçeklenebilirlik (Gelecek)

- `trend_embeddings` tablosu vektör bazlı semantik arama için hazır (384 dim)
- `trend_clusters` tablosu kümeleme algoritması eklendiğinde aktive edilebilir
- SQLite → PostgreSQL migrasyonu mümkün (SQLAlchemy bağımlılığı yok, raw sqlite3)

---

## 4. Teknik Kısıtlar & Varsayımlar

### 4.1 Teknik Kısıtlar

| Kısıt | Detay |
|-------|-------|
| Google Trends rate limit | pytrends rate-limit sınırı nedeniyle 1.5-3s bekleme zorunlu |
| Pinterest 403 sorunu | Mevcut MVP kapsamı dışında bırakıldı. Stabilizasyon sonrası araştırılacak. |
| Gemini API | Zorunlu (`GEMINI_API_KEY`), sistemin çekirdeği |
| SQLite single-writer | Paralel yazma desteklenmiyor, sequential pipeline yapısı bunun için seçilmiş |

### 4.2 Varsayımlar

1. Kullanıcı Python 3.x ortamı kurabiliyor (`pip install -r requirements.txt`)
2. `GEMINI_API_KEY` temin edebiliyor (Google AI Studio ücretsiz tier mevcut)
3. Tek kullanıcı, tek makine ortamı (SQLite yeterli)
4. Haftalık batch ritmi POD iş döngüsüne uygun

---

## 5. Veri Modeli (SQLite V2 Şeması)

### 5.1 Tablolar

#### `signals` — Ham Sinyaller
```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT
source      TEXT NOT NULL   -- 'reddit_rss' | 'hackernews' | 'google_trends' | 'pinterest'
subsource   TEXT            -- e.g. 'r/funny', 'topstories'
raw_title   TEXT NOT NULL
url         TEXT
engagement  INTEGER DEFAULT 0
captured_at TEXT NOT NULL   -- ISO 8601
```

#### `trends` — Normalize Trendler + AI Skorları
```sql
id                INTEGER PRIMARY KEY AUTOINCREMENT
normalized_phrase TEXT NOT NULL UNIQUE
cluster_id        INTEGER REFERENCES trend_clusters(id)
first_seen        TEXT NOT NULL
last_seen         TEXT NOT NULL
total_mentions    INTEGER DEFAULT 0
analyzed          INTEGER DEFAULT 0   -- 0: bekliyor, 1: Gemini analiz edildi
radar_score       REAL DEFAULT 0.0    -- Future: Momentum bazlı skor (koruma altında)
ai_score          REAL DEFAULT 0.0    -- Gemini POD skoru (V2 Differentiator)
niche             TEXT DEFAULT 'general'
humor             REAL DEFAULT 0.0
identity          REAL DEFAULT 0.0
giftability       REAL DEFAULT 0.0
design            REAL DEFAULT 0.0
```

#### `trend_signals` — Günlük Zaman Serisi
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
trend_id        INTEGER REFERENCES trends(id)
platform        TEXT NOT NULL
mentions        INTEGER DEFAULT 1
engagement_sum  INTEGER DEFAULT 0
captured_at     TEXT NOT NULL   -- YYYY-MM-DD
```

#### `outputs` — Üretilen İçerikler
```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT
trend_id    INTEGER REFERENCES trends(id)
output_type TEXT NOT NULL   -- 'design_prompt' | 'etsy_listing' | 'social_content' | 'printify_draft'
content     TEXT NOT NULL   -- JSON string
created_at  TEXT NOT NULL
```

---

## 6. API & Entegrasyonlar

### 6.1 Harici API'ler

| API | Amaç | Auth | Zorunluluk |
|-----|------|------|-----------|
| Google Gemini API | Trend skorlama + İçerik üretimi | API Key (`.env`) | Zorunlu |
| Reddit RSS | Trend sinyali toplama | Yok | Önerilen |
| HackerNews Firebase API | Trend sinyali toplama | Yok | Önerilen |
| Google Trends (pytrends) | Trend sinyali toplama | Yok | Önerilen |
| Printify API | Ürün taslağı oluşturma | API Token + Shop ID | Opsiyonel |

### 6.2 Prompt Şablonları (Dışsal Konfigürasyon)

| Dosya | Amaç |
|-------|------|
| `prompts/scoring_system.md` | Gemini scoring system prompt |
| `prompts/scoring_user.md` | Scoring user prompt şablonu |
| `prompts/design_system.md` | Tasarım promptu system prompt |
| `prompts/design_user.md` | Tasarım promptu user şablonu |
| `prompts/listing_system.md` | Etsy listing system prompt |
| `prompts/listing_user.md` | Listing user şablonu |
| `prompts/social_system.md` | Sosyal içerik system prompt |
| `prompts/social_user.md` | Sosyal içerik user şablonu |

---

## 7. Gelecek Versiyonlar (V3 Yol Haritası)

### Kısa Vadeli (1-2 Sprint)
- [ ] **Pinterest Collector Onarımı:** 403 sorununu çöz (User-Agent rotasyonu veya Playwright)
- [ ] **Etsy Scraper Aktivasyonu:** `collectors/etsy_scraper.py` mevcut ama pasif
- [ ] **Dashboard Geliştirme:** Streamlit dashboard'u production-ready hale getir
- [ ] **Embedding Aktivasyonu:** `trend_embeddings` tablosunu semantik kümeleme için aktive et

### Orta Vadeli (3-4 Sprint)
- [ ] **SaaS Mimarisi:** Çok kullanıcılı destek için PostgreSQL + ayrı user tenancy
- [ ] **Etsy API Entegrasyonu:** Otomatik listing yükleme (Etsy OAuth2)
- [ ] **Performans Takibi:** Hangi trendlerin satışa dönüştüğünü görmek için feedback loop

### Uzun Vadeli
- [ ] **Gerçek Zamanlı İzleme:** Redis + stream processing ile anlık trend yakalama
- [ ] **A/B Test Altyapısı:** Farklı listing varyantlarını test etme
- [ ] **Çok Platform Desteği:** Amazon Merch, Redbubble, Teepublic entegrasyonu

---

## 7b. V2 Teknik Borç

Aşağıdaki özellikler **schema'da mevcut** ancak V2'de implement edilmemiştir. Bunlar gelecek özellik değil, mevcut eksiklerdir:

| Alan / Bileşen | Durum | Açıklama |
|---------------|-------|----------|
| `trends.radar_score` | ⚠️ Schema var, hesaplama yok | Momentum + novelty skoru; `trend_signals` zaman serisi hazır ama `radar_score` hesaplayan kod yok |
| `trends.cluster_id` | ⚠️ FK var, veri yazılmıyor | `trend_clusters` tablosu boş; kümeleme algoritması implement edilmedi |
| `trend_embeddings` | ⚠️ Tablo var, dolmuyor | 384-dim vektör tablosu oluşturuluyor ama hiçbir kod veri yazmıyor |
| `signals` processed flag | ⚠️ Flag yok | `get_unprocessed_signals` son N sinyali getiriyor; aynı sinyal tekrar işlenebilir |

> **Not:** Momentum engine konuşması öncesinde `radar_score` implementasyonu önceliklendirilmelidir.

---

## 8. Başarı Metrikleri & KPI'lar

| Metrik | Mevcut (Tahmini) | Hedef V2 |
|--------|-----------------|----------|
| Haftalık sinyal toplama | **758 sinyal** (ölçüldü) | > 200 sinyal |
| Phrase extraction kalitesi (anlamlı oran) | Ölçülmedi | > %60 |
| Gemini haftalık API maliyeti | Ölçülmedi | < $0.10 |
| 7.0+ skor alan trend oranı | Ölçülmedi | %10-20 |
| Tam pipeline çalışma süresi | Ölçülmedi | < 5 dakika |
| Manuel müdahale ihtiyacı | Yüksek | Sıfır (haftalık) |

---

## 9. Kapsam & Sınırlar

### Kapsam İÇİNDE (V2)
✅ Reddit RSS + HackerNews + Google Trends koleksiyonu  
✅ TF-IDF phrase extraction  
✅ Gemini 2.5 Flash ile 4D skorlama  
✅ Etsy listing + tasarım promptu + sosyal içerik üretimi  
✅ Printify draft oluşturma (opsiyonel)  
✅ SQLite V2 veri tabanı  
✅ Haftalık APScheduler otomasyonu  
✅ Streamlit dashboard  

### Kapsam DIŞINDA (V2)
❌ Gerçek zamanlı (real-time) trend izleme  
❌ Çok kullanıcılı / SaaS mimarisi  
❌ Etsy API ile otomatik listing yükleme  
❌ Semantik kümeleme (tablo hazır, aktif değil)  
❌ Satış performansı takibi / feedback loop  
❌ Pinterest aktif koleksiyon  
❌ A/B test altyapısı  

---

## 10. Doküman Geçmişi

| Versiyon | Tarih | Değişiklik |
|---------|-------|-----------|
| 1.0 | 2026-03-15 | İlk taslak — BMAD PM workflow ile oluşturuldu |
