# Story 5.1: Pipeline Orkestrasyonu & Zamanlama

Status: done

## Story

As a Yoğun POD Satıcısı,
I want sistemin bir zamanlayıcı yardımıyla otomatik çalışmasını,
so that tüm trend takip döngüsünün (toplama, analiz, üretim) müdahalesiz ilerlemesini sağlayabileyim.

## Acceptance Criteria

1. **Given** APScheduler kütüphanesi yüklü ve yapılandırılmış.
2. **When** `python run_pipeline.py --schedule` komutu çalıştırıldığında.
3. **Then** sistem şu zamanlamaya göre çalışmalıdır:
    - **Her 2 Saatte Bir**: Veri Toplama, Phrase Extraction ve Gemini Analizi.
    - **Günde Bir Kez (Gece 04:00)**: Momentum Engine (Viral Doğrulama).
4. **And** her adımın başlangıcı, sonucu ve hataları loglanmalıdır.
5. **And** sistem Railway veya benzeri bir platformda 7/24 çalışabilir durumda olmalıdır.

## Tasks / Subtasks

- [ ] **APScheduler Konfigürasyonu**: `run_pipeline.py` içindeki `run_schedule` fonksiyonunun Railway dostu olacak şekilde (BlockingScheduler) optimize edilmesi.
- [ ] **Hata Yönetimi (Graceful Failure)**: Job'lar arasında oluşabilecek hataların (API timeout vb.) tüm sistemi durdurmaması için `try-except` bloklarının güçlendirilmesi.
- [ ] **Logging Sistemi**: `logging` modülünü kullanarak çalışma geçmişinin kalıcı log dosyalarına yazılması.
- [ ] **Zamanlama Testi**: Zamanlayıcının job'ları doğru sırayla tetiklediğinin (dry-run modunda) doğrulanması.

## Dev Notes

- **BlockingScheduler**: Railway veya Docker ortamlarında ana process'in canlı kalması için tercih edilir.
- **Fail-Safe**: Eğer bir toplama job'ı başarısız olursa, bir sonraki 2 saatlik döngüde tekrar denenecektir.

### References

- [Source: run_pipeline.py#L120]
- [Documentation: APScheduler BlockingScheduler]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `run_pipeline.py` içindeki `run_schedule` fonksiyonu tam döngü (Adım 1-4) için güncellendi.
- [x] `logging` modülü entegre edilerek `pipeline.log` dosyasına kalıcı kayıt tutma mantığı kuruldu.
- [x] `APScheduler` (BlockingScheduler) ile 2 saatlik interval ve günlük 04:00 momentum check zamanlaması yapıldı.
- [x] Her bir job için hata yakalama (try-except) eklenerek sistemin dayanıklılığı artırıldı.
- [x] `test_scheduler_logic.py` ile mimari değişiklikler doğrulandı.

### File List
- `run_pipeline.py`
- `_bmad-output/implementation-artifacts/5-1-pipeline-orkestrasyonu-zamanlama.md`
- `test_scheduler_logic.py`
