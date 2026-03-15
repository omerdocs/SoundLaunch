@echo off
title SoundLaunch — .exe Derleyici
color 0A

echo.
echo  ╔══════════════════════════════════════╗
echo  ║       SoundLaunch .exe Derleyici     ║
echo  ╚══════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [HATA] Python bulunamadi!
    echo  Python indirmek icin: https://python.org
    pause
    exit /b 1
)
echo  [OK] Python bulundu.

:: Install dependencies
echo.
echo  Bagimliliklar yukleniyor...
pip install fastapi uvicorn pywin32 pystray pillow python-multipart pyinstaller --quiet
if errorlevel 1 (
    echo  [HATA] Bagimlilk yukleme basarisiz!
    pause
    exit /b 1
)
echo  [OK] Bagimliliklar hazir.

:: Build exe
echo.
echo  .exe derleniyor... (1-3 dakika surebilir)
echo.
python -m PyInstaller launcher.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo  [HATA] Derleme basarisiz! Hata mesajini yukarida kontrol edin.
    pause
    exit /b 1
)

echo.
echo  ╔══════════════════════════════════════╗
echo  ║           DERLEME BASARILI!          ║
echo  ║                                      ║
echo  ║  dist\SoundLaunch.exe                ║
echo  ╚══════════════════════════════════════╝
echo.
echo  SoundLaunch.exe dosyasini dist klasoründe bulabilirsin.
echo  Kullanmak icin sadece SoundLaunch.exe'ye cift tikla!
echo.
pause
