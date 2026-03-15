# SoundLaunch

[English](#english) | [Türkçe](#turkce)

---

## English

SoundLaunch is a web-based Launchpad interface designed for the Soundpad software. It transforms any device with a web browser (like your smartphone or tablet) into a wireless control panel for your Soundpad audio library, completely eliminating the need for complex hotkey combinations. 

Whether you are gaming, live streaming, or recording a podcast, SoundLaunch provides a touch-friendly, latency-free way to manage your sound effects.

### Features
* **Zero Hotkeys:** Communicates directly with Soundpad via the Windows Named Pipe API. No keyboard macros required.
* **Device Agnostic:** Works seamlessly on any device connected to your local network that has a web browser.
* **Spam Mode:** Play a specific sound repeatedly at custom millisecond intervals.
* **Customization:** Organize sounds into categories, assign custom images, and apply color tags.
* **OLED UI:** A modern, pitch-black interface optimized for mobile battery saving and low eye strain.
* **Easy Import:** Automatically fetch and sync your existing Soundpad tracklist with a single click.

### Installation & Usage

You can run SoundLaunch either via the standalone executable or directly from the Python source code. Both server and Soundpad must be running on the same PC.

#### Method 1: Standalone Executable (.exe) [Recommended]
1. Download the latest `SoundLaunch.exe` from the **Releases** page.
2. Run the executable. It will automatically start the backend server and display your local IP address.
3. Open a web browser on your phone or tablet and navigate to the address shown in the console window.
   > Example: `http://192.168.1.42:7878`

#### Method 2: From Source (Python)
1. Ensure Python is installed, then install the required dependencies:
   `pip install -r requirements.txt`
2. Start the server:
   `python server.py`
3. Connect via your mobile browser to your computer's local IPv4 address on port 7878.

### Soundpad Configuration
For SoundLaunch to communicate with Soundpad, the Named Pipe API must be enabled.
Open Soundpad and navigate to:
`File` -> `Preferences` -> `Remote Control` -> Check **"Enable named pipe"**.

---

## Türkçe

SoundLaunch, Soundpad yazılımı için geliştirilmiş web tabanlı bir Launchpad arayüzüdür. Tarayıcıya sahip herhangi bir cihazı (akıllı telefonunuz veya tabletiniz gibi) Soundpad ses kütüphaneniz için kablosuz bir kontrol paneline dönüştürür ve karmaşık klavye kısayollarına olan ihtiyacı tamamen ortadan kaldırır.

Oyun oynarken, canlı yayın yaparken veya podcast kaydederken ses efektlerinizi yönetmek için dokunmatik ve gecikmesiz bir deneyim sunar.

### Özellikler
* **Sıfır Kısayol Tuşu:** Windows Named Pipe API üzerinden doğrudan Soundpad ile haberleşir. Klavye makrosu gerektirmez.
* **Cihaz Bağımsız:** Yerel ağınıza bağlı, web tarayıcısı olan tüm cihazlarda sorunsuz çalışır.
* **Spam Modu:** Belirlediğiniz milisaniye aralıklarıyla bir sesi peş peşe (spam) çaldırın.
* **Tam Kişiselleştirme:** Seslerinizi kategorize edin, özel görseller atayın ve renk etiketleri ekleyin.
* **OLED Arayüz:** Mobil cihazlarda pil tasarrufu sağlayan ve göz yormayan tam siyah, modern tasarım.
* **Kolay İçe Aktarım:** Mevcut Soundpad listenizi tek tıkla otomatik olarak çekin ve web arayüzüne ekleyin.

### Kurulum ve Kullanım

SoundLaunch'ı tek başına çalışan bir program (.exe) olarak veya doğrudan Python kaynak kodundan çalıştırabilirsiniz. Sunucu ve Soundpad aynı bilgisayarda çalışmalıdır.

#### Yöntem 1: Çalıştırılabilir Dosya (.exe) [Önerilen]
1. **Releases** sayfasından en güncel `SoundLaunch.exe` dosyasını indirin.
2. Dosyayı çalıştırın. Arka plan sunucusu otomatik olarak başlayacak ve yerel IP adresinizi ekranda gösterecektir.
3. Telefonunuzda veya tabletinizde bir web tarayıcısı açın ve konsol penceresinde gösterilen adrese gidin.
   > Örnek: `http://192.168.1.42:7878`

#### Yöntem 2: Kaynak Koddan (Python)
1. Python'un kurulu olduğundan emin olun ve gerekli kütüphaneleri yükleyin:
   `pip install -r requirements.txt`
2. Sunucuyu başlatın:
   `python server.py`
3. Mobil tarayıcınız üzerinden bilgisayarınızın yerel IPv4 adresine 7878 portu ile bağlanın.

### Soundpad Ayarları
SoundLaunch'ın Soundpad ile iletişim kurabilmesi için Named Pipe API'sinin aktif olması gerekir.
Soundpad'i açın ve şu adımları izleyin:
`Dosya` -> `Tercihler` -> `Uzaktan Kontrol` -> **"Adlandırılmış kanalı etkinleştir"** (Enable named pipe) kutucuğunu işaretleyin.
