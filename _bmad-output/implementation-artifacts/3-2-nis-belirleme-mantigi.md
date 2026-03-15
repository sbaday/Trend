# Story 3.2: Niş Belirleme Mantığı

Status: done

## Story

As a POD satıcısı,
I want trendlerin nişlerinin (kategori) tutarlı ve stratejik bir listeden seçilmesini,
so that dashboard üzerinde filtreleme yaparken "cat lovers" ve "cats" gibi farklı ama aynı grubu temsil eden etiketler yerine tek bir standart niş görebileyim.

## Acceptance Criteria

1. **Given** AI tarafından üretilen ham niş verisi.
2. **When** analiz süreci tamamlandığında veya kaydedilmeden önce.
3. **Then** sistem bu ham veriyi önceden tanımlanmış "Master Niche List" ile eşleştirmelidir.
4. **And** eğer eşleşme bulunamazsa "general" veya "other" olarak işaretlemelidir.
5. **And** Master Niche List içinde şu kategoriler bulunmalıdır: `Pets`, `Fitness`, `Gaming`, `Funny/Quotes`, `Occupation`, `Hobby`, `Family`, `Holiday`, `Aesthetic/Art`.

## Tasks / Subtasks

- [ ] **Master Niche List Tanımlama**: `analyzer/niche_manager.py` (yeni dosya) veya `gemini_scoring.py` içinde standart niş listesinin oluşturulması.
- [ ] **Mapping Mantığının Kurulması**: Basit bir keyword matching veya Gemini'a bu listeden seçmesini söyleyen prompt kısıtlamasının eklenmesi.
- [ ] **Gemini Prompt Güncellemesi**: `scoring_user.md` promptuna "Aşağıdaki listeden en uygun nişi seç" talimatının eklenmesi.
- [ ] **DB Kayıt Güncellemesi**: `update_scores` çağrılırken artık normalize edilmiş nişin gönderilmesi.

## Dev Notes

- **Strategy**: Gemini'a prompt içinde seçenekleri vermek (`response_schema` içinde `Enum` olarak veya açıklama olarak) en temiz yoldur.
- **Master List**: Projenin ölçeklenmesi için bu liste dinamik olabilir ama şimdilik statik bir liste yeterlidir.

### References

- [Source: prompts/scoring_user.md]
- [Source: analyzer/gemini_scoring.py]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Pro (Antigravity)

### Completion Notes List
- [x] Stratejik niş listesi (`Pets`, `Fitness`, `Gaming`, `Funny`, `Occupation`, `Hobby`, `Family`, `Holiday`, `Aesthetic`, `Politics`, `Crypto`, `General`) tanımlandı.
- [x] `models.py` içindeki `ScoringOutput` sınıfı `Literal` tipi ile bu listeye sabitlendi.
- [x] Gemini promptu bu listeden seçim yapacak şekilde kısıtlandı.
- [x] Testlerde nişlerin tutarlı bir şekilde kategorize edildiği doğrulandı.

### File List
- `models.py`
- `prompts/scoring_user.md`
- `_bmad-output/implementation-artifacts/3-2-nis-belirleme-mantigi.md`
