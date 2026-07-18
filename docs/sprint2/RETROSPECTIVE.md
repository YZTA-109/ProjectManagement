# Sprint 2 Retrospective

## İyi Gidenler

- Sprint 1 retrospektifindeki "harici veri kaynağı" aksiyonu üç kaynakla (RxNorm, openFDA, Gemini) kapatıldı.
- Provider katmanı sayesinde harici bağımlılıklar izole edildi; her kaynak tek tek kapatılabiliyor.
- Test kapsamı sıfırdan 51 teste çıktı; harici API'ler mock'landığı için testler çevrimdışı da çalışıyor.
- Marka adı çözümlemesi demo senaryolarını belirgin şekilde güçlendirdi.
- Uygulama, harici kaynaklar erişilemediğinde bile Sprint 1 davranışıyla çalışmaya devam ediyor (graceful degradation).

## Zorlayan Noktalar

- RxNorm tam sürümü (~8 GB açılmış hali) doğrudan kullanılamayacak kadar büyüktü; lokal SQLite özütü üretme ihtiyacı doğdu.
- Gemini modellerinde kota kısıtları yaşandı; gemini-2.0-flash yerine gemini-3.1-flash-lite kullanıldı.
- openFDA verileri İngilizce; arayüzde Türkçe özetle birlikte sunulması gerekti (AI özeti bu boşluğu kapatıyor).
- Türkiye'ye özgü marka adları (örn. Majezik) RxNorm'da bulunmuyor; sistem bu durumda ismi olduğu gibi kullanıyor.

## Sonraki Sprint (Sprint 3) İçin Aksiyonlar

- Uygulamanın Streamlit Community Cloud üzerinde canlıya alınması (secrets yönetimiyle).
- Final demo senaryosunun ve sunum videosu akışının hazırlanması.
- README ve dokümantasyonun final teslim formatına getirilmesi.
- Hata ayıklama ve UI cilalama turu.
