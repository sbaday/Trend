---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments: 
  - 'c:\Users\doguk\OneDrive\Belgeler\test Trend\_bmad-output\planning-artifacts\prd-test-Trend-v2-2026-03-15.md'
---

# POD Trend Engine V2 - Epik Kırılımı

## Genel Bakış

Bu doküman, POD Trend Engine V2 projesi için üretilmiş epik ve kullanıcı hikayeleri (story) kırılımını içerir. Gereksinimler PRD üzerinden alınmış ve uygulamanın geliştirme adımlarını yönetecek Sprint Backlog'una dönüştürülmüştür.

## Gereksinim Envanteri

### Fonksiyonel Gereksinimler (FR)

FR1 (US-001): Reddit RSS Sinyal Toplayıcı (rising/hot/top)
FR2 (US-002): HackerNews Topstories Toplayıcı
FR3 (US-003): Google Trends İlgili Sorgu Keşfi
FR4 (US-004): TF-IDF Phrase Çıkarımı
FR5 (US-005): Gemini 4D Skorlama Motoru (humor, identity, giftability, design)
FR6 (US-006): Otomatik Etsy Listing Üretimi
FR7 (US-007): Görsel Tasarım Prompt Motoru (Midjourney/Kittl)
FR8 (US-008): Çok Platformlu Sosyal İçerik Üretimi (TikTok, Pinterest, IG)
FR9 (US-009): Printify Draft Entegrasyonu (Opsiyonel)
FR10 (US-010): Haftalık APScheduler Otomasyonu (Pipeline Orkestrasyonu)
FR11 (US-011): Streamlit Analitik Dashboard

\* *Ek Gereksinim: Radar Score V2 Placeholder & Semantik Tablo Hazırlığı*

### Fonksiyonel Olmayan Gereksinimler (NFR)

NFR1: Tam pipeline çalışma süresi < 5 dakika
NFR2: Gemini yanıt süresi < 3 saniye / trend
NFR3: SQLite sorgu süresi < 100ms
NFR4: Google Trends API jitter (1.5-3s)
NFR5: Hata durumunda bağımsız kolektör yönetimi ve graceful skip

### Ek Gereksinimler (Mimari & Teknik)

- SQLite V2 Şeması (trends, signals, trend_signals, outputs veritabanı yapısı)
- API anahtarlarının .env dosyasında güvenli tutulması
- Printify API tokenı yoksa dahi sistemin çalışmaya devam etmesi (graceful skip)

### UX Tasarım Gereksinimleri

- Streamlit arayüzünde hızlı (2 saniye altı) veri tablosu yükleme.

### FR Kapsam Haritası (Coverage Map)

FR1: Epik 1 - Stratejik Sinyal Toplama
FR2: Epik 1 - Stratejik Sinyal Toplama
FR3: Epik 1 - Stratejik Sinyal Toplama
FR4: Epik 2 - Pattern Tanıma & Semantik Keşif
FR5: Epik 3 - AI Kar Edilebilirlik Analizi
FR6: Epik 4 - Pazara Hazır Listing & Kreatif Üretim
FR7: Epik 4 - Pazara Hazır Listing & Kreatif Üretim
FR8: Epik 4 - Pazara Hazır Listing & Kreatif Üretim
FR9: Epik 6 - Dış Platform Entegrasyonu (Opsiyonel)
FR10: Epik 5 - Operasyonel Performans & Görünürlük
FR11: Epik 5 - Operasyonel Performans & Görünürlük
*Radar/Momentum*: Epik 2 ve Epik 7

## Epik Listesi

### Epik 1: Stratejik Sinyal Toplama
Temel platformlardan trend sinyallerinin otomatik toplanması.
**Kapsanan FR'ler:** FR1, FR2, FR3

### Epik 2: Pattern Tanıma & Semantik Keşif
Ham sinyalleri anlamlı trend phrase’lerine dönüştür ve radar skor için altyapı hazırla.
**Kapsanan FR'ler:** FR4, (Radar/Embedding DB hazırlığı)

### Epik 3: AI Kar Edilebilirlik Analizi
Trendleri Gemini AI ile POD potansiyeli için puanla.
**Kapsanan FR'ler:** FR5

