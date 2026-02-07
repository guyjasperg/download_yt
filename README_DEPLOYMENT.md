# YouTube Downloader - Deployment Guide

## System Requirements
- Windows 10/11
- Python 3.13
- VLC Media Player (64-bit)
- FFmpeg

## Installation Steps

### 1. Install Python 3.13
- Download from: https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation

### 2. Install VLC Media Player (64-bit)
- Download from: https://www.videolan.org/vlc/
- Install with default settings

### 3. Install FFmpeg
- Download from: https://www.gyan.dev/ffmpeg/builds/
- Download "ffmpeg-release-essentials.zip"
- Extract to `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to System PATH:
  1. Right-click "This PC" > Properties > Advanced system settings
  2. Click "Environment Variables"
  3. Under "System variables", find "Path", click "Edit"
  4. Click "New" and add: `C:\ffmpeg\bin`
  5. Click OK on all dialogs
  6. **Restart your computer** (or at least close all terminals)

### 4. Setup Project
- Run `setup.bat`
- Wait for all dependencies to install

### 5. Run the Application
- Run `run.bat`

## Troubleshooting

### FFmpeg not found
- Verify FFmpeg is installed: Open CMD and type `ffmpeg -version`
- If not found, check PATH is set correctly
- Restart your terminal/computer after adding to PATH

### VLC errors
- Make sure you installed 64-bit VLC (not 32-bit)
- Check VLC is installed in default location

### Python errors
- Make sure Python 3.13 is installed (not 3.14 or 3.12)
- Check Python is in PATH: `python --version`

## Project Structure
```
download_yt/
├── .venv/                  # Virtual environment (created by setup.bat)
├── DOWNLOADS/              # Temporary download folder
├── NEW_SONGS/              # Output folder
├── DownloadYT.py          # Main script
├── config.ini             # Configuration file
├── requirements_windows.txt  # Python dependencies
├── setup.bat              # Setup script
├── run.bat                # Run script
└── README_DEPLOYMENT.md   # This file
```
```

## Step 5: Clean up requirements_windows.txt (optional)

Open `requirements_windows.txt` and make sure it doesn't have unnecessary packages. It should look something like:
```
Cython<3.0
opencv-python
python-vlc
requests
# Add other packages your script actually uses