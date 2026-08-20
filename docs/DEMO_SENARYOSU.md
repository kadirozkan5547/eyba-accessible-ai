# EYBA Demo Senaryosu

## Hazırlık

1. Microsoft Foundry Local'ın kurulu ve iki modelin önbellekte olduğunu doğrulayın.
2. İnterneti kapatın veya makineyi dış ağ erişimi olmayan bir profile alın.
3. Proje klasöründe `baslat.bat` dosyasını çalıştırın.
4. `http://127.0.0.1:8765` adresini açın.

## Beş dakikalık akış

1. **Offline ve gizlilik:** Alt bilgide uygulamanın dış ağa bağlanmadığını gösterin.
2. **Resmî yanıt:** “Afet çantasında hangi malzemeler bulunmalı?” sorusunu sorun.
3. **Kaynak görünürlüğü:** Yanıtın altındaki AFAD kaynak kartını gösterin.
4. **Haklar:** “İŞKUR'a engelli olarak kayıt olmak için rapor oranı kaç olmalı?” sorusunu sorun.
5. **Kapsam sınırı:** “Yarın İstanbul'da hava nasıl olacak?” sorusuyla sabit ret davranışını gösterin.
6. **Erişilebilirlik:** Fare kullanmadan `Tab` ile forma ilerleyin; odak halkasını ve “Ana içeriğe geç” bağlantısını gösterin.
7. **Gizlilik:** “Temizle” düğmesinin soruyu ve yanıtı kaldırdığını gösterin.

## Beklenen sonuçlar

- Kapsam içi sorular kısa Türkçe yanıt ve en az bir resmî kaynak kartı üretir.
- Kapsam dışı soru model çağrısı yapılmadan reddedilir.
- Soru veya konuşma diske yazılmaz.
- İnternet kapalıyken uygulama çalışmaya devam eder.

## Demo öncesi hızlı doğrulama

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\validate_knowledge.py
.\.venv\Scripts\python.exe scripts\run_offline_acceptance.py --network-condition wifi-off-manual
```
