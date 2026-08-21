# Katkıda Bulunma Rehberi

EYBA'ya katkı sağladığınız için teşekkürler. Projenin temel ilkeleri
erişilebilirlik, çevrimdışı çalışma, kaynak gösterme ve doğrulanabilirliktir.

## Geliştirme ortamı

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Değişiklik yapmadan önce mevcut testleri çalıştırın:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\validate_knowledge.py
```

## Değişiklik gönderme

1. Kapsamı küçük ve tek amaçlı tutun.
2. Davranış değişikliklerine test ekleyin.
3. Arayüz değişikliklerinde klavye, odak görünürlüğü, metin büyütme ve ekran
   okuyucu durumlarını kontrol edin.
4. Bilgi tabanı değişikliklerinde resmî URL'yi, erişim tarihini ve SHA-256
   doğrulamasını güncelleyin.
5. Uygulamanın çalışma zamanında harici ağ isteği yapmadığını koruyun.
6. Pull request şablonundaki doğrulama listesini doldurun.

## İçerik kuralları

- Yalnızca doğrulanabilir ve tercihen birincil/resmî kaynak kullanın.
- Kaynaksız telefon numarası, ücret, süre veya başvuru kanalı eklemeyin.
- Sağlık veya hukuk alanında kesin hüküm veren metinler eklemeyin.
- Kişisel veri, gizli anahtar, model ağırlığı veya kullanıcı konuşması commit
  etmeyin.

Katkı göndererek katkınızın projenin [MIT Lisansı](LICENSE) altında
yayımlanmasını kabul etmiş olursunuz.

