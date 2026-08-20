# PROJECT_SPEC — Accessible Local RAG Assistant (EYBA)

Bu dosya, ana plan dokümanı **Accessible_Local_RAG_Foundry_Local_WCAG_Proje_Plani.md v1.0**
(§76 Faz 0) uyarınca projenin sabitlenmiş kararlarını içerir. Plan çizgisinden sapma yoktur;
bir madde planla çelişirse plan üstündür.

## 1. Kullanım senaryosu

Engelli bireylerin Türkiye'deki temel haklar, kamu hizmetleri ve pilot şehirdeki yerel
hizmetler hakkında **internet olmadan**, **resmî kaynaklara dayalı** ve **kaynak gösteren**
bilgi almasını sağlayan, cihaz üzerinde çalışan RAG asistanı.

Ürün adı: Erişilebilir Yerel Bilgi Asistanı (EYBA)

## 2. Kapsam (plan §4.1)

Ulusal: engelli kimlik kartı, engelli hakları, sosyal hizmetler, evde bakım, engelli sağlık
kurulu raporu, yetkili sağlık kuruluşları, İŞKUR engelli kaydı, engelli istihdamı, EKPSS,
erişilebilir ulaşım, afet ve acil durum hazırlığı, dijital erişilebilirlik.

Yerel — pilot şehir **Şanlıurfa**: Büyükşehir Belediyesi Engelsiz Yaşam içerikleri,
Engelliler Koordinasyon ve Yaşam Merkezi, belediye iletişim kanalları.

## 3. Kapsam dışı (plan §4.2)

Canlı veri (otobüs/trafik/hava/nöbetçi eczane/hastane sırası), e-Devlet'e kullanıcı adına
giriş, kullanıcı adına başvuru, ödeme, sağlık teşhisi, kesin hukuki görüş, otomatik acil
çağrı, konum takibi, runtime scraping, bulut LLM yedeği, OpenAI/Azure üzerinden inference.

## 4. Erişilebilirlik hedefi

**WCAG 2.2 Seviye AA** + seçili AAA iyileştirmeleri (44×44 hedef boyutu, mümkün olduğunda
7:1 kontrast, sade dil). "WCAG 2.2 AA uyumlu" ifadesi ancak plan §63 kabul kapısındaki tüm
maddeler PASS olduğunda kullanılacaktır. Erişilebilirlik overlay kullanılmaz (§29.1).

## 5. Offline tanımı (plan §8.2, §53)

- BUILD/UPDATE MODE: internet serbest, yalnız `scripts/` altında.
- OFFLINE RUNTIME MODE: `app/` içinde hiçbir dış ağ çağrısı bulunmaz
  (`requests`/`httpx`/`urllib`/`aiohttp`/`socket`). Embedding ve chat inference cihazda.
- Kabul: Wi-Fi kapalıyken uygulama açılır, modeller cache'ten yüklenir, 10 soru cevaplanır.

## 6. Model kararı (plan §11.2)

| Rol | Model | Durum |
|---|---|---|
| Embedding | `qwen3-embedding-0.6b` | Katalogda mevcut (495 MB, CPU), 2026-08-18 tarihinde indirildi |
| Chat | `qwen2.5-1.5b` | Plan §11.2'nin verdiği izinle değiştirildi (aşağıdaki ölçüm) |

**Chat modeli değişikliğinin gerekçesi (ölçüm, 2026-08-18).** Plan §11.2'nin başlangıç modeli
`qwen2.5-0.5b` ile Faz 1 konsol testi çalıştırıldı: retrieval doğru olmasına rağmen üretilen
Türkçe bozuktu ("Bolsuksa", "mühlimleri" gibi var olmayan kelimeler). Bu, plan §38 (bilişsel
erişilebilirlik) ve §74 (yanıt dil standardı) ile bağdaşmıyor. Aynı context ile
`qwen2.5-1.5b` akıcı ve doğru Türkçe üretti (13.7 s / 11.3 s). Temel RAG mantığı
değiştirilmedi; yalnız model alias'ı değişti.

Donanım: RTX 5050 Laptop, 4 GB VRAM — 7B+ modeller kapsam dışı.
Chat modeli değiştirilirse plan §11.2 uyarınca README'de açıkça belirtilir ve temel RAG
mantığı değiştirilmez.

## 7. Bilgi tabanı sürümü

`knowledge_version`: `2026-08-20` (İŞKUR kaynaklarının arşive eklendiği son build).
