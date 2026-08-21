# Erişilebilir Yerel Bilgi Asistanı (EYBA)

EYBA, Türkiye'deki engelli hakları ve kamu hizmetleri hakkında resmî kaynaklara
dayalı cevaplar veren, cihaz üzerinde çalışan bir RAG asistanıdır. Çalışma
zamanında dış ağa bağlanmaz; embedding ve cevap üretimi Microsoft Foundry Local
üzerinden yerel olarak yapılır.

## Güncel durum

- Uygulama sürümü: `1.1.1`
- 15 resmî kaynak, ham arşiv ve SHA-256 doğrulaması
- 47 metadata'lı chunk, 1024 boyutlu yerel embedding indexi
- Retrieval ölçümü: Top-1 `%86,7`, Top-3 `%100`
- Yetersiz bağlam eşiği: `0.39`
- FastAPI tabanlı Türkçe ve klavye erişilebilir web arayüzü
- 6 kullanım senaryosu, karakter sayacı ve yanıt kopyalama içeren yönlendirmeli arayüz
- Ana konu kanıtı, uydurma iletişim kanalı/sayı engeli ve doğrulanmış olgu yedeği
- Bilgi tabanı sürümü: `2026-08-20`

## Modeller

| Rol | Foundry Local alias'ı |
|---|---|
| Embedding | `qwen3-embedding-0.6b` |
| Chat | `qwen2.5-1.5b` |

Ana plandaki başlangıç chat modeli `qwen2.5-0.5b` idi. Faz 1 ölçümünde bozuk
Türkçe ürettiği için, temel RAG mantığı değiştirilmeden `qwen2.5-1.5b` modeline
geçildi. Ayrıntılı gerekçe [PROJECT_SPEC.md](PROJECT_SPEC.md) §6'dadır.

## Kurulum

Ön koşullar: Windows 10/11, Python 3.10+ ve Microsoft Foundry Local.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\prepare_models.py
```

Son komut build/update modunda bir kez internet kullanarak modelleri indirir.
Sonraki uygulama çalışmaları çevrimdışıdır.

## Bilgi tabanını oluşturma

Resmî kaynakları güncellemek isterseniz yalnız `scripts/` altındaki build
komutlarını internet bağlıyken çalıştırın:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_sources.py
.\.venv\Scripts\python.exe scripts\normalize_sources.py
.\.venv\Scripts\python.exe scripts\build_chunks.py
.\.venv\Scripts\python.exe scripts\build_index.py
.\.venv\Scripts\python.exe scripts\validate_knowledge.py
```

Retrieval ölçümü:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
```

## Çalıştırma

```powershell
.\baslat.bat
```

Ardından tarayıcıda `http://127.0.0.1:8765` adresini açın. Alternatif komut:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

## Test

Ek test paketi kurmadan çalışır:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\validate_knowledge.py
```

Gerçek yerel modellerle 10 soruluk kabul turu:

```powershell
.\.venv\Scripts\python.exe scripts\run_offline_acceptance.py --network-condition restricted
```

Fiziksel Wi-Fi kapalı manuel kabulte `restricted` yerine `wifi-off-manual`
kullanın. Ayrıntılı erişilebilirlik matrisi [docs/KABUL_MATRISI.md](docs/KABUL_MATRISI.md)
dosyasındadır.

## Sürüm paketi

```powershell
.\.venv\Scripts\python.exe scripts\package_release.py
```

Komut `dist/eyba-1.1.1.zip` paketini ve yanında SHA-256 doğrulama dosyasını
üretir. Foundry Local model ağırlıkları pakete eklenmez; hedef bilgisayarda
`scripts/prepare_models.py` ile bir kez hazırlanmalıdır. Demo akışı
[docs/DEMO_SENARYOSU.md](docs/DEMO_SENARYOSU.md) dosyasındadır.

## Güvenlik ve gizlilik

- `app/` altında `requests`, `httpx`, `urllib`, `aiohttp` veya `socket` çağrısı yoktur.
- Soru ve konuşmalar diske kaydedilmez.
- Canlı veri, kullanıcı adına başvuru, teşhis ve kesin hukuki görüş kapsam dışıdır.
- Kaynak bulunamazsa model çağrılmadan sabit ve sade bir ret yanıtı verilir.

Kalan işler ve ilerleme kaydı için [DEVAM_DURUMU.md](DEVAM_DURUMU.md) dosyasına bakın.
