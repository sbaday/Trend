# Story 1.3: Google Trends İlgili Sorgu Keşfi

Status: done

## Story

As a POD satıcısı,
I want Google Trends'te yükselen ve top sorguları (related queries) otomatik keşfetmeyi,
so that arama motoru bazlı trend sinyallerini veri setime dahil edebileyim.

## Acceptance Criteria

1. **Given** `pytrends` kütüphanesi aktif ve `google_trends.py` içindeki client yapısı hazır.
2. **When** toplama süreci çalıştığında (`get_related_signals` fonksiyonu tetiklendiğinde).
3. **Then** sistem belirlenen "tohum" (seed) anahtar kelimeler üzerinden `related_queries` metodunu çağırmalıdır.
4. **And** Google Trends rate-limit'lerini engellemek için her istek arasında 1.5 - 3 saniye arası rastgele (jitter) bekleme süresi uygulanmalıdır.
5. **And** çekilen verilerden "Rising" ve "Top" listeleri parse edilip `signals` tablosuna `source='google_trends'`, `subsource='related_queries'` olarak kaydedilmelidir.

## Tasks / Subtasks

- [ ] **Tohum Kelimelerin Belirlenmesi**: Keşif için kullanılacak jenerik (örn: "t-shirt design") veya niş bazlı kelime listesinin `config.py` veya `google_trends.py` içinde tanımlanması.
- [ ] **`get_related_signals` Fonksiyonunun Geliştirilmesi**:
  - [ ] `pytrends.related_queries()` çağrısının yapılması.
  - [ ] "top" ve "rising" DataFrame'lerinin parse edilmesi.
- [ ] **Rate-Limit & Jitter Entegrasyonu**: Mevcut `validate_phrases` içindeki jitter mantığının yeni fonksiyona da uygulanması.
- [ ] **Veritabanı Entegrasyonu**: `insert_signal` fonksiyonu ile her bir sorgunun sinyal olarak kaydedilmesi.
- [ ] **Pipeline Entegrasyonu**: `run_pipeline.py` içindeki `--collect` adımına bu yeni metodun dahil edilmesi.

## Dev Notes

- **Relevant patterns**: Mevcut `google_trends.py` dosyasındaki `TrendReq` yapılandırmasını (build_client) aynen kullanın.
- **Source tree components**: 
  - `collectors/google_trends.py` (Ekleme yapılacak yer)
  - `run_pipeline.py` (Test ve çağrı yeri)
- **Constraint**: Google Trends rate-limit'leri çok katıdır. Tohum kelime listesini başlangıçta küçük tutun (örn: 5-10 kelime).

### Project Structure Notes

- `collectors/google_trends.py` dosyası V2 mimarisinde merkezi bir yere sahiptir.
- SQLite yerine PostgreSQL (DATABASE_URL) kullanıldığından emin olun (Mevcut `db/database.py` bunu sağlıyor).

### References

- [Source: collectors/google_trends.py]
- [Source: db/database.py#insert_signal]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `get_related_signals` fonksiyonu `google_trends.py` dosyasına eklendi.
- [x] Pytrends `related_queries` metodunu kullanarak "Top" ve "Rising" sorguları toplama yeteneği eklendi.
- [x] Rate-limit koruması (jitter) uygulandı.
- [x] `run_pipeline.py` üzerinden otomatik veri toplama akışına entegre edildi.
- [x] Bağımsız test scripti (`test_pytrends_related.py`) ile başarıyla doğrulandı.

### File List
- `collectors/google_trends.py`
- `run_pipeline.py`
- `_bmad-output/implementation-artifacts/1-3-google-trends-ilgili-sorgu-kesfi.md`
