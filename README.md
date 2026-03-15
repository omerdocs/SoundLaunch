<div align="center">

<img src="static/icon.svg" width="80" height="80" alt="SoundLaunch">

# SoundLaunch

**Soundpad için web tabanlı launchpad.**  
Telefonunu kumandaya çevir. Tuş kombinasyonu yok, kablo yok, zahmetsiz.

[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-3b82f6?style=flat-square)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10+-f59e0b?style=flat-square)](https://python.org)
[![Soundpad](https://img.shields.io/badge/requires-Soundpad-ef4444?style=flat-square)](https://store.steampowered.com/app/629520/Soundpad/)

</div>

---

## Ne işe yarar?

Oyun oynarken ya da Discord'da arkadaşlarınla sesli sohbet ederken ses efekti çalmak istiyorsun — ama küçük klavyende tuş kombinasyonları için yer yok, ya da her seferinde Soundpad penceresine geçmek istemiyorsun.

SoundLaunch bu sorunu çözüyor. Bilgisayarında küçük bir sunucu açıyor, telefonda tarayıcıdan bu sunucuya bağlanıyorsun. Telefonun artık senin launchpad'in — seslere tek dokunuşla erişiyorsun.

---

## Özellikler

| | |
|---|---|
| 🎵 **Tek dokunuş** | Soundpad Named Pipe API ile doğrudan iletişim — tuş kombinasyonu yok |
| 📱 **Telefon desteği** | PWA olarak ana ekrana eklenebilir, uygulama gibi çalışır |
| 🖤 **OLED uyumlu** | Tam siyah arka plan, pil tüketimi minimum |
| 🎨 **3 tema** | OLED / Koyu / Açık — tercihine göre |
| 📂 **Kategoriler** | Sesleri grupla, hızlıca bul |
| ↕️ **Sürükle & bırak** | Sesleri istediğin sıraya diz |
| ⚡ **Spam çalma** | Bir sesi ayarladığın aralık ve tekrarla art arda çal |
| 🖼️ **Görseller & renkler** | Her sese özel görsel veya renk etiketi |
| ⭐ **Favoriler** | İşaretle, en çok çalınanlar otomatik üste gelir |
| 🔍 **Canlı arama** | Sesler arasında anında filtrele |
| ⚠️ **Silinmiş ses tespiti** | Soundpad'den silinen sesler otomatik "Kullanılamaz" olur |
| 📳 **Haptic feedback** | Dokunuşlarda titreşim (mobil) |
| 👆 **Kategori swipe** | Kategoriler arası parmakla kaydır |

---

## Kurulum

### ✅ Yol 1 — .exe ile (Önerilen)

Python bilmene gerek yok. Sadece indir ve çalıştır.

1. [**Releases**](../../releases) sayfasından `SoundLaunch.exe` dosyasını indir
2. İstediğin bir klasöre koy — örneğin `C:\SoundLaunch\`
3. `SoundLaunch.exe`'ye çift tıkla
4. Açılan penceredeki adresi telefonunda tarayıcıya yaz

> **Gereksinimler:**
> - Windows 10 veya 11
> - [Soundpad](https://store.steampowered.com/app/629520/Soundpad/) açık olmalı
> - Bilgisayar ve telefon aynı Wi-Fi ağında olmalı

---

### 🐍 Yol 2 — Python ile (Geliştirici)

```bash
# Bağımlılıkları yükle
pip install fastapi uvicorn pywin32 python-multipart

# Sunucuyu başlat
python server.py
```

Tarayıcıda aç: `http://[BİLGİSAYAR_IP]:7878`

IP adresini öğrenmek için terminale `ipconfig` yaz → **IPv4 Address** satırı.

---

### 🔨 .exe Kendin Derlemek İstersen

```bash
# Tüm bağımlılıkları ve PyInstaller'ı yükler, derler
build.bat
```

`dist/SoundLaunch.exe` oluşur. Yaklaşık 2–3 dakika sürer.

---

## Kullanım

### İlk Kurulum

1. **SoundLaunch.exe**'yi başlat — pencere açılır, IP adresi gösterilir
2. Soundpad'de seslerini ekle (zaten ekliyse sonraki adıma geç)
3. Telefonunda tarayıcıyı aç, adresi yaz
4. **+** butonuna bas → Soundpad listesi otomatik yüklenir → sesleri seç → **Ekle**

### Ses Ekleme

`+` butonuna bas. Soundpad'deki tüm sesler otomatik listelenir. İstediğin sesleri işaretle, kategori seç, **"X Sesi Ekle"**'ye bas.

### Sıralama Değiştirme

Header'daki **✦** butonuna bas → düzenleme modu açılır → kartlar sallanmaya başlar → sürükle & bırak.

### Kısayol Menüsü

Herhangi bir sese **uzun bas** (mobil) veya **sağ tıkla** (masaüstü) → Oynat / Spam Çal / Favoriye Ekle / Düzenle / Sil

### Soundpad'den Ses Silinirse

Ayarlar → Drawer menü → **"Silinmiş Sesleri Kontrol Et"** — ya da sunucu her açıldığında otomatik kontrol eder. Silinmiş sesler "Kullanılamaz" etiketiyle en alta iner.

---

## Ekran Görüntüleri

> *(Releases sayfasına eklenecek)*

---

## Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| Backend | Python 3.10+ · FastAPI · Uvicorn |
| Frontend | HTML · CSS · Vanilla JS |
| Soundpad API | Windows Named Pipe — `\\.\pipe\sp_remote_control` |
| Launcher GUI | Tkinter |
| Paketleme | PyInstaller |

### Soundpad API Hakkında

SoundLaunch, Soundpad ile Windows **Named Pipe** protokolü üzerinden iletişim kurar. Bu sayede:
- Hiçbir tuş simülasyonu yapılmaz — oyunlar etkilenmez
- Soundpad'in kendi ses motorunu kullanır — kalite ve ayarlar korunur
- Ekstra Soundpad ayarı gerekmez — Named Pipe varsayılan olarak açıktır

### Dosya Yapısı

```
soundpad-launcher/
├── server.py          # FastAPI backend — Soundpad API iletişimi
├── launcher.py        # .exe launcher — GUI + server thread
├── launcher.spec      # PyInstaller derleme ayarları
├── build.bat          # Tek tıkla .exe derleme
├── requirements.txt   # Python bağımlılıkları
└── static/
    ├── index.html     # Web arayüzü (tek dosya)
    ├── icon.png       # Uygulama ikonu
    └── manifest.json  # PWA manifest
```

---

## Sık Sorulan Sorular

**Telefon bağlanamıyor?**  
→ Bilgisayar ve telefon aynı Wi-Fi'da mı? Windows Güvenlik Duvarı port 7878'i engelliyor olabilir. Güvenlik duvarında `SoundLaunch.exe`'ye izin ver veya 7878 portunu aç.

**Soundpad bağlantısı yok diyor?**  
→ Soundpad'in açık olduğundan emin ol. Kapalıysa aç, SoundLaunch otomatik bağlanır.

**Ses çalmıyor ama hata da yok?**  
→ Soundpad index numaraları kaydı yaşamış olabilir. Ayarlar → "Silinmiş Sesleri Kontrol Et" butonuna bas.

**Port 7878 meşgul?**  
→ `server.py` içindeki `PORT = 7878` satırını başka bir sayıyla değiştir.

---

## Katkı

Pull request, issue veya öneri için çekinme. Bu proje küçük ama kullanışlı olmaya devam edecek.

---

## Lisans

[MIT](LICENSE) — İstediğin gibi kullan, dağıt, değiştir.

---

<div align="center">

*Klavyene dokunmadan meme yapmak için yapıldı.*

</div>
