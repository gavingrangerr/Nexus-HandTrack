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

## Install and run from terminal (no IDE)

Install Python 3.10+ from [python.org](https://www.python.org/downloads/) if needed. Then use a terminal (Terminal.app on Mac, Command Prompt or PowerShell on Windows).

### Mac (Terminal)

```bash
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python track.py
```

### Windows (Command Prompt or PowerShell)

**Command Prompt:**

```bat
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python track.py
```

**PowerShell:**

```powershell
git clone https://github.com/gavingrangerr/Nexus-HandTrack.git
cd Nexus-HandTrack
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python track.py
```

If PowerShell blocks the script, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then try again.

At launch choose `1` (Fast), `2` (Quality), or `3` (Auto). Grant camera access when asked. Models download on first run.

## Get the newest updates (Mac terminal)

If you already have the repo and want the latest code from GitHub:

```bash
cd Nexus-HandTrack
git pull
source venv/bin/activate
pip install -r requirements.txt
python track.py
```

If you get merge conflicts, ask the repo owner or run `git status` and resolve. To discard local changes and match GitHub exactly: `git fetch origin` then `git reset --hard origin/main` (replace `main` with your default branch if different).

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
python track.py
```

**2b. Build the Mac app and DMG:**

```bash
./scripts/build_mac_app.sh
```

This creates `dist/Nexus.app` and puts `Nexus.dmg` in your Downloads folder. Optional: add `icon.png` (1024×1024) in the project root for the app icon.

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
├── track.py
├── track.spec
├── icon.png
├── models
├── scripts
│   ├── build.sh
│   ├── build_mac_app.sh
│   └── build.bat
├── venv
├── build
└── dist
```

- **Root:** App entry (`track.py`), PyInstaller spec (`track.spec`), deps (`requirements.txt`), optional `icon.png`. `models/` is populated by the build (hand/face/object assets).
- **scripts/:** Build scripts; run from repo root as above. `venv/`, `build/`, `dist/` are created by the build and ignored by git.

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
