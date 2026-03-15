# Story 4.2: Görsel Tasarım Prompt Motoru

Status: done

## Story

As a POD tasarımcısı,
I want her yüksek potansiyelli trend için Midjourney veya Kittl formatına uygun görsel promptlar üretilmesini,
so that tasarım aşamasına hızlıca geçebileyim.

## Acceptance Criteria

1. **Given** `trends` tablosunda `ai_score` >= 7.0 olan ve henüz tasarım promptu üretilmemiş bir trend olduğunda.
2. **When** üretim süreci (`python run_pipeline.py --generate`) çalıştığında.
3. **Then** Gemini API kullanılarak POD baskı süreçlerine (t-shirt, kupa, vb.) uygun:
    - **Midjourney Prompt**: Stil, kompozisyon, renk paleti ve teknik parametreleri içeren açıklayıcı metin.
    - **Kittl/Vektör Odaklı Açıklama**: Tipografi ve ikonografi önerileri.
4. **And** üretilen bu veri `outputs` tablosuna `output_type='design_prompt'` olarak kaydedilmelidir.

## Tasks / Subtasks

- [ ] **Prompt Template Optimizasyonu**: `design_system.md` ve `design_user.md` promptlarının POD tasarım trendlerine (vintage, minimalist, typography-focused) uygun şekilde zenginleştirilmesi.
- [ ] **Model Entegrasyonu**: `generator/generators.py` içindeki `generate_design_prompt` fonksiyonunun `gemini-flash-latest` ile sorunsuz çalıştığının doğrulanması.
- [ ] **Çıktı Kalite Kontrolü**: Üretilen promptların "clean background", "isolated on white", "vector style" gibi T-shirt baskı dostu anahtar kelimeler içerdiğinden emin olunması.

## Dev Notes

- **Model Selection**: `gemini-flash-latest` hızlı ve görsel betimleme yeteneği yüksek olduğu için tercih edilir.
- **Keywords**: Baskı için arka planı olmayan (isolated) veya kolay temizlenebilir (flat design) öneriler kritiktir.

### References

- [Source: generator/generators.py]
- [Source: prompts/design_system.md]
- [Source: prompts/design_user.md]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `prompts/design_system.md` ve `prompts/design_user.md` dosyaları Midjourney v6 ve Kittl uyumlu hale getirildi.
- [x] Baskı dostu tasarım kriterleri (isolated on white background, vector style, flat design) promptlara eklendi.
- [x] Tipografi ve yerleşim (Kittl style) önerileri için özel talimatlar eklendi.
- [x] Canlı test scripti (`test_design_generation.py`) ile sonuçların kalitesi doğrulandı.

### File List
- `prompts/design_system.md`
- `prompts/design_user.md`
- `_bmad-output/implementation-artifacts/4-2-gorsel-tasarim-prompt-motoru.md`
- `test_design_generation.py`
