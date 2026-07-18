# Sprint 2 Backlog

| No | User Story / Görev | Öncelik | Durum |
| --- | --- | --- | --- |
| 1 | Geliştirici olarak harici ilaç veri kaynaklarını tek bir `DrugDataProvider` katmanı arkasında toplamak istiyorum, böylece yeni kaynaklar kolayca eklenebilsin. | Yüksek | Tamamlandı |
| 2 | Doktor olarak yeni ilacın FDA prospektüs uyarılarını (kutulu uyarı, etkileşim metni) görmek istiyorum, böylece resmi kaynak temelli risk bilgisine ulaşabileyim. | Yüksek | Tamamlandı |
| 3 | Doktor olarak marka adıyla ilaç girebilmek istiyorum (örn. Coumadin), sistemin bunu etken maddeye (warfarin) çözümleyerek etkileşim kontrolü yapmasını istiyorum. | Yüksek | Tamamlandı |
| 4 | Doktor olarak analiz sonucunun Türkçe, okunabilir bir yapay zeka özetini görmek istiyorum, böylece bulguları hızla kavrayabileyim. | Orta | Tamamlandı |
| 5 | Geliştirici olarak demo etkileşim veri setini genişletmek istiyorum, böylece daha fazla senaryo test edilebilsin. | Orta | Tamamlandı |
| 6 | Doktor olarak analiz sonuçlarını sekmeli, düzenli bir arayüzde görmek istiyorum. | Orta | Tamamlandı |
| 7 | Kullanıcı olarak indirilen raporda harici kaynak bilgisi ve AI özetini de görmek istiyorum. | Düşük | Tamamlandı |
| 8 | Geliştirici olarak tüm agent ve provider'lar için otomatik test istiyorum, böylece regresyonlar erken yakalansın. | Yüksek | Tamamlandı |
| 9 | Geliştirici olarak uygulamanın canlıya alınma seçeneklerini değerlendirmek istiyorum. | Düşük | Sprint 3'e devredildi |

## Teknik Görev Dökümü

- `providers/rxnorm_provider.py` — lokal RxNorm SQLite sorguları (isim → RXCUI, marka → etken madde, öneri)
- `providers/openfda_client.py` — openFDA drug/label istemcisi (önbellek, zaman aşımı, sessiz hata düşüşü)
- `providers/local_json_provider.py` — JSON etkileşim kural sağlayıcısı
- `providers/drug_data_service.py` — tüm kaynakları birleştiren facade
- `scripts/build_rxnorm_db.py` — tam RxNorm sürümünden 2,6 MB'lık lokal veritabanı üretimi
- `agents/gemini_explainer.py` — Gemini (gemini-3.1-flash-lite) ile Türkçe klinik özet
- `agents/interaction_agent.py` — etken madde çözümlemeli etkileşim eşleştirme
- `agents/orchestrator.py` — provider + AI akış entegrasyonu, openFDA kutulu uyarı bulgusu
- `data/demo_interactions.json` — 9 → 29 kural
- `tests/` — 51 test (agent'lar, provider'lar, orchestrator, Gemini mock)
