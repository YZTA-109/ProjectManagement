# Product Backlog — PolyPharm AI

## Ürün Vizyonu

PolyPharm AI, doktorun yeni bir ilaç yazmadan önce hastanın mevcut ilaçları, laboratuvar değerleri ve polifarmasi riskini birlikte değerlendirebildiği, agent tabanlı bir karar destek prototipidir. Backlog, ürünü sırasıyla "çalışan MVP → zengin veri kaynağı → final teslim" aşamalarından geçirecek şekilde önceliklendirilmiştir.

## Durum Özeti

| Sprint | Kapsam | Durum |
|---|---|---|
| Sprint 1 | Çalışan MVP (agent mimarisi, demo veri, temel analiz) | Tamamlandı |
| Sprint 2 | Veri kaynağı/API zenginleştirme, RAG araştırması, UI/test iyileştirme | Planlandı |
| Sprint 3 | Final'e hazırlık, canlıya alma, sunum | Planlandı |

## Backlog — User Stories

| ID | User Story | Öncelik | Sprint | Durum |
|---|---|---:|---|---|
| US-01 | Doktor olarak demo hasta seçebilmek istiyorum; böylece ürünü hızlıca test edebilirim. | High | Sprint 1 | Done |
| US-02 | Doktor olarak manuel hasta bilgisi girebilmek istiyorum; böylece farklı klinik senaryoları deneyebilirim. | High | Sprint 1 | Done |
| US-03 | Doktor olarak mevcut ilaçları ve yeni ilacı analiz ettirmek istiyorum. | High | Sprint 1 | Done |
| US-04 | Sistem olarak ilaç-ilaç etkileşimlerini demo veri tabanından kontrol etmek istiyorum. | High | Sprint 1 | Done |
| US-05 | Sistem olarak laboratuvar değerlerine göre risk sinyali üretmek istiyorum. | High | Sprint 1 | Done |
| US-06 | Doktor olarak güvenlik skoru ve risk seviyesi görmek istiyorum. | High | Sprint 1 | Done |
| US-07 | Doktor olarak analiz raporunu indirebilmek istiyorum. | Medium | Sprint 1 | Done |
| US-08 | Geliştirici olarak temel testleri çalıştırmak istiyorum. | Medium | Sprint 1 | Done |
| US-09 | Ürün ekibi olarak Sprint 1 çıktılarını GitHub üzerinde belgelemek istiyorum. | High | Sprint 1 | Done |
| US-10 | Geliştirici olarak harici bir ilaç veri kaynağı/API'ye bağlanmak istiyorum; böylece demo veri sınırını aşabilirim. | High | Sprint 2 | Backlog |
| US-11 | Geliştirici olarak `DrugDataProvider` katmanı kurmak istiyorum; böylece veri kaynağı değişse de agent'lar etkilenmesin. | High | Sprint 2 | Backlog |
| US-12 | Geliştirici olarak RAG tabanlı resmi kaynak sorgulama olasılığını araştırmak istiyorum. | Medium | Sprint 2 | Backlog |
| US-13 | Doktor olarak daha ayrıntılı ve okunabilir bir analiz raporu almak istiyorum. | Medium | Sprint 2 | Backlog |
| US-14 | Kullanıcı olarak daha akıcı bir arayüz deneyimi yaşamak istiyorum. | Low | Sprint 2 | Backlog |
| US-15 | Geliştirici olarak test kapsamını genişletmek istiyorum. | Medium | Sprint 2 | Backlog |
| US-16 | Ürün ekibi olarak uygulamayı canlıya alınabilir hale getirmek istiyorum. | High | Sprint 3 | Backlog |
| US-17 | Ürün ekibi olarak final demo senaryosunu ve sunum videosunu hazırlamak istiyorum. | High | Sprint 3 | Backlog |
| US-18 | Ürün ekibi olarak README ve tüm dokümantasyonu final teslime hazır hale getirmek istiyorum. | High | Sprint 3 | Backlog |

## Önceliklendirme Mantığı

1. Önce uçtan uca çalışan bir iskelet (Sprint 1).
2. Sonra veri/analiz kalitesini artıran işler (Sprint 2).
3. Son olarak ürün bütünlüğü, canlıya alma ve sunuma hazırlık (Sprint 3).

## Referanslar

- Sprint 1 Backlog: `docs/sprint1/SPRINT_BACKLOG.md`
- User Stories (detaylı): `docs/user_stories.md`
- Sprint 1 Review: `docs/sprint1/SPRINT1_REVIEW.md`
- Sprint 1 Retrospective: `docs/sprint1/RETROSPECTIVE.md`
