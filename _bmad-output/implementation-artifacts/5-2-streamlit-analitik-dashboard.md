# Story 5.2: Streamlit Analitik Dashboard

Status: done

## Story

As a POD satıcısı,
I want toplanan trendleri, AI skorlarını ve üretilen içerikleri tek bir görsel arayüzden yönetebilmeyi,
so that kolay filtreleme ile en değerli trendleri hızlıca tespit edebileyim.

## Acceptance Criteria

1. **Given** veritabanında işlenmiş trendler ve üretilen outputlar bulunuyor.
2. **When** `streamlit run ui/streamlit_app.py` komutu çalıştırıldığında.
3. **Then** sistem şu özellikleri sunan bir dashboard açmalıdır:
    - **Trend Tablosu**: Phrase, Mention Sayısı, AI Skoru ve Niş bilgilerini içeren liste.
    - **Filtreleme**: Niş, Minimum AI Skoru ve Tarih aralığına göre filtreleme.
    - **Detay Görünümü**: Seçilen bir trend için üretilen Etsy Listing ve Tasarım Promptu detayları.
4. **And** dashboard 2 saniye altı bir sürede yüklenmelidir.

## Tasks / Subtasks

- [ ] **UI Altyapısının İncelenmesi**: `ui/streamlit_app.py` dosyasının mevcut durumunun analizi.
- [ ] **Veri Çekme Optimizasyonu**: `db/database.py` üzerinden dashboard için gerekli (join'li) sorguların yazılması.
- [ ] **Tablo ve Filtre Uygulaması**: `st.dataframe` veya `st.table` kullanarak interaktif liste yapısının kurulması.
- [ ] **Detay Panel Tasarımı**: Seçilen trendin tüm çıktılarını (social, etsy, design) yan panelde veya expander içinde gösteren yapının kurulması.

## Dev Notes

- **Performance**: Çok fazla veri olması durumunda pagination veya limit kullanılmalıdır.
- **Visuals**: POD projesi olduğu için arayüzün modern ve temiz (vibrant colors/dark mode support) olması beklenir.

### References

- [Source: ui/streamlit_app.py]
- [Source: db/database.py]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] `db/database.py` içindeki `get_top_trends` fonksiyonuna SQL seviyesinde niş ve tarih filtrelemesi eklendi.
- [x] `ui/streamlit_app.py` üzerinde niş listesi `Literal` değerlerle senkronize edildi.
- [x] Sidebar'a tarih aralığı (date_range) filtresi eklendi.
- [x] Dashbord üzerinden yapılan "On-Demand" içerik üretim mantığı `generators.py` ve Pydantic modelleriyle (model_dump) tam uyumlu hale getirildi.
- [x] Dashboard'un çalışma performansı ve filtreleme mantığı doğrulandı.

### File List
- `db/database.py`
- `ui/streamlit_app.py`
- `_bmad-output/implementation-artifacts/5-2-streamlit-analitik-dashboard.md`
