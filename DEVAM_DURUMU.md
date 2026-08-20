# EYBA — Devam Durumu

Bu dosya, `PROJECT_SPEC.md` kararlarını uygulamaya dönüştüren canlı iş listesidir.
Planla çelişirse ana proje planı ve ardından `PROJECT_SPEC.md` geçerlidir.

## Tamamlananlar

- [x] Proje iskeleti ve merkezi ayarlar
- [x] Foundry Local model yaşam döngüsü
- [x] Faz 1 embedding → retrieval → chat konsol doğrulaması
- [x] Resmî kaynak manifesti, ham arşiv ve SHA-256 kayıtları
- [x] Ham HTML → frontmatter'lı Markdown normalizasyonu
- [x] Normalize betiğindeki sözdizimi hatasının giderilmesi
- [x] Metadata'lı, örtüşmeli ve deterministik JSONL chunk üretimi
- [x] Chunk üretimi için ağsız birim testleri
- [x] Eksik iki İŞKUR kaynağının resmî sayfalardan arşivlenmesi
- [x] Normalize içerik kalite kapısı ve SHA-256/manifest doğrulaması
- [x] 15 kaynak için 47 chunk ve 1024 boyutlu yerel embedding indexi
- [x] 20 soruluk retrieval ölçümü: Top-1 %86,7, Top-3 %100
- [x] `min_similarity=0.39` kalibrasyonu ve kapsam dışı soru reddi
- [x] Yerel RAG servis katmanı ve kaynak kartı sözleşmesi
- [x] FastAPI JSON API ve erişilebilir Türkçe web arayüzü
- [x] README ve tek komutluk Windows başlatıcısı
- [x] `app/` dış ağ importu ve haricî web varlığı için statik offline denetimi
- [x] 24 testlik otomatik kalite paketi ve WCAG kontrast/hedef boyutu kontrolleri
- [x] Gerçek tarayıcıda 320 CSS px yeniden akış ve RAG yanıt/kaynak akışı
- [x] Ağ kısıtlı ortamda 10/10 gerçek yerel model kabul turu
- [x] `1.0.0` sürümü, kaynak ZIP paketi, SHA-256 ve demo senaryosu
- [x] `1.1.0` senaryo tabanlı arayüz, karakter sayacı ve yanıt kopyalama akışı

## Sıradaki işler

- [ ] Ekran okuyucu (NVDA) ve yalnız klavye manuel kabul turu
- [ ] Fiziksel Wi-Fi kapalı turu `--network-condition wifi-off-manual` ile tekrarlamak
- [ ] Gerçek %200/%400 zoom ve Windows Yüksek Karşıtlık manuel kabul turu
- [ ] Retrieval soru setini paraphrase ve zor negatiflerle genişletmek

## Bilinen blokajlar

- `pytest` mevcut `.venv` içine kurulmamış. Testler Python `unittest` ile dış
  bağımlılık olmadan çalıştırılır.
- NVDA, fiziksel Wi-Fi anahtarı, tarayıcı zoomu ve Windows Yüksek Karşıtlık
  doğrulamaları gerçek kullanıcı oturumu gerektirir; otomatik eşdeğerleri PASS olsa da
  bu satırlar insan testi yapılmadan kapatılmaz.
