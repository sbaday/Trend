# Story 3.1: Gemini Analiz Modülü (Sınıflandırma ve Skorlama)

Status: done

## Story

As a POD satıcısı,
I want her bir trend phrase'inin Gemini AI tarafından analiz edilip kârlılık potansiyeline göre puanlanmasını,
so that binlerce trend arasından en çok para kazandıracak olanlara odaklanabileyim.

## Acceptance Criteria

1. **Given** `trends` tablosunda henüz analiz edilmemiş (`analyzed=0`) ve belirli bir mention eşiğini geçmiş trendler bulunduğunda.
2. **When** analiz süreci (`python run_pipeline.py --analyze`) çalıştığında.
3. **Then** sistem Gemini API (Google Generative AI) kullanarak her phrase için şu metrikleri üretmelidir:
    - **humor** (0.0 - 10.0)
    - **identity** (0.0 - 10.0)
    - **giftability** (0.0 - 10.0)
    - **design** (0.0 - 10.0)
    - **niche** (Örn: "gaming", "fitness", "cat-lovers")
4. **And** bu metriklerin ortalaması alınarak bir `ai_score` hesaplanmalıdır.
5. **And** sonuçlar `trends` tablosundaki ilgili satırlara kaydedilmeli ve `analyzed=1` olarak işaretlenmelidir.

## Tasks / Subtasks

- [ ] **Analyzer Altyapısının İncelenmesi**: `analyzer/gemini_scoring.py` içindeki mevcut yapının incelenmesi.
- [ ] **Prompt Geliştirme**: Trendleri POD perspektifinden (mizah, hediye edilebilirlik vb.) en doğru şekilde değerlendirecek sistem promptunun hazırlanması.
- [ ] **JSON Output Parsing**: Gemini'dan gelen yanıtın (JSON formatında olması beklenir) sağlam bir şekilde parse edilmesi ve hata yönetimi.
- [ ] **Batch Processing**: API maliyetini ve hızını optimize etmek için trendlerin 5'li veya 10'lu gruplar halinde gönderilmesi.
- [ ] **Database Update**: `update_scores` fonksiyonunun (db/database.py) yeni metriklerle uyumlu hale getirilmesi.

## Dev Notes

- **Model Selection**: `gemini-1.5-flash` hızı ve maliyeti nedeniyle bu iş için idealdir.
- **API Key**: `.env` içindeki `GEMINI_API_KEY` kullanılmalıdır.
- **Fail-Safe**: API hatası durumunda `analyzed=0` kalmalı ve bir sonraki döngüde tekrar denenmelidir.

### References

- [Source: analyzer/gemini_scoring.py]
- [Source: db/database.py#update_scores]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] Gemini AI entegrasyonu `gemini-flash-latest` modeli ile tamamlandı.
- [x] 4 boyutlu (humor, identity, giftability, design) puanlama sistemi kuruldu.
- [x] Pydantic modelleri (`ScoringOutput`) ile JSON şema kontrolü sağlandı.
- [x] `analyzer/gemini_scoring.py` üzerinden toplu analiz ve DB güncelleme yeteneği eklendi.
- [x] Canlı API testi (`test_gemini_analysis.py`) ile başarıyla doğrulandı.

### File List
- `analyzer/gemini_scoring.py`
- `models.py`
- `prompts/scoring_system.md`
- `prompts/scoring_user.md`
- `_bmad-output/implementation-artifacts/3-1-gemini-analiz-modulu.md`
