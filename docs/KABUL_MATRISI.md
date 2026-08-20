# EYBA Kabul Matrisi

Bu matris otomatik kanıtları gerçek cihazda yapılması gereken insan testlerinden ayırır.
`WCAG 2.2 AA uyumlu` ifadesi yalnız tüm zorunlu satırlar PASS olduğunda kullanılabilir.

| Alan | Yöntem | Sonuç | Kanıt / not |
|---|---|---:|---|
| Birim ve API testleri | `python -m unittest discover -s tests -v` | PASS | 24/24, 2026-08-21 |
| Bilgi tabanı bütünlüğü | `scripts/validate_knowledge.py` | PASS | 15 kaynak, 47 chunk |
| Retrieval | 20 soruluk ölçüm | PASS | Top-1 %86,7; Top-3 %100 |
| Dış ağsız runtime kodu | Statik import ve haricî varlık denetimi | PASS | `tests/test_offline_runtime.py` |
| 320 CSS px yeniden akış | Gerçek tarayıcı, yatay taşma ölçümü | PASS | `scrollWidth=305`, `innerWidth=320` |
| Erişilebilir adlar ve bölgeler | Tarayıcı erişilebilirlik ağacı | PASS | Form, durum ve yanıt bölgeleri adlandırılmış |
| Renk kontrastı | Otomatik WCAG oran testi | PASS | Normal metin ≥4.5:1, odak/sınır ≥3:1 |
| 44×44 hedef boyutu | CSS sözleşme testi | PASS | Kontroller en az 48×48 CSS px |
| Gerçek RAG web akışı | Tarayıcıdan soru → cevap → kaynak | PASS | Yanıt odağı ve kaynak kartı doğrulandı |
| Senaryo akışı | Kart → hazır soru → sayaç → yanıt → kopyalama | PASS | Gerçek tarayıcı, 2026-08-21 |
| 10 soruluk çevrimdışı kabul | `scripts/run_offline_acceptance.py` | PASS | Ağ kısıtlı ortam, 10/10, 2026-08-21 |
| Yalnız klavye | Gerçek klavye ile manuel tur | MANUEL | Aşağıdaki kontrol listesi |
| NVDA | NVDA + Firefox/Edge manuel tur | MANUEL | Aşağıdaki kontrol listesi |
| %200/%400 zoom | Tarayıcı zoom ile görsel tur | MANUEL | 320 CSS px otomatik reflow testi PASS |
| Windows yüksek karşıtlık | Forced Colors ile manuel tur | MANUEL | CSS `forced-colors` desteği mevcut |

## Manuel erişilebilirlik kontrol listesi

- [ ] `Tab` ile “Ana içeriğe geç”, soru, “Yanıtı getir” ve “Temizle” sırası anlaşılır.
- [ ] Her odaklanan öğede görünür odak halkası vardır.
- [ ] NVDA sayfa başlığını, ana başlığı, soru etiketini ve yardım metnini okur.
- [ ] Arama sırasında durum mesajı; tamamlanınca “Yanıt hazır” duyurulur.
- [ ] Yanıt geldiğinde odak “Yanıt” başlığına gider; kaynaklar liste olarak okunur.
- [ ] Hata ve yetersiz bağlam mesajları yalnız renkle anlatılmaz.
- [ ] %200 ve %400 zoomda içerik veya işlev kaybı olmaz.
- [ ] Windows Yüksek Karşıtlık modunda sınırlar ve odak göstergesi görünür.

Manuel turu yapan kişi tarih, tarayıcı, NVDA sürümü ve sonucu bu dosyaya eklemelidir.
