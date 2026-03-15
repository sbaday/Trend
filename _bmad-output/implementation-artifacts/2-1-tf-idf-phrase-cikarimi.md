# Story 2.1: TF-IDF Phrase Çıkarımı

Status: done

## Story

As a POD satıcısı,
I want "I survived 2025 and all I got was this lousy t-shirt" gibi ham başlıklardan "survived 2025" gibi anlamlı phrase'ler çıkarılmasını,
so that doğrudan tasarıma uygulanabilir konseptler elde edeyim.

## Acceptance Criteria

1. **Given** `signals` tablosunda henüz işlenmemiş ham başlıklar bulunduğunda.
2. **When** extraction süreci (`python run_pipeline.py --extract`) çalıştığında.
3. **Then** sistem TF-IDF algoritması ile n-gram phrase extraction yaparak en anlamlı 1, 2 ve 3 kelimelik öbekleri belirlemelidir.
4. **And** belirlenen phrase'ler `trends` tablosuna "upsert" edilmelidir (Eğer phrase zaten varsa `total_mentions` 1 artırılmalı, yoksa yeni kayıt açılmalıdır).
5. **And** her trend için platform bazlı `trend_signals` (zaman serisi) kaydı güncellenmelidir.

## Tasks / Subtasks

- [ ] **Extraction Mantığının İncelenmesi**: `extraction/phrase_extractor.py` içindeki mevcut TF-IDF implementasyonunun incelenmesi ve n-gram (1-3) desteğinin kontrolü.
- [ ] **Gürültü Filtreleme**: "a", "the", "in" gibi durak kelimelerinin (stop words) ve POD için anlamsız kısa kelimelerin elenmesi.
- [ ] **Veritabanı Entegrasyonu (Upsert)**: `db/database.py` içindeki `upsert_trend` fonksiyonunun n-gram phrase'leri doğru şekilde kaydedip sayacı artırdığının doğrulanması.
- [ ] **Pipeline Otomasyonu**: `run_pipeline.py` içindeki `run_extract` fonksiyonunun, tüm ham sinyalleri tek tek değil, toplu (batch) işleyip phrase'lere dönüştürecek şekilde optimize edilmesi.

## Dev Notes

- **Relevant patterns**: Scikit-learn TfidfVectorizer kullanımı.
- **Source tree components**: 
  - `extraction/phrase_extractor.py`
  - `run_pipeline.py`
  - `db/database.py`
- **Constraint**: Çok genel kelimelerden (örn: "t-shirt") kaçınmak için TF-IDF skor eşiği veya min_df parametreleri kullanılabilir.

### References

- [Source: extraction/phrase_extractor.py]
- [Source: db/database.py#upsert_trend]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `signals` tablosuna `processed` (boolean) kolonu eklendi (Teknik borç temizlendi).
- [x] `phrase_extractor.py` n-gram (1-3) destekleyecek şekilde güncellendi.
- [x] `STOP_WORDS` listesi possessive pronoun'lar ile zenginleştirildi.
- [x] `run_pipeline.py` üzerinden toplu işleme ve sinyalleri "işlendi" olarak işaretleme mantığı kuruldu.
- [x] Bağımsız test scripti (`test_extraction_logic.py`) ile doğrulandı.

### File List
- `db/database.py`
- `extraction/phrase_extractor.py`
- `run_pipeline.py`
- `_bmad-output/implementation-artifacts/2-1-tf-idf-phrase-cikarimi.md`
