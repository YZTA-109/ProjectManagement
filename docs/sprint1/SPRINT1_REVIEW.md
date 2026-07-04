# Sprint 1 Review

## Sprint Hedefi

PolyPharm AI ürün fikrini çalışan bir MVP iskeletine dönüştürmek.

## Tamamlananlar

- Streamlit doktor paneli
- Demo hasta seçimi
- Manuel hasta girişi
- Mevcut ilaç ve yeni ilaç analizi
- Demo ilaç-ilaç etkileşim kontrolü
- eGFR, AST, ALT ve yaş/ilaç sayısı tabanlı risk kontrolleri
- Güvenlik skoru
- Risk seviyesi
- Markdown raporu indirme
- Unit testler
- Sprint 1 dokümantasyonu

## Ürün Durumu

Ürün Sprint 1 sonunda lokal ortamda çalıştırılabilir durumdadır.

Çalıştırma:

```bash
streamlit run main.py
```

Test:

```bash
python -m pytest -q
```

## Demo Senaryo

1. Demo Hasta 1 seçilir.
2. Yeni ilaç olarak `aspirin` seçilir.
3. Sistem:
   - Warfarin-aspirin etkileşimi bulur.
   - eGFR düşüklüğünü tespit eder.
   - Yaşlı hastada polifarmasi riskini gösterir.
   - Güvenlik skoru ve risk seviyesi üretir.

## Sprint 2 Önerileri

- Resmi ilaç dokümanları ile RAG
- LLM destekli açıklama ve öneri üretimi
- İlaç adı normalizasyonu
- Kullanıcı oturumu ve analiz geçmişi
- Daha geniş demo etkileşim veri tabanı
