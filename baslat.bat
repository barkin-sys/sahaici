@echo off
chcp 65001 >nul
title Saha Ici - Canli Futbol ve AI Analiz Platformu
cd /d "%~dp0"

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [HATA] Python calistirilamadi!
    pause
    exit /b 1
)

cls
echo ==============================================================================
echo           SAHA ICI - CANLI MAC TAKIP VE AI ANALIZ PLATFORMU
echo ==============================================================================
echo.
echo [1/2] Sunucu baslatiliyor (FastAPI ^& Uvicorn)...
echo [2/2] Tarayiciniz birazdan http://localhost:8000 adresini acacak...
echo.
start "" http://localhost:8000
python server.py
pause