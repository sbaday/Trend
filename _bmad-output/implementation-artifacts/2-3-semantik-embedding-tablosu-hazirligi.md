# Story 2.3: Semantik Embedding Tablosu Hazırlığı

Status: done

## Story

As a Sistem Mimarı,
I want `trend_embeddings` tablosunun semantik veri için hazırlanmasını,
so that V3'te semantik kümeleme yapıldığında altyapı hazır olsun.

## Acceptance Criteria

1. **Given** PostgreSQL veritabanı bağlantısı aktif.
2. **When** `init_db()` fonksiyonu çalıştırıldığında.
3. **Then** 384-boyutlu vektörleri destekleyen `trend_embeddings` tablosu oluşturulmalıdır.
4. **And** tablo `trend_id` üzerinden `trends` tablosuna referans vermelidir.

## Tasks / Subtasks

- [ ] **Tablo Tanımlama**: `db/database.py` içine `trend_embeddings` tablosunun eklenmesi.
- [ ] **Migration Çalıştırma**: Mevcut veritabanına yeni tablonun eklenmesi için migration scriptinin hazırlanması/çalıştırılması.

## Dev Notes

- **Choice of Type**: PostgreSQL üzerinde `REAL[]` (array) kullanımı pgvector kurulumu gerektirmediği için başlangıç seviyesinde daha uyumludur. V3'te gerekirse `vector` tipine dönüştürülebilir.

### References

- [Source: db/database.py]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `db/database.py` içine `trend_embeddings` tablosu eklendi.
- [x] V3 semantik kümeleme için 384-boyutlu vektörleri destekleyen `REAL[]` altyapısı hazırlandı.
- [x] Migration scripti (`migrate_embeddings_table.py`) oluşturuldu.

### File List
- `db/database.py`
- `migrate_embeddings_table.py`
- `_bmad-output/implementation-artifacts/2-3-semantik-embedding-tablosu-hazirligi.md`
