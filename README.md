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

## Build for macOS (.dmg)

Run on a Mac. Produces `Nexus.app` and `~/Downloads/Nexus.dmg`.


Mac-only script:

```bash
./scripts/build_mac_app.sh
```

With no argument on Mac, `./scripts/build.sh` defaults to `.dmg`. Optional: add `icon.png` (1024×1024) in the project root for the app icon.

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
| R | Start/stop recording the graph panel to video |

Recordings and output go to `~/Downloads/Nexus_Output` (Mac) or `%USERPROFILE%\Downloads\Nexus_Output` (Windows).

## License

MIT
