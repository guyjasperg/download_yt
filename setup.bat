@echo off
echo ================================================
echo YouTube Downloader - Windows Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.13 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo [4/4] Installing dependencies...
pip install -r requirements_windows.txt

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Install VLC Media Player (64-bit): https://www.videolan.org/vlc/
echo 2. Install FFmpeg: https://www.gyan.dev/ffmpeg/builds/
echo    - Extract to C:\ffmpeg
echo    - Add C:\ffmpeg\bin to System PATH
echo 3. Run: run.bat
echo.
pause