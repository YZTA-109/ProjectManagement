# User Stories — Kabul Kriterleri (Sprint 1)

Bu doküman, `docs/product_backlog.md` içindeki Sprint 1 kapsamındaki (US-01–US-09) user story'lerin detaylı kabul kriterlerini içerir. Sprint 2 ve Sprint 3'teki story'ler (US-10–US-18) henüz backlog aşamasında olduğu için kabul kriterleri ilgili sprint planlamasında detaylandırılacaktır.

---

## US-01 — Demo hasta seçimi

**Doktor olarak** demo hasta seçebilmek istiyorum; **böylece** ürünü hızlıca test edebilirim.

**Kabul Kriterleri:**
- Streamlit arayüzünde önceden tanımlı demo hastalar (`data/sample_patients.json`) listeden seçilebilir.
- Demo hasta seçildiğinde yaş, cinsiyet, mevcut ilaç listesi ve laboratuvar değerleri (eGFR, kreatinin, AST, ALT) otomatik doldurulur.
- Kullanıcı ek bir veri girişi yapmadan doğrudan analiz akışına geçebilir.

---

## US-02 — Manuel hasta girişi

**Doktor olarak** manuel hasta bilgisi girebilmek istiyorum; **böylece** farklı klinik senaryoları deneyebilirim.

**Kabul Kriterleri:**
- Yaş (0–120), cinsiyet, mevcut ilaç listesi alanları manuel olarak doldurulabilir.
- Girilen ilaç isimleri normalize edilir (baş/son boşluk temizlenir, büyük/küçük harfe duyarsız tekrarlar tekilleştirilir).
- Zorunlu alanlar boş bırakıldığında (`Patient`/`PrescriptionRequest` validasyonu) kullanıcıya uyarı gösterilir.

---

## US-03 — Yeni ilaç analizi

**Doktor olarak** mevcut ilaçları ve yeni ilacı analiz ettirmek istiyorum.

**Kabul Kriterleri:**
- Yeni yazılmak istenen ilaç adı girilebilir ve boş bırakılamaz (`min_length=1`).
- "Analiz Et" tetiklendiğinde `Orchestrator.analyze()` çağrılır ve tüm agent'lar (Interaction, LabRisk, Scoring, Report) sırayla çalışır.
- Analiz sonucu ekranda güvenlik skoru, risk seviyesi ve bulgu listesi olarak gösterilir.

---

## US-04 — İlaç-ilaç etkileşim kontrolü

**Sistem olarak** ilaç-ilaç etkileşimlerini demo veri tabanından kontrol etmek istiyorum.

**Kabul Kriterleri:**
- `InteractionAgent`, yeni ilacı hastanın mevcut ilaç listesindeki her bir ilaçla `data/demo_interactions.json` üzerinden karşılaştırır.
- Eşleşen bir etkileşim bulunursa `RiskFinding` (başlık, önem derecesi, açıklama, öneri) üretilir.
- Etkileşim bulunmazsa ilgili agent'tan boş bulgu listesi döner; sistem hatasız devam eder.

---

## US-05 — Laboratuvar temelli risk sinyalleri

**Sistem olarak** laboratuvar değerlerine göre risk sinyali üretmek istiyorum.

**Kabul Kriterleri:**
- `LabRiskAgent`, eGFR ve kreatinin değerlerine göre böbrek fonksiyonu riskini değerlendirir.
- `LabRiskAgent`, AST ve ALT değerlerine göre karaciğer fonksiyonu riskini değerlendirir.
- Hastanın yaşı ve mevcut ilaç sayısına göre polifarmasi riski ayrıca değerlendirilir.
- Tüm laboratuvar değerleri tanımlı aralıklar içinde olmalıdır (örn. eGFR 0–150, kreatinin 0–20); aralık dışı girişte validasyon hatası verilir.

---

## US-06 — Güvenlik skoru ve risk seviyesi

**Doktor olarak** güvenlik skoru ve risk seviyesi görmek istiyorum.

**Kabul Kriterleri:**
- `ScoringAgent`, `InteractionAgent` ve `LabRiskAgent`'tan gelen tüm bulguları önem derecesine göre (critical > high > medium > low) sıralar.
- Bulgulara göre 0–100 arası bir `safety_score` ve buna karşılık gelen bir `risk_level` (örn. düşük/orta/yüksek) hesaplanır.
- Sonuç, kullanıcı arayüzünde net ve tek bakışta anlaşılır şekilde gösterilir.

---

## US-07 — Raporu dışa aktarma

**Doktor olarak** analiz raporunu indirebilmek istiyorum.

**Kabul Kriterleri:**
- `ReportAgent`, bulgular ve güvenlik skorunu okunabilir bir özet (`recommendation_summary`) haline getirir.
- Tam analiz, Markdown formatında (`markdown_report`) indirilebilir.
- Ham analiz çıktısı JSON formatında da arayüzde görüntülenebilir.

---

## US-08 — Temel testler

**Geliştirici olarak** temel testleri çalıştırmak istiyorum; **böylece** analiz mantığının doğru çalıştığını doğrulayabilirim.

**Kabul Kriterleri:**
- `pip install -r requirements.txt` sonrası `pytest` kurulu olur.
- `python -m pytest -q` komutu proje kök dizininde hatasız/anlamlı sonuç döner.
- En az MVP akışının uçtan uca (hasta girişi → analiz → sonuç) doğru çalıştığını doğrulayan bir test seti bulunur.

> **Not:** Bu kriter Sprint 1 sonunda backlog'da "Devam Ediyor" olarak işaretlenmiştir; `tests/` klasörünün eklenmesi Sprint 2'ye taşınmıştır.

---

## US-09 — Sprint 1 dokümantasyonu

**Ürün ekibi olarak** Sprint 1 çıktılarını GitHub üzerinde belgelemek istiyorum.

**Kabul Kriterleri:**
- `README.md` içinde takım, ürün, mimari ve kurulum bilgileri eksiksiz yer alır.
- `docs/sprint1/` altında Sprint Backlog, Daily Scrum notları, Sprint Review ve Retrospective belgeleri bulunur.
- Ürünün çalıştığını gösteren en az iki ekran görüntüsü (`docs/sprint1/screenshots/`) eklenir.
- Tüm dokümanlar GitHub reposunda public olarak erişilebilir durumdadır.

---

## Referanslar

- Product Backlog: `docs/product_backlog.md`
- Sprint 1 Backlog: `docs/sprint1/SPRINT_BACKLOG.md`
- Sprint 1 Review: `docs/sprint1/SPRINT1_REVIEW.md`
- Sprint 1 Retrospective: `docs/sprint1/RETROSPECTIVE.md`