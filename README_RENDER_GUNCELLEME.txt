========================================================================
   RUMELİ TEKEL - RENDER.COM & BULUT İÇİN GÜNCELLENMİŞ DOSYALAR
========================================================================

Tüm API istekleri (fetch çağrıları, Excel indirme, oturum işlemleri)
"http://localhost:8000" gibi statik adreslerden tamamen arındırılarak
%100 RELATIVE PATH (göreceli yol, örn: "/api/dashboard", "/api/suppliers")
olacak şekilde güncellenmiştir.

Bu sayede:
1. Render.com üzerindeki canlı sitenizde (örn: https://rumeli-tekel.onrender.com)
   istekler otomatik olarak kendi sunucunuza gider. "ERR_CONNECTION_REFUSED"
   veya "Failed to fetch" hatası ALINMAZ.
2. Butonlara ("İşlem Ekle", "Tedarikçi Ekle", "Ekstre", "Excel") tıklandığında
   tüm işlemler anında merkezi veritabanında çalışır.

------------------------------------------------------------------------
RENDER'DA GÜNCELLEME NASIL YAPILIR?
------------------------------------------------------------------------
Eğer GitHub üzerinden bağladıysanız:
- Deponuzdaki "index.html" ve "main.py" dosyalarını bu pakettekilerle değiştirip
  commit & push yapınız. Render 1-2 dakika içinde otomatik günceller.

Eğer manuel yüklediyseniz:
- Bu paketteki dosyaları Render Web Service'inize yüklemeniz yeterlidir.

Giriş Bilgileri:
- Kullanıcı Adı: ugur
- Şifre: rumeli2026
========================================================================
