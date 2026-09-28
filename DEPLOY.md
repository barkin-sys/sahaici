# 🌐 Saha İçi - Ücretsiz Canlı Web Yayını (Cloud Deployment Rehberi)

Bu platformu bilgisayarınız kapalıyken bile 7/24 internette çalışan ve herkesin girebileceği gerçek bir web sitesi haline getirmek için en kolay ve tamamen ücretsiz iki yöntem aşağıdadır:

---

## 🚀 1. Yöntem: Render.com ile Yayınlama (Önerilen - En Kolay)

1. **GitHub'a Yükleyin:**
   - [github.com](https://github.com) sitesine gidin ve **"New repository"** diyerek yeni bir repo açın (örn: `saha-ici`).
   - Proje klasöründeki dosyaları (static, server.py, football_engine.py, coupon_engine.py, requirements.txt, render.yaml, Procfile) GitHub'a yükleyin.

2. **Render'a Bağlayın:**
   - [render.com](https://render.com) adresine gidin ve **GitHub ile ücretsiz giriş yapın**.
   - Sağ üstteki **"New +"** butonuna tıklayıp **"Web Service"** seçin.
   - Oluşturduğunuz GitHub reposunu seçin.

3. **Otomatik Kurulum:**
   - Projedeki `render.yaml` ve `requirements.txt` dosyaları sayesinde tüm ayarlar otomatik algılanır:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **"Deploy Web Service"** butonuna tıklayın.

4. **Sonuç:**
   - 2-3 dakika içinde size özel ücretsiz bir HTTPS web adresi (örn: `https://saha-ici-xxxx.onrender.com`) verilir.
   - Artık telefonunuzdan, tabletinizden veya dilediğiniz her cihazdan bu linke tıklayarak analiz platformunu kullanabilirsiniz!

---

## 🤗 2. Yöntem: Hugging Face Spaces (Alternatif - 7/24 Kesintisiz)

1. [huggingface.co](https://huggingface.co) sitesine ücretsiz üye olun.
2. Sağ üstten profilinize tıklayıp **"New Space"** deyin.
3. Space SDK olarak **Docker** (Blank) seçin.
4. Proje klasöründeki tüm dosyaları (projedeki hazır `Dockerfile` dahil) Space'e yükleyin.
5. Hugging Face projeyi otomatik olarak Docker ile ayağa kaldırır ve size özel 7/24 kesintisiz çalışan bir web linki sağlar.

---

## 🔒 Şifreli Giriş & Güvenlik
- Telefondan veya bilgisayardan ilk kez girdiğinizde şifre ekranı açılır.
- **"Beni Hatırla"** seçeneği sayesinde aynı cihazda bir daha şifre girmek zorunda kalmazsınız.
- Şifreli güvenli erişim sayesinde yalnızca yetkili kullanıcılar platforma erişebilir.

---

## 📱 Evde / Aynı Wi-Fi'de Telefondan Anında Bağlanma
Bilgisayarınızda `baslat.bat` çalışırken:
1. Telefonunuzun aynı Wi-Fi ağına bağlı olduğundan emin olun.
2. Telefon tarayıcınızdan yerel ağ adresini açın.
3. Şifrenizi girip **"Giriş Yap"** butonuna dokunun!
