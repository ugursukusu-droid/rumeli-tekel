@echo off
title Rumeli Tekel Bulut Sunucusu
cd /d "%~dp0"
echo ====================================================
echo   Rumeli Tekel Cari & Borc Takip Sistemi Aciliyor...
echo ====================================================
start "" python main.py
timeout /t 2 >nul
start "" http://localhost:8000
exit
