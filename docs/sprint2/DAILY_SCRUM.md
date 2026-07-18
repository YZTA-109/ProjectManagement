# Daily Scrum Notları - Sprint 2

## Gün 6

- Ne yaptık?
    -  DrugDataService facade'ı ve providers/ katmanı oluşturuldu.
    -  RxNorm tam sürümünden 2,6 MB'lık lokal SQLite veritabanı üreten scripts/build_rxnorm_db.py betiği yazıldı.
    -  API anahtarları .env dosyasına taşındı.
- Ne yapacağız?
  - openFDA API entegrasyonu eklenecek ve kutulu uyarı mantığı sisteme dahil edilecek.
  - Blocker: Yok.

## Gün 7

- Ne yaptık?
      - openFDA drug/label istemcisi eklendi.
      - FDA kutulu uyarıları ve prospektüs metinlerinden dinamik etkileşim tespiti (FdaLabelInteractionAgent) analize dahil edildi.
-  Ne yapacağız?
      - RxNorm üzerinden marka adı çözümleme (marka → etken madde) işlemi kurgulanacak.
      - Yapay zeka ajanının entegrasyonuna başlanacak.
- Blocker:
    -  API bağlantısı koparsa sistemin durmaması lazım; kural tabanlı yapıya geri dönüş (graceful degradation) kurgulanacak.

## Gün 8
- Ne yaptık?
    - Marka adıyla girilen ilaçlar etken maddeye çözümlenir hale getirildi.
    -  GeminiExplainer ajanı (gemini-3.1-flash-lite) eklendi ve Türkçe yapay zeka klinik özeti üretilmeye başlandı.
   - Ne yapacağız? 
    -  Streamlit arayüzü baştan tasarlanacak ve sekmeli yapıya geçirilecek.
    -  Demo veriler genişletilecek.
  - Blocker: Yok.

## Gün 9
- Ne yaptık?
-   Demo etkileşim veri seti 9'dan 29 kurala genişletildi.
-   Streamlit arayüzü beyaz "hastane paneli" temasıyla sekmeli sonuç görünümüne (Özet / Risk Bulguları / İlaç Bilgisi / Ham Çıktı) geçirildi.
-   Markdown raporu güncellendi.
  - Ne yapacağız? Sistemin güvenilirliği için otomatik testlerin yazımına başlanacak.
  - Blocker:
-  openFDA ve Gemini servisleri testleri yavaşlatabilir; mock'lama yapılması gerekecek.

## Gün 10
- Ne yaptık?
-  openFDA ve Gemini mock'lanarak çevrimdışı da çalışabilen 51 adet otomatik test yazıldı.
-  Sprint 2 MVP'si tamamlandı ve tüm geliştirmeler GitHub'a gönderildi.
-Ne yapacağız?
-  Canlıya alma (deployment) seçenekleri ve Streamlit Community Cloud planlaması Sprint 3'e devredilecek.
-  Blocker: Yok.
