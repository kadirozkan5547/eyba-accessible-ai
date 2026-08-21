# GitHub Yayın Ayarları

## Önerilen depo bilgileri

- **Depo adı:** `eyba-accessible-ai`
- **Görünürlük:** Public
- **Açıklama:** `Microsoft AI Innovators Summer Internship kapsamında geliştirilen, Foundry Local tabanlı erişilebilir Türkçe RAG staj projesi.`
- **Website:** İlk yayın sırasında boş bırakılabilir; uygulama yerel çalışır.
- **Lisans:** MIT

Önerilen topics:

```text
rag accessibility turkish local-ai foundry-local fastapi offline-first
assistive-technology responsible-ai microsoft-internship
```

## İlk yayın kontrol listesi

- [ ] GitHub hesabında e-posta gizliliğini etkinleştir.
- [ ] Commit e-postasını GitHub `noreply` adresiyle değiştirip geçmiş için
      kişisel e-posta kararını ver.
- [ ] Public ve boş bir `eyba-accessible-ai` deposu oluştur.
- [ ] GitHub'ın otomatik README, `.gitignore` veya lisans oluşturma
      seçeneklerini işaretleme; bu dosyalar projede hazır.
- [ ] Uzak depoyu `origin` adıyla ekle ve `main` dalını gönder.
- [ ] Actions sekmesinde `CI` iş akışının geçtiğini doğrula.
- [ ] **Settings → General → Features** altında Issues'ı etkinleştir.
- [ ] **Settings → Security** altında private vulnerability reporting'i aç.
- [ ] `main` için pull request ve başarılı CI isteyen branch protection kuralı ekle.
- [ ] About bölümüne açıklamayı ve topics listesini ekle.

## Yayın komutları

GitHub'da boş depo oluşturulduktan sonra:

```powershell
git remote add origin https://github.com/kadirozkan5547/eyba-accessible-ai.git
git push -u origin main
```

Kişisel e-postanız mevcut commit geçmişinde yer alıyorsa ilk push'tan önce
geçmişi düzenlemek daha güvenlidir. Bunun için GitHub hesabındaki doğrulanmış
`noreply` adresi gereklidir; adres bilinmeden otomatik değiştirilmemelidir.