### Epik 4: Pazara Hazır Listing & Kreatif Üretim
Etsy listing, tasarım promptu ve sosyal medya içeriği üret.
**Kapsanan FR'ler:** FR6, FR7, FR8

### Epik 5: Operasyonel Performans & Görünürlük
Pipeline’ın sorunsuz çalışmasını sağla ve dashboard ile görünürlük sun.
**Kapsanan FR'ler:** FR10, FR11

### Epik 6: Dış Platform Entegrasyonu (Opsiyonel)
Opsiyonel olarak Printify draft oluşturma.
**Kapsanan FR'ler:** FR9

### Epik 7: Trend Zekası Katmanı (Momentum & Saturasyon)
Momentum skoru, trendin düşüş ve doygunluk ölçümleri için altyapı oluştur (V2 minimal, V3 tam).
**Kapsanan FR'ler:** (Momentum/Saturasyon altyapısı)

## Epik 1: Stratejik Sinyal Toplama

Temel platformlardan trend sinyallerinin otomatik toplanması.

### Story 1.1: Reddit RSS Sinyal Toplayıcı (rising/hot/top)

As a POD satıcısı,
I want Reddit'ten yükselen ve popüler içeriklerin başlıklarını otomatik toplamayı,
So that elle takip etmek zorunda kalmadan viral trend adaylarını yakalayabilirim.

**Acceptance Criteria:**

**Given** çalışan bir internet bağlantısı ve Python ortamı
**When** `python run_pipeline.py --collect` çalıştırıldığında (veya zamanlanmış görev tetiklendiğinde)
**Then** sistem Reddit RSS feed'lerinden (rising, hot, top) okuma yapmalı
**And** her sinyal `signals` tablosuna source, subsource, raw_title ile birlikte kaydedilmelidir.

### Story 1.2: HackerNews En Popüler Gönderiler Toplayıcı

As a POD satıcısı,
I want HackerNews'teki yüksek puanlı gönderilerin başlıklarını toplamayı,
So that tech nişindeki trend sinyallerini veri setime dahil edebileyim.

**Acceptance Criteria:**

**Given** HackerNews Firebase API'sine erişim
**When** toplama süreci çalıştığında
**Then** topstories endpoint'inden veriler çekilmeli
**And** engagement (puan) bilgisiyle birlikte `signals` tablosuna (source='hackernews') aktarılmalıdır.

### Story 1.3: Google Trends İlgili Sorgu Keşfi

As a POD satıcısı,
I want Google Trends'te yükselen sorguları otomatik keşfetmeyi,
So that arama motoru bazlı trend sinyallerini yakalayabileyim.

**Acceptance Criteria:**

**Given** `pytrends` kütüphanesi aktif
**When** toplama süreci çalıştığında
**Then** sistem 1.5-3 saniye jitter uygulayarak (rate-limit önlemi) sorguları çekmeli
**And** yeni keşfedilen sinyaller `signals` tablosuna kaydedilmelidir.

## Epik 2: Pattern Tanıma & Semantik Keşif

Ham sinyalleri anlamlı trend phrase’lerine dönüştür ve radar skor için altyapı hazırla.

### Story 2.1: TF-IDF Phrase Çıkarımı

As a POD satıcısı,
I want "I survived 2025 and all I got was this lousy t-shirt" gibi ham başlıklardan "survived 2025" gibi anlamlı phrase'ler çıkarılmasını,
So that doğrudan tasarıma uygulanabilir konseptler elde edeyim.

**Acceptance Criteria:**

**Given** `signals` tablosunda ham başlıklar bulunduğunda
**When** extraction süreci (`--extract`) çalıştığında
**Then** sistem TF-IDF algoritması ile n-gram phrase extraction yapmalı
**And** phrase'ler `trends` tablosuna upsert edilmeli (aynı phrase varsa `total_mentions` artar).

### Story 2.2: Radar Skor Placeholder

As a Sistem Mimarı,
I want `trends` tablosunda `radar_score` alanı için bir placeholder değer (0.0) oluşturulmasını,
So that gelecekte momentum ve novelty bazlı trend zekası eklendiğinde şemanın hazır olmasını sağlayabileyim.

