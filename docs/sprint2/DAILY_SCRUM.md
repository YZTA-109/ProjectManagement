# Sprint 2 Daily Scrum Notları

> Not: Tarihleri ve katılımcıları ekip toplantı düzenine göre güncelleyin.

## Daily Scrum 1

- Sprint 1 retrospektif aksiyonları gözden geçirildi.
- Harici veri kaynağı araştırması sonuçlandı: openFDA (API) + RxNorm (lokal veri seti) + Gemini (AI özet) kombinasyonuna karar verildi.
- `DrugDataProvider` katmanının mimarisi tasarlandı.

## Daily Scrum 2

- RxNorm tam sürümünden lokal SQLite veritabanı üreten script yazıldı.
- Marka adı → etken madde çözümlemesi doğrulandı (Coumadin → warfarin, Lipitor → atorvastatin).
- openFDA istemcisi geliştirildi ve API anahtarıyla test edildi.

## Daily Scrum 3

- Gemini tabanlı Türkçe klinik özet ajanı eklendi.
- InteractionAgent etken madde çözümlemesiyle güncellendi.
- Orchestrator yeni provider katmanıyla entegre edildi; openFDA kutulu uyarısı bulgu olarak eklendi.

## Daily Scrum 4

- Demo etkileşim veri seti 9 kuraldan 29 kurala çıkarıldı.
- Streamlit arayüzü sekmeli sonuç görünümüne geçirildi; RxNorm geri bildirimi ve veri kaynağı anahtarları eklendi.
- Markdown raporuna harici kaynak bilgisi ve AI özeti bölümleri eklendi.

## Daily Scrum 5

- Test paketi yazıldı: 51 test (agent, provider, orchestrator, mock'lu Gemini/openFDA).
- Uçtan uca canlı API testi yapıldı.
- README ve sprint dokümantasyonu güncellendi.
