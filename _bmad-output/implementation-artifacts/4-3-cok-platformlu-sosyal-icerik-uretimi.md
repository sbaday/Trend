# Story 4.3: Çok Platformlu Sosyal İçerik Üretimi

Status: done

## Story

As a POD satıcısı,
I want satışlarımı desteklemek için trend bazlı TikTok hook, Pinterest başlığı ve Instagram caption üretilmesini,
so that sosyal medya promosyonlarını otomatikleştirebileyim.

## Acceptance Criteria

1. **Given** `trends` tablosunda `ai_score` >= 7.0 olan ve henüz sosyal içerik üretilmemiş bir trend olduğunda.
2. **When** üretim süreci (`python run_pipeline.py --generate`) çalıştığında.
3. **Then** Gemini API kullanılarak:
    - **TikTok**: Dikkat çekici bir "hook" (ilk 3 saniye cümlesi).
    - **Pinterest**: SEO odaklı başlık ve açıklama.
    - **Instagram**: Emoji destekli, hashtag içeren bir "caption".
4. **And** üretilen bu veri `outputs` tablosuna `output_type='social_content'` olarak JSON formatında kaydedilmelidir.

## Tasks / Subtasks

- [ ] **Prompt Geliştirme**: `social_system.md` ve `social_user.md` promptlarının viral platform trendlerine uygun şekilde güncellenmesi.
- [ ] **Model Doğrulaması**: `generator/generators.py` içindeki `generate_social_content` fonksiyonunun `gemini-flash-latest` ile JSON çıktı kalitesinin kontrolü.
- [ ] **Hashtag Optimizasyonu**: Instagram için niş bazlı stratejik hashtag önerileri eklenmesi.

## Dev Notes

- **Platform Switch**: Her platformun tonu farklıdır (TikTok: enerjik, Pinterest: SEO/İlham, Instagram: estetik). Prompt buna göre ayrıştırılmalıdır.
- **JSON Structure**: `SocialContentOutput` modeli (`models.py`) ile tam uyumlu çıktı alınmalıdır.

### References

- [Source: generator/generators.py]
- [Source: models.py#SocialContentOutput]
- [Source: prompts/social_system.md]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] TikTok, Pinterest ve Instagram için platform-spesifik viral promptlar (`prompts/social_system.md`, `prompts/social_user.md`) hazırlandı.
- [x] Instagram için otomatik hashtag stratejisi ve TikTok için "curiosity hook" mantığı eklendi.
- [x] `generator/generators.py` üzerinden `social_content` üretimi ve JSON parsing başarıyla test edildi.
- [x] Canlı test scripti (`test_social_generation.py`) ile doğrulandı.

### File List
- `prompts/social_system.md`
- `prompts/social_user.md`
- `_bmad-output/implementation-artifacts/4-3-cok-platformlu-sosyal-icerik-uretimi.md`
- `test_social_generation.py`
