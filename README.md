<div align="center">

# EYBA — Erişilebilir Yerel Bilgi Asistanı

**Türkiye'deki engelli hakları ve kamu hizmetleri için, cihaz üzerinde çalışan, kaynak gösteren ve internet gerektirmeyen Türkçe RAG asistanı.**

[![CI](https://github.com/kadirozkan5547/eyba-accessible-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/kadirozkan5547/eyba-accessible-ai/actions/workflows/ci.yml)
[![Sürüm](https://img.shields.io/badge/s%C3%BCr%C3%BCm-1.1.1-informational)](VERSION)
[![Lisans: MIT](https://img.shields.io/badge/lisans-MIT-green)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Foundry Local](https://img.shields.io/badge/runtime-Foundry%20Local-0078D4)](https://github.com/microsoft/Foundry-Local)
[![Çalışma zamanı: çevrimdışı](https://img.shields.io/badge/%C3%A7al%C4%B1%C5%9Fma%20zaman%C4%B1-%C3%A7evrimd%C4%B1%C5%9F%C4%B1-lightgrey)](#güvenlik-gizlilik-ve-sınırlar)
[![Erişilebilirlik hedefi: WCAG 2.2 AA](https://img.shields.io/badge/eri%C5%9Filebilirlik-WCAG%202.2%20AA%20hedefli-orange)](docs/KABUL_MATRISI.md)

</div>

---

## İçindekiler

- [Genel bakış](#genel-bakış)
- [Microsoft staj projesi](#microsoft-staj-projesi)
- [Neden EYBA?](#neden-eyba)
- [Güncel kapsam ve ölçümler](#güncel-kapsam-ve-ölçümler)
- [Mimari](#mimari)
- [Proje yapısı](#proje-yapısı)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Çalıştırma](#çalıştırma)
- [HTTP API](#http-api)
- [Test ve doğrulama](#test-ve-doğrulama)
- [Bilgi tabanını güncelleme](#bilgi-tabanını-güncelleme)
- [Sürüm paketi](#sürüm-paketi)
- [Erişilebilirlik](#erişilebilirlik)
- [Güvenlik, gizlilik ve sınırlar](#güvenlik-gizlilik-ve-sınırlar)
- [Veri kaynakları](#veri-kaynakları)
- [Katkıda bulunma](#katkıda-bulunma)
- [Lisans](#lisans)
- [English summary](#english-summary)

## Genel bakış

EYBA, engelli bireylerin Türkiye'deki temel haklar, kamu hizmetleri ve pilot
şehirdeki yerel hizmetler hakkında **internet olmadan**, **resmî kaynaklara
dayalı** ve **kaynak gösteren** bilgi almasını sağlar. Embedding ve yanıt
üretimi Microsoft Foundry Local üzerinden cihazda gerçekleştirilir; uygulama
kodu çalışma zamanında hiçbir dış ağ isteği yapmaz.

Sorular kayıt altına alınmaz, bulut LLM yedeği yoktur ve bağlam yetersizse
model tahmin yürütmek yerine açık bir yetersiz-bilgi yanıtı döner.

> **Proje durumu:** Aktif geliştirme — sürüm `1.1.1`, bilgi tabanı sürümü `2026-08-20`

## Microsoft staj projesi

Bu proje, **Abdülkadir Özkan** tarafından **Microsoft AI Innovators Summer
Internship Program** kapsamında, **AI Innovators Summer Intern** pozisyonunda
staj projesi olarak geliştirilmiştir.

| Bilgi | Açıklama |
|---|---|
| Kurum | Microsoft |
| Program | Microsoft AI Innovators Summer Internship Program |
| Pozisyon | AI Innovators Summer Intern |
| Geliştirici | [Abdülkadir Özkan](https://www.linkedin.com/in/mabdulkadirozkan/) |
| Dönem | Yaz 2026 |

## Neden EYBA?

- **Kaynaklı yanıt.** Her yanıt resmî kaynak kartlarıyla birlikte sunulur; kaynak
  kanıtı olmayan cümle üretilmez.
- **Gizlilik.** Kullanıcı soruları ve konuşmalar diske kaydedilmez.
- **Çevrimdışı.** İlk model hazırlığından sonra internet bağlantısı gerekmez.
- **Erişilebilirlik.** Klavye, ekran okuyucu, yüksek kontrast ve büyütülmüş metin
  gözetilerek tasarlanmış Türkçe web arayüzü; erişilebilirlik overlay kullanılmaz.
- **Dürüst reddetme.** Kapsam dışı sorularda benzerlik eşiği altında kalan bağlam
  reddedilir, uydurma yanıt üretilmez.

## Güncel kapsam ve ölçümler

| Ölçüt | Değer |
|---|---|
| Resmî kaynak sayısı | 15 (SHA-256 ile doğrulanmış ham arşiv) |
| Bilgi parçası (chunk) | 47, metadata'lı |
| Embedding boyutu | 1024 |
| Retrieval Top-1 doğruluğu | %86,7 |
| Retrieval Top-3 doğruluğu | %100 |
| Benzerlik eşiği | `min_similarity = 0.39` |
| Otomatik test | 34 test, `unittest` ile ağsız |
| Çevrimdışı kabul turu | 10/10 PASS (ağ kısıtlı ortam, gerçek yerel modeller) |
| Kullanım senaryosu | 6 yönlendirmeli senaryo |

Retrieval ölçüm çıktısı depoda tutulur:
[`tests/rag/retrieval_report.json`](tests/rag/retrieval_report.json). Çevrimdışı
kabul raporu makineye özgü olduğu için depoya alınmaz; `scripts/run_offline_acceptance.py`
çalıştırıldığında `tests/acceptance/` altında yerel olarak üretilir.

**Kapsam.** Ulusal: engelli kimlik kartı, engelli hakları, sosyal hizmetler, evde
bakım, engelli sağlık kurulu raporu, yetkili sağlık kuruluşları, İŞKUR engelli
kaydı ve istihdamı, EKPSS, erişilebilir ulaşım, afet hazırlığı, dijital
erişilebilirlik. Yerel pilot şehir: **Şanlıurfa**.

**Kapsam dışı.** Canlı veri, e-Devlet'e kullanıcı adına giriş, kullanıcı adına
başvuru, ödeme, sağlık teşhisi, kesin hukuki görüş, otomatik acil çağrı, konum
takibi, runtime scraping, bulut LLM yedeği. Ayrıntı: [PROJECT_SPEC.md](PROJECT_SPEC.md).

## Mimari

```text
Kullanıcı sorusu
      │
      ▼
Yerel embedding → Benzerlik araması → Kaynaklı bağlam
                                           │
                                           ▼
                                  Yerel dil modeli
                                           │
                                           ▼
                                Yanıt + kaynak kartları
```

| Rol | Foundry Local modeli |
|---|---|
| Embedding | `qwen3-embedding-0.6b` |
| Yanıt üretimi | `qwen2.5-1.5b` |

Başlangıç planındaki `qwen2.5-0.5b`, değerlendirmede yeterli Türkçe kalitesi
sağlamadığı için değiştirilmiştir. `qwen3-1.7b` de denenmiş; tekrar, yazım kusuru
ve zaman aşımı nedeniyle üretim için reddedilmiştir. Teknik gerekçe
[PROJECT_SPEC.md](PROJECT_SPEC.md) dosyasının 6. bölümündedir.

Proje iki moda ayrılmıştır: **BUILD/UPDATE MODE** (yalnızca `scripts/` altında,
internet serbest) ve **OFFLINE RUNTIME MODE** (`app/` altında hiçbir dış ağ
çağrısı yok). Bu ayrım otomatik testle denetlenir.

## Proje yapısı

```text
app/                 Çevrimdışı çalışma zamanı (FastAPI)
  main.py            HTTP uçları ve arayüz
  settings.py        Merkezî ayarlar
  rag/               Embedding, retrieval, Foundry Local istemcisi, şemalar
  services/          RAG servis katmanı ve kaynak kartı sözleşmesi
  templates/         Erişilebilir Türkçe arayüz
knowledge/           Bilgi tabanı
  manifest/          Kaynak listesi ve erişim tarihleri
  raw/               Ham HTML arşivi + SHA-256
  normalized/        Frontmatter'lı Markdown
  chunks/            Metadata'lı JSONL parçalar
  index/             Embedding indeksi ve index metadata
scripts/             BUILD/UPDATE araçları, değerlendirme, paketleme
tests/               34 otomatik test ve retrieval ölçüm raporu
docs/                Kabul matrisi ve demo senaryosu
```

## Gereksinimler

- Windows 10 veya Windows 11
- Python 3.10 veya daha yeni bir sürüm
- [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local)

Model ağırlıkları depoya dahil değildir. İlk model hazırlığı internet bağlantısı
gerektirir; sonraki uygulama çalışmaları çevrimdışıdır.

## Kurulum

```powershell
git clone https://github.com/kadirozkan5547/eyba-accessible-ai.git
cd eyba-accessible-ai
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\prepare_models.py
```

`prepare_models.py`, gerekli Foundry Local modellerini indirir ve yükler; bu adım
tek seferliktir ve internet bağlantısı ister.

## Çalıştırma

```powershell
.\baslat.bat
```

Ardından [http://127.0.0.1:8765](http://127.0.0.1:8765) adresini açın.

Alternatif komut:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

## HTTP API

Uygulama yalnızca `127.0.0.1` üzerinde dinler.

| Uç | Yöntem | Açıklama |
|---|---|---|
| `/` | GET | Erişilebilir Türkçe web arayüzü |
| `/api/health` | GET | Model, indeks ve bilgi tabanı hazırlık durumu |
| `/api/ask` | POST | Soruyu yanıtlar; yanıt ve kaynak kartlarını döner |

```powershell
curl.exe -X POST http://127.0.0.1:8765/api/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Afet çantasında hangi malzemeler bulunmalı?\"}"
```

Hazırlık durumunu doğrulamak için:

```powershell
curl.exe http://127.0.0.1:8765/api/health
```

## Test ve doğrulama

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\validate_knowledge.py
```

Testler dış bağımlılık ve ağ gerektirmez; `main` dalına yapılan her push ve pull
request'te GitHub Actions üzerinde de çalışır.

Gerçek yerel modellerle çevrimdışı kabul turu:

```powershell
.\.venv\Scripts\python.exe scripts\run_offline_acceptance.py --network-condition restricted
```

Fiziksel Wi-Fi kapalı manuel kabul için `restricted` yerine `wifi-off-manual`
kullanın.

## Bilgi tabanını güncelleme

Aşağıdaki komutlar **yalnızca** resmî kaynakları güncellerken ve internet
bağlantısı varken çalıştırılmalıdır:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_sources.py
.\.venv\Scripts\python.exe scripts\normalize_sources.py
.\.venv\Scripts\python.exe scripts\build_chunks.py
.\.venv\Scripts\python.exe scripts\build_index.py
.\.venv\Scripts\python.exe scripts\validate_knowledge.py
```

Retrieval değerlendirmesi:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
```

## Sürüm paketi

```powershell
.\.venv\Scripts\python.exe scripts\package_release.py
```

Komut `dist/eyba-1.1.1.zip` paketini ve SHA-256 doğrulama dosyasını üretir.
Foundry Local model ağırlıkları pakete eklenmez. Demo akışı için
[docs/DEMO_SENARYOSU.md](docs/DEMO_SENARYOSU.md) dosyasına bakın.

## Erişilebilirlik

Hedef: **WCAG 2.2 Seviye AA** ve seçili AAA iyileştirmeleri (44×44 hedef boyutu,
mümkün olduğunda 7:1 kontrast, sade dil). Kontrast, hedef boyutu ve 320 CSS px
yeniden akış otomatik olarak doğrulanır.

"WCAG 2.2 AA uyumlu" ifadesi, kabul matrisindeki **tüm** maddeler — ekran okuyucu
(NVDA), yalnız klavye, %200/%400 zoom ve Windows Yüksek Karşıtlık manuel turları
dahil — PASS olmadan kullanılmayacaktır. Güncel durum:
[docs/KABUL_MATRISI.md](docs/KABUL_MATRISI.md).

## Güvenlik, gizlilik ve sınırlar

- Soru ve konuşmalar kalıcı olarak saklanmaz.
- Uygulama kodu çalışma zamanında harici ağ isteği yapmaz; bu statik testle denetlenir.
- Proje teşhis, kesin hukuki görüş veya kullanıcı adına resmî başvuru sunmaz.
- Sağlık, hukuk ve kamu hizmetleriyle ilgili kararlar güncel resmî kaynaktan
  doğrulanmalıdır; hak ve ödeme tutarları yıl içinde değişebilir.
- Güvenlik açığı bildirmek için [SECURITY.md](SECURITY.md) dosyasını izleyin.

## Veri kaynakları

Kaynak listesi ve erişim tarihleri
[knowledge/manifest/sources.yaml](knowledge/manifest/sources.yaml) dosyasındadır.
Resmî kurumlara ait arşiv ve türetilmiş içerikler proje kodunun MIT lisansına
dahil değildir. Ayrıntılar için [NOTICE.md](NOTICE.md) dosyasına bakın.

## Katkıda bulunma

Katkılar memnuniyetle karşılanır. Başlamadan önce
[CONTRIBUTING.md](CONTRIBUTING.md) belgesini okuyun. Özellikle bilgi tabanı
değişikliklerinde kaynak, erişim tarihi ve doğrulama çıktısı eklenmelidir.

## Lisans

Kaynak kodu MIT Lisansı ile sunulur. Bkz. [LICENSE](LICENSE). Üçüncü taraf veri
ve içeriklerin kendi kullanım koşulları geçerlidir; bkz. [NOTICE.md](NOTICE.md).

## English summary

**EYBA (Accessible Local Knowledge Assistant)** is an offline, on-device Turkish
RAG assistant that answers questions about disability rights and public services
in Türkiye, grounded in 15 official government sources with visible citations.

Embedding and generation run locally through **Microsoft Foundry Local**
(`qwen3-embedding-0.6b` and `qwen2.5-1.5b`); the runtime makes no external
network calls and stores no user questions. Retrieval accuracy is 86.7% Top-1 and
100% Top-3 over a 20-question evaluation set, and the FastAPI web interface is
built against **WCAG 2.2 Level AA** as its target.

Developed by Abdülkadir Özkan as an internship project for the Microsoft AI
Innovators Summer Internship Program (Summer 2026). Code is MIT licensed; the
archived official-source content is not — see [NOTICE.md](NOTICE.md).
