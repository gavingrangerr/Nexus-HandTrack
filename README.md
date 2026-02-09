# Nexus

Real-time hand, face, and object tracking using OpenCV and MediaPipe. Runs as a desktop app on macOS (DMG) and Windows (EXE) or from source with Python.

## Features

- Hand landmark tracking with gesture recognition (fist, point, peace, etc.)
- Face mesh overlay
- Object detection (bottles, cups, etc.)
- X/Y position graphs with smooth trails
- Resizable window; close with Q or the window close button
- Profile selection at launch: Fast (FPS), Quality (visual), or Auto (architecture-adaptive)

## Requirements

- Python 3.10+
- Camera (built-in or external)
- macOS or Windows for packaged builds

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 src/nexus.py

# Or use the run script
./run.sh
```

## Install and run from terminal (no IDE)

Install Python 3.10+ from [python.org](https://www.python.org/downloads/) if needed. Then use a terminal (Terminal.app on Mac, Command Prompt or PowerShell on Windows).

### Mac (Terminal)

```bash
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python nexus.py
```

### Windows (Command Prompt or PowerShell)

**Command Prompt:**

```bat
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python nexus.py
```

**PowerShell:**

```powershell
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python nexus.py
```

If PowerShell blocks the script, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then try again.

At launch choose `1` (Fast), `2` (Quality), or `3` (Auto). Grant camera access when asked. Models download on first run.

## Get the newest version (already set up)

If you’ve already cloned and installed everything and only want the latest Python/code:

**Go into the project folder** (the folder where you ran `git clone`). For example, if you put it in Documents:

```bash
cd ~/Documents/nexus
git pull
```

If that says “No such file or directory”, the repo is somewhere else. Find it (e.g. `ls ~/Documents` or `ls ~`) then `cd` into that folder and run `git pull` there.

Then run the app as usual (`source venv/bin/activate` then `python nexus.py`).

### “No module named 'cv2'” or missing packages

Make sure you’re in the project folder and the venv is active, then install dependencies:

**Mac:**

```bash
cd ~/Documents/nexus
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:** same idea—`cd` into the project folder, run `venv\Scripts\activate` (or `.\venv\Scripts\Activate.ps1` in PowerShell), then `pip install -r requirements.txt`.

That installs OpenCV (cv2), MediaPipe, and the rest. Then run `python nexus.py` again.

## Mac: run from terminal and build the DMG

All from **Terminal.app** (no IDE). One-time setup, then either run the app or build the installer.

**1. Clone and install (once):**

```bash
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2a. Run from source:**

```bash
python nexus.py
```

**2b. Build the Mac app and DMG:**

```bash
./scripts/build_mac_app.sh
```

This creates `dist/Nexus.app` and puts `Nexus.dmg` in your Downloads folder. Optional: add `assets/icon.png` (1024×1024) for the app icon.

## Build for Windows (.exe)

Run on Windows. Produces `dist/Nexus/Nexus.exe` and optionally copies to `%USERPROFILE%\Downloads\Nexus.exe`.

**Command Prompt (from repo root):**

```bat
scripts\build.bat
```

**Git Bash or WSL:**

```bash
./scripts/build.sh .exe
```

With no argument on Windows, `./scripts/build.sh` defaults to `.exe`.

## Project layout

```
Nexus-HandTrack/
├── .gitignore
├── README.md
├── requirements.txt
├── nexus.py                 # Main application entry point
├── assets/
│   └── icon.png            # Application icon
├── config/
│   └── nexus.spec          # PyInstaller configuration
├── docs/
│   └── UI_COLORS.txt       # UI color reference documentation
├── scripts/
│   ├── build.sh            # Cross-platform build script
│   ├── build_mac_app.sh    # macOS-specific build script
│   └── build.bat           # Windows build script
├── models/                  # MediaPipe models (auto-downloaded)
├── venv/                   # Virtual environment (git-ignored)
├── build/                   # Build artifacts (git-ignored)
└── dist/                    # Distribution output (git-ignored)
```

- **Root:** Main application (`nexus.py`), dependencies (`requirements.txt`), documentation (`README.md`)
- **assets/:** Application assets like icons
- **config/:** Build configuration files (PyInstaller spec)
- **docs/:** Documentation files
- **scripts/:** Build scripts; run from repo root as above
- **models/:** MediaPipe model files (populated automatically on first run)
- `venv/`, `build/`, `dist/` are created by the build and ignored by git

## Controls

| Key | Action |
|-----|--------|
| Q | Quit |
| C | Start gesture capture (type a name, then S to save) |
| R | Start/stop recording the graph panel to video and log tracking data (hands, wrists, elbows, shoulders, face) to a CSV with the same timestamp; both saved to Nexus_Output |
| L | Start/stop logging only (no video) to CSV |

Recordings and output go to `~/Downloads/Nexus_Output` (Mac) or `%USERPROFILE%\Downloads\Nexus_Output` (Windows).

## License

MIT
