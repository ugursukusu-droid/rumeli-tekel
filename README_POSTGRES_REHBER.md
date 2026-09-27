# Rumeli Tekel - PostgreSQL Bulut Veritabanı Kurulum Rehberi

Render'ın ücretsiz planında verilerin silinmesini engellemek için **tamamen ücretsiz ve kalıcı** bir PostgreSQL veritabanı (Neon DB veya Supabase) kullanıyoruz.

---

### YÖNTEM 1: Neon.tech (En Kolay & En Hızlı - 1 Dakika)

Neon, Render ile kusursuz çalışan, kredi kartı istemeyen ücretsiz bir PostgreSQL servisidir:

1. **[neon.tech](https://neon.tech)** adresine gidin.
2. "Sign in with Google" diyerek Google hesabınızla tek tıkla giriş yapın.
3. Proje Adı olarak: `rumeli-tekel-db` yazın ve **"Create project"** butonuna basın.
4. Karşınıza çıkan ekrandan **"Connection string"** başlığı altındaki linki kopyalayın.
   *(Örnek: `postgresql://neondb_owner:xyz123@ep-cool-fog-123456.eu-central-1.aws.neon.tech/neondb?sslmode=require`)*

---

### YÖNTEM 2: Supabase (Alternatif)

1. **[supabase.com](https://supabase.com)** adresine gidin ve ücretsiz giriş yapın.
2. "New Project" butonuna basıp bir veritabanı şifresi belirleyin.
3. **Project Settings > Database > Connection String > URI** kısmındaki linki kopyalayın.

---

### RENDER.COM'A `DATABASE_URL` EKLEME ADIMLARI

1. **[dashboard.render.com](https://dashboard.render.com)** adresine girin.
2. Yayındaki Web Service'inize (örn: `rumeli-tekel`) tıklayın.
3. Sol menüdeki **"Environment"** sekmesine tıklayın.
4. **"Add Environment Variable"** butonuna basın:
   * **Key (Anahtar):** `DATABASE_URL`
   * **Value (Değer):** *(Neon veya Supabase'den kopyaladığınız linki buraya yapıştırın)*
5. **"Save Changes"** butonuna basın.

Render birkaç saniye içinde uygulamayı otomatik olarak yeniden başlatır ve tüm veritabanı tablolarını kalıcı bulut sunucunuzda anında oluşturur. Artık Render uyku moduna geçse veya yeniden başlasa bile hiçbir veriniz ASLA silinmez!
