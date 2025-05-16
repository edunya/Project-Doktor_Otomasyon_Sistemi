# 🩺 Doktor Otomasyon Sistemi

Bu proje, hastaların çevrim içi ortamda randevu almasını ve doktorların bu randevuları yönetmesini sağlayan bir **web tabanlı otomasyon sistemi**dir. Flask framework'ü ve MySQL veritabanı kullanılarak geliştirilmiştir.

---

## 🔧 Özellikler

### 👤 Hasta Paneli

* Kayıt Ol / Giriş Yap
* Randevu Al (doktor listesinden seçimli)
* Randevu İptal Et (muayene yapılmamışsa)
* Muayene Geçmişini Görüntüle

### 🩺 Doktor Paneli

* Giriş Yap (email & şifre)
* Randevularını Görüntüle (sadece aktif olanlar)
* Muayene Kaydı Gir (teşhis, ilaç, not)
* Yapılan Muayeneleri Listele

---

## 🧱 Kullanılan Teknolojiler

* Python 3 & Flask
* MySQL 8 & PyMySQL
* HTML5 / CSS3
* Visual Studio Code / PyCharm

---

## 🗂️ Klasör Yapısı

```
proje/
├── app.py                # Flask ana uygulama
├── templates/            # HTML şablon dosyaları
│   ├── hasta_*.html      
│   ├── doktor_*.html     
│   └── ana_menu.html
├── static/
│   └── style.css         # Sayfa stilleri
├── sorgular.sql          # Veritabanı oluşturma scripti
└── README.md
```

---

## 🧠 Veritabanı Yapısı (Temel Tablolar)

* `Hasta(HastaID, Ad, Soyad, TC, Telefon, DogumTarihi, Sifre)`
* `Doktor(DoktorID, Ad, Soyad, Email, Sifre, BransID)`
* `Randevu(RandevuID, HastaID, DoktorID, Tarih, Sikayet, MuayeneDurumu)`
* `Muayene(MuayeneID, RandevuID, Teshis, Ilac, Notlar)`
* `Brans(BransID, Ad)`

Ek olarak:

* `AktifRandevular` adında bir **VIEW**
* `trg_hasta_sil` adında bir **TRIGGER**
* `idx_randevu_tarih` adında bir **INDEX** tanımlanmıştır

---

## 🚀 Projeyi Çalıştırmak

1. Veritabanını oluştur:

   ```sql
   mysql -u root -p < sorgular.sql
   ```
2. `app.py` dosyasındaki veritabanı bağlantısını kendi ayarlarına göre düzenle.
3. Aşağıdaki komutla Flask uygulamasını başlat:

   ```bash
   python app.py
   ```
4. Tarayıcıda `http://localhost:5000` adresini aç.

---

## 👥 Katkıda Bulunanlar

* Tüm ekip üyeleri yazılım geliştirme, test, veritabanı modelleme ve belge hazırlama görevlerini ortaklaşa üstlenmiştir.

---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir. Telif hakkı yoktur.
