# Story 2.2: Radar Skor Placeholder

Status: done

## Story

As a Sistem Mimarı,
I want `trends` tablosunda `radar_score` alanı için bir placeholder değer (0.0) oluşturulmasını,
so that gelecekte momentum ve novelty bazlı trend zekası eklendiğinde şemanın hazır olmasını sağlayabileyim.

## Acceptance Criteria

1. **Given** `trends` tablosu şeması kurulduğunda.
2. **When** yeni bir phrase eklendiğinde.
3. **Then** `radar_score` varsayılan olarak 0.0 değeri almalıdır.

## Tasks / Subtasks

- [x] **Şema Doğrulaması**: `db/database.py` içinde `radar_score REAL DEFAULT 0.0` tanımlandığının konfirme edilmesi.

## Dev Notes

- Bu özellik V2 mimarisi ilk kurulduğunda DDL seviyesinde implement edilmiştir. Extra kod değişikliği gerekmemektedir.

### References

- [Source: db/database.py#L64]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] Veritabanı şemasında `radar_score` sütunu varsayılan 0.0 değeriyle mevcut.