**Acceptance Criteria:**

**Given** `trends` tablosu şeması kurulduğunda
**When** yeni bir phrase eklendiğinde
**Then** `radar_score` varsayılan olarak 0.0 değeri almalıdır.

### Story 2.3: Semantik Embedding Tablosu Hazırlığı

As a Sistem Mimarı,
I want `trend_embeddings` tablosunun semantik veri için hazırlanmasını,
So that V3'te semantik kümeleme yapıldığında altyapı hazır olsun.

**Acceptance Criteria:**

**Given** SQLite veritabanı kurulumu
**When** şema oluşturulduğunda
**Then** 384-boyutlu vektörleri destekleyen `trend_embeddings` tablosu oluşturulmalıdır.

## Epik 3: AI Kar Edilebilirlik Analizi

Trendleri Gemini AI ile POD potansiyeli için puanla.

### Story 3.1: Gemini 4D Skorlama Motoru

As a POD satıcısı,
I want her trend phrase'in POD ürünü olarak potansiyelini (mizah, kimlik, hediye edilebilirliği, tasarım) Gemini ile puanlamayı,
So that hangi trendlere yatırım yapacağıma veri odaklı karar verebileyim.

**Acceptance Criteria:**

**Given** `trends` tablosunda henüz analiz edilmemiş (analyzed=0) minimum 3 mention'a sahip phrase'ler
**When** analiz süreci (`--analyze`) çalıştığında
**Then** Gemini 2.5 Flash ile API bağlatısı kurularak puanlama istenmeli
**And** 4 boyuttan hesaplanan final_score tablodaki `ai_score` alanına yazılmalı ve `analyzed=1` olarak işaretlenmelidir.

## Epik 4: Pazara Hazır Listing & Kreatif Üretim

Etsy listing, tasarım promptu ve sosyal medya içeriği üret.

### Story 4.1: Otomatik Etsy Listing Üretimi

As a Etsy satıcısı,
I want yüksek potansiyelli (ai_score ≥ 7.0) trendler için optimize edilmiş başlık, açıklama ve taglar üretilmesini,
So that manuel listing yazmaya zaman harcamadan içerik elde edeyim.

**Acceptance Criteria:**

**Given** `ai_score` >= 7.0 olan trendler
**When** üretim süreci (`--generate`) çalıştığında
**Then** Gemini ile uygun başlık (≤140 karakter), açıklama ve 13 tag içeren JSON oluşturulmalı
**And** bu veri `outputs` tablosuna `output_type="etsy_listing"` olarak kaydedilmelidir.

### Story 4.2: Görsel Tasarım Prompt Motoru

As a POD tasarımcısı,
I want her yüksek potansiyelli trend için Midjourney veya Kittl formatına uygun görsel promptlar üretilmesini,
So that tasarım aşamasına hızlıca geçebileyim.

**Acceptance Criteria:**

**Given** `ai_score` >= 7.0 olan trendler
**When** üretim süreci çalıştığında
**Then** Gemini ile tasarıma uygun renk, stil ve kompozisyon içeren promptlar oluşturulmalı
**And** veri `outputs` tablosuna `output_type="design_prompt"` olarak kaydedilmelidir.

### Story 4.3: Çok Platformlu Sosyal İçerik Üretimi

As a POD satıcısı,
I want satışlarımı desteklemek için trend bazlı TikTok hook, Pinterest başlığı ve Instagram caption üretilmesini,
So that sosyal medya promosyonlarını otomatikleştirebileyim.

**Acceptance Criteria:**

**Given** `ai_score` >= 7.0 olan trendler
**When** üretim süreci çalıştığında
**Then** hedef platformlara özgü içerikler oluşturulmalı
**And** veri `outputs` tablosuna `output_type="social_content"` olarak JSON formatında kaydedilmelidir.

## Epik 5: Operasyonel Performans & Görünürlük

Pipeline’ın sorunsuz çalışmasını sağla ve dashboard ile görünürlük sun.

### Story 5.1: Pipeline Orkestrasyonu & Zamanlama

