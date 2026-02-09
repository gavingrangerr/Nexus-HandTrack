# Windows Installation Guide

This guide will help you install and run Nexus on a Windows computer.

## Prerequisites

- **Windows 10 or later**
- **Python 3.10 or later** - Download from [python.org](https://www.python.org/downloads/)
  - During installation, check "Add Python to PATH"
- **Webcam** - Built-in or external USB camera
- **Internet connection** - For downloading dependencies and MediaPipe models

## Method 1: Run from Source (Recommended for Development)

### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Click "Install Now"

### Step 2: Clone or Download the Repository

**Option A: Using Git (if you have Git installed):**
```cmd
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
```

**Option B: Download ZIP:**
1. Go to the GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open Command Prompt in the extracted folder

### Step 3: Set Up Virtual Environment

Open **Command Prompt** (cmd) or **PowerShell** in the project folder:

**Command Prompt:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell shows an execution policy error, run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- OpenCV (cv2)
- NumPy
- MediaPipe
- PyInstaller (for building executables)

### Step 5: Run the Application

```cmd
python src\nexus.py
```

On first run, MediaPipe models will be downloaded automatically (hand.task, face.task).

## Method 2: Build Windows Executable (.exe)

Build a standalone executable that can run without Python installed.

### Option A: Build on Windows Computer

**Step 1: Complete Method 1 Steps 1-4**

Make sure you have Python installed and dependencies set up.

**Step 2: Build the Executable**

**Command Prompt:**
```cmd
scripts\build.bat
```

**PowerShell:**
```powershell
.\scripts\build.bat
```

**Git Bash or WSL:**
```bash
./scripts/build.sh .exe
```

**Step 3: Find Your Executable**

The build script creates:
- **Main location:** `dist\Nexus\Nexus.exe`
- **Copy location:** `%USERPROFILE%\Downloads\Nexus.exe` (usually `C:\Users\YourName\Downloads\Nexus.exe`)

**Step 4: Run the Executable**

Double-click `Nexus.exe` or run from command line:
```cmd
dist\Nexus\Nexus.exe
```

### Option B: Build on Mac Using GitHub Actions (Recommended)

If you're on a Mac and want to build a Windows executable, use GitHub Actions:

**Step 1: Push Your Code to GitHub**

```bash
git add .
git commit -m "Ready for Windows build"
git push origin main
```

**Step 2: Trigger the Build**

1. Go to your GitHub repository
2. Click the **Actions** tab
3. Select **Build Windows Executable** workflow
4. Click **Run workflow** → **Run workflow** (or it will run automatically on push)

**Step 3: Download the Executable**

1. Wait for the workflow to complete (~5-10 minutes)
2. Click on the completed workflow run
3. Scroll down to **Artifacts**
4. Download **Nexus-Windows-Executable**
5. Extract the ZIP file to get `Nexus.exe`

**Step 4: Transfer to Windows**

- Email the `.exe` file to yourself
- Use cloud storage (Dropbox, Google Drive, etc.)
- Transfer via USB drive
- Use file sharing service

**Step 5: Run on Windows**

Double-click `Nexus.exe` on the Windows computer. No Python installation needed!

## Troubleshooting

### "Python is not recognized"

- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH:
  1. Find Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX`)
  2. Add `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX` and `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\Scripts` to PATH
  3. Restart Command Prompt

### "No module named 'cv2'" or Missing Packages

Make sure your virtual environment is activated and install dependencies:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Camera Not Working

1. **Grant camera permissions:**
   - Windows Settings → Privacy → Camera
   - Enable "Allow apps to access your camera"
   - Enable "Allow desktop apps to access your camera"

2. **Check camera is working:**
   - Try Windows Camera app first
   - Make sure no other app is using the camera

3. **Try different camera index:**
   - The app tries cameras 0-5 by default
   - If you have multiple cameras, try disconnecting others

### Build Fails

1. **Make sure PyInstaller is installed:**
   ```cmd
   pip install pyinstaller
   ```

2. **Check antivirus:**
   - Some antivirus software blocks PyInstaller
   - Temporarily disable or add exception

3. **Clean build:**
   ```cmd
   rmdir /s /q build dist
   scripts\build.bat
   ```

### Application Crashes on Startup

1. **Check Windows Event Viewer:**
   - Search "Event Viewer" in Windows
   - Look for application errors

2. **Run from command line to see errors:**
   ```cmd
   python src\nexus.py
   ```

3. **Check camera permissions** (see above)

## Using the Application

### Profile Selection

When you start the app, choose a profile:
- **1** - FAST: FPS optimized (staggered detection)
- **2** - QUALITY: Visual max (concurrent landmarks)
- **3** - AUTO: Architecture adaptive (recommended)

### Controls

| Key | Action |
|-----|--------|
| **Q** | Quit application |
| **C** | Start gesture capture (type name, press S to save) |
| **R** | Start/stop recording graph panel to video |
| **L** | Start/stop logging to CSV |

### Output Files

Recordings and logs are saved to:
```
%USERPROFILE%\Downloads\Nexus_Output\
```

Usually: `C:\Users\YourName\Downloads\Nexus_Output\`

## System Requirements

- **OS:** Windows 10 (64-bit) or later
- **RAM:** 4GB minimum, 8GB recommended
- **CPU:** Any modern processor (Intel/AMD)
- **Camera:** Any USB or built-in webcam
- **Disk Space:** ~500MB for application + models

## Notes

- The application uses OpenCV's default camera backend on Windows (`CAP_ANY`)
- First run downloads MediaPipe models (~50MB total)
- Models are cached in the `models\` folder
- The executable includes all dependencies - no Python installation needed

## Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Run from command line to see error messages
3. Check Windows Event Viewer for crash logs
4. Open an issue on GitHub with:
   - Windows version
   - Python version (if running from source)
   - Error messages
   - Steps to reproduce
