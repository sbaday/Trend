# Story 5.3: Monitoring & Çalışma Geçmişi

Status: done

## Story

As a Sistem Yöneticisi,
I want arka planda çalışan pipeline job'larının durumunu ve sistem loglarını dashboard üzerinden izleyebilmeyi,
so that olası hataları (API limitleri, bağlantı kopmaları) anında fark edip müdahale edebileyim.

## Acceptance Criteria

1. **Given** `pipeline.log` dosyası veya bir `job_history` tablosu mevcut.
2. **When** dashboard üzerinde "Sistem Günlüğü" veya "Monitoring" sekmesi açıldığında.
3. **Then** şu bilgiler görüntülenmelidir:
    - **Son Loglar**: `pipeline.log` dosyasının son 50-100 satırı.
    - **Döngü Özeti**: Son başarılı tam döngü (full cycle) zamanı.
    - **Hata Bildirimleri**: Kritik (`ERROR` seviyesindeki) logların belirginleştirilmiş listesi.
4. **And** loglar canlı olarak (veya manuel yenileme ile) takip edilebilmelidir.

## Tasks / Subtasks

- [ ] **Log Okuma Mekanizması**: `pipeline.log` dosyasını güvenli ve performanslı şekilde okuyacak fonksiyonun yazılması.
- [ ] **Monitoring Sekmesi Ekleme**: `ui/streamlit_app.py` içine yeni bir tab eklenmesi.
- [ ] **Görselleştirme**: Log seviyelerine göre (INFO: yeşil, ERROR: kırmızı) renklendirilmiş bir metin alanı veya tablo yapısının kurulması.
- [ ] **Sistem Metrikleri**: Disk kullanımı veya veritabanı kapasitesi gibi temel operasyonel verilerin eklenmesi (isteğe bağlı).

## Dev Notes

- **Log Rotation**: Log dosyası çok büyürse performansı etkileyebilir. Gelecekte `RotatingFileHandler` düşünülmelidir.
- **Security**: Railway ortamında dosya okuma izinleri kontrol edilmelidir.

### References

- [Source: run_pipeline.py]
- [Source: pipeline.log]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] Streamlit dashboard'a "Sistem İzleme" sekmesi eklendi.
- [x] `pipeline.log` dosyasından son 100 satırı okuyup `ERROR` (kırmızı), `WARNING` (sarı) ve `INFO` (normal) seviyelerine göre renklendiren yapı kuruldu.
- [x] Logları dashboard üzerinden temizleme (🗑️) butonu eklendi.
- [x] Sunucu saati, çalışma dizini ve veritabanı modu gibi temel monitoring metrikleri eklendi.
- [x] Testlerde logların doğru şekilde yüklendiği ve renklendirildiği doğrulandı.

### File List
- `ui/streamlit_app.py`
- `_bmad-output/implementation-artifacts/5-3-monitoring-calisma-gecmisi.md`
