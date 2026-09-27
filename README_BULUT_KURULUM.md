# Rumeli Tekel - Bulut Tabanlı Web Uygulaması (Her Yerden Erişim)

Bu sürüm, **telefondan, dükkandaki veya evdeki bilgisayardan, internet kafeden veya dünyanın herhangi bir yerindeki tarayıcıdan** kullanıcı adı ve şifrenizle giriş yaparak tüm tedarikçi borç ve alım kayıtlarınıza anında ulaşabileceğiniz **merkezi bulut web sitesi** mimarisidir.

---

### Varsayılan Giriş Bilgileri
* **Kullanıcı Adı:** `ugur`
* **Şifre:** `rumeli2026`
*(Giriş yaptıktan sonra sağ üstteki anahtar simgesine tıklayarak şifrenizi istediğiniz zaman değiştirebilirsiniz.)*

---

### 1. En Kolay & Tamamen Ücretsiz Canlıya Alma (Render.com - 3 Dakika)

Render.com, bu uygulamayı ömür boyu **ücretsiz** olarak bir web sitesi gibi çalıştırmanızı sağlar:

1. [render.com](https://render.com) adresine girip ücretsiz bir hesap açın (GitHub veya Google ile).
2. Bu ZIP içerisindeki dosyaları bir GitHub deposuna yükleyin (veya Render ekranında "New Web Service" seçin).
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. "Create Web Service" butonuna basın.
6. Yaklaşık 2 dakika içinde size özel canlı bir web adresi oluşturulur:  
   👉 **`https://rumeli-tekel-cari.onrender.com`**

Artık bu linki telefonunuzun ana ekranına ekleyebilir, internet kafeden veya evinizden kullanıcı adı ve şifrenizle doğrudan açabilirsiniz!

---

### 2. Kendi Sunucunuzda / Alan Adınızda Çalıştırma (Örn: cari.posetistan.com)

Eğer mevcut bir cPanel, Plesk veya VPS sunucunuz varsa:
* `cari.posetistan.com` şeklinde bir alt alan adı (subdomain) oluşturup Python uygulamasını (veya Docker konteynerini) çalıştırabilirsiniz.
* Paketteki `Dockerfile`, doğrudan Docker desteği sağlar.

---

### 3. Kendi Bilgisayarınızda Yerel Olarak Test Etme

1. Terminalde:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
2. Tarayıcınızda açın:
   `http://localhost:8000`
