@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo HATA: .venv bulunamadi. Once README.md kurulum adimlarini uygulayin.
  exit /b 1
)
echo EYBA http://127.0.0.1:8765 adresinde baslatiliyor...
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8765
