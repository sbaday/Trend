# Story 4.1: Otomatik Etsy Listing Üretimi

Status: done

## Story

As a Etsy satıcısı,
I want yüksek potansiyelli (ai_score ≥ 7.0) trendler için optimize edilmiş başlık, açıklama ve taglar üretilmesini,
so that manuel listing yazmaya zaman harcamadan içerik elde edeyim.

## Acceptance Criteria

1. **Given** `trends` tablosunda `ai_score` >= 7.0 olan ve henüz listing üretilmemiş bir trend olduğunda.
2. **When** üretim süreci (`python run_pipeline.py --generate`) çalıştığında.
3. **Then** Gemini API kullanılarak Etsy standartlarına uygun:
    - **Title**: Max 140 karakter, SEO uyumlu.
    - **Description**: Ürün özelliklerini vurgulayan, ilgi çekici açıklama.
    - **Tags**: 13 adet SEO anahtar kelimesi.
4. **And** üretilen bu veriler `outputs` tablosuna `output_type='etsy_listing'` olarak kaydedilmelidir.

## Tasks / Subtasks

- [ ] **Generator Modülü Analizi**: `generator/generators.py` içindeki mevcut listing üretim mantığının incelenmesi.
- [ ] **Prompt Geliştirme**: Etsy SEO prensiplerine uygun `listing_system.md` ve `listing_user.md` promptlarının optimize edilmesi.
- [ ] **JSON Output Parsing**: Listing verilerinin JSON formatında alınması ve `outputs` tablosuna uygun şekilde serileştirilmesi.
- [ ] **Pipeline Entegrasyonu**: `run_pipeline.py` içindeki `--generate` flag'inin sadece Etsy listing değil, Story 4.1 kapsamında listing üretmesini sağlamak.

## Dev Notes

- **SEO Focus**: Etsy algoritması için başlık ve ilk birkaç tag kritiktir.
- **Data Persistence**: `outputs` tablosu `trend_id` ile `trends` tablosuna referans verir. Bir trend için birden fazla listing üretilmemesi için kontrol eklenmelidir.

### References

- [Source: generator/generators.py]
- [Source: db/database.py]
- [Source: prompts/listing_system.md]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `generator/generators.py` stabil `gemini-flash-latest` modelini kullanacak şekilde güncellendi.
- [x] Etsy SEO kriterlerine uygun (Title <= 140 karakter, tam 13 tag) üretim mantığı kuruldu.
- [x] `run_pipeline.py --generate` üzerinden yüksek skorlu trendler için otomatik listing üretimi sağlandı.
- [x] Canlı test scripti (`test_etsy_generation.py`) ile doğrulandı.

### File List
- `generator/generators.py`
- `_bmad-output/implementation-artifacts/4-1-otomatik-etsy-listing-uretimi.md`
- `test_etsy_generation.py`
