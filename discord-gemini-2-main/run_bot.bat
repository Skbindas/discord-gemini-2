@echo off
title Discord Bot Smart Launcher
color 0A

echo.
echo ========================================
echo    DISCORD BOT SMART LAUNCHER
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found! Starting smart launcher...
echo.

python run_bot.py

echo.
echo Bot session ended.
pause