As a Yoğun POD Satıcısı,
I want sistemin bir cron zamanlayıcısıyla otomatik çalışmasını,
So that tüm trend takip döngüsünün müdahalesiz ilerlemesini sağlayabileyim.

**Acceptance Criteria:**

**Given** APScheduler kütüphanesi yapılandırıldığında
**When** `python run_pipeline.py --schedule` komutu çalıştırıldığında
**Then** belirtilen gün ve saatlerde ilgili pipeline aşamaları tetiklenmeli
**And** sorun çıkması halinde hatalar yakalanmalı ve loglanmalıdır.

### Story 5.2: Streamlit Analitik Dashboard

As a POD satıcısı,
I want toplanan trendleri, AI skorlarını ve üretilen içerikleri tek bir görsel arayüzden yönetebilmeyi,
So that kolay filtreleme ile en değerli trendleri hızlıca tespit edebileyim.

**Acceptance Criteria:**

**Given** veritabanında işlenmiş sinyaller ve outputlar
**When** `streamlit run ui/streamlit_app.py` çalıştırıldığında
**Then** 2 saniye altı bir sürede veriler tabloya yüklenmeli
**And** skor eşiği, kaynak ve tarihe göre filtreleme yapılabilmelidir.

### Story 5.3: Monitoring & Çalışma Geçmişi

As a Sistem Yöneticisi,
I want pipeline çalışmalarının başarı/hata durumunu ve metrikleri bir dashboard/log üzerinde görebilmeyi,
So that sorunlara hızlı müdahale edebileyim.

**Acceptance Criteria:**

**Given** aktif bir logging mekanizması
**When** pipeline çalışmasını tamamladığında
**Then** toplanan sinyal sayısı, geçen süre ve olası hatalar log dosyasına yazılmalı
**And** istatistikler Streamlit üzerinde "Logs" gibi bir sekmede izlenebilmelidir.

## Epik 6: Dış Platform Entegrasyonu (Opsiyonel)

Opsiyonel olarak Printify draft oluşturma.

### Story 6.1: Printify Draft Entegrasyonu (Opsiyonel)

As a POD satıcısı,
I want üretilen listing bilgilerinin Printify hesabımdaki ürün draftlarına doğrudan gönderilmesini,
So that tek tıkla yükleme aşamasına geçebileyim.

**Acceptance Criteria:**

**Given** geçerli bir PRINTIFY_API_TOKEN ve PRINTIFY_SHOP_ID tanımlandığında
**When** üretim sonrasında publish tetiklendiğinde
**Then** Printify API kullanılarak ilgili başlık ve etiketlerle taslak ürün oluşturulmalı
**And** token eksikse bu süreç hata vermeden atlanmalıdır (graceful skip).

## Epik 7: Trend Zekası Katmanı (Momentum & Saturasyon)

Momentum skoru, trendin düşüş ve doygunluk ölçümleri için altyapı oluştur (V2 minimal, V3 tam).

### Story 7.1: Radar Skor Hesaplama Mantığı (V2 minimal)

As a Veri Analisti,
I want `trend_signals` zaman serisi verisini okuyan ve `radar_score` güncelleyen temel bir algoritma oluşturulmasını,
So that trendin hızını ve momentumunu zaman içinde izleyebileyim.

**Acceptance Criteria:**

**Given** `trend_signals` günlük mention verisi
**When** skorlama fonksiyonu çalıştığında
**Then** geçmiş güne göre ivme artışı hesaplanarak `radar_score` güncellenmelidir.

### Story 7.2: Momentum & Saturasyon Placeholder Altyapısı

As a Ürün Yöneticisi,
I want saturasyon ve düşüş metriklerinin V3 öncesinde konsept ve altyapısal planının yapılmasını,
So that gelecekte hangi pazarın doygunluğa ulaştığını tespit etme mekanizmaları için hazırlıklı olayım.

**Acceptance Criteria:**

**Given** V2 mimarisi
**When** şema ve pipeline incelendiğinde
**Then** düşüş sinyalleri (decay) ve pazardaki satıcı doyum noktası (saturation) veri gereksinimleri dokümante edilmelidir.
