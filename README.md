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

## Run from source

```bash
git clone https://github.com/YOUR_USERNAME/Nexus.git
cd Nexus
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Models download on first run. Then:

```bash
python track.py
```

At the prompt choose `1` (Fast), `2` (Quality), or `3` (Auto). Grant camera access when asked.

## Build for macOS (.dmg)

Build on a Mac. Produces `Nexus.app` and a DMG in `~/Downloads/Nexus.dmg`.

```bash
./build.sh .dmg
```

With no argument on Mac, `./build.sh` defaults to `.dmg`.

Or the Mac-only script:

```bash
./build_mac_app.sh
```

Optional: add `icon.png` (1024×1024) in the project root; the build will use it for the app icon.

## Build for Windows (.exe)

Build on Windows. Produces `dist/Nexus/Nexus.exe` and optionally copies it to `%USERPROFILE%\Downloads\Nexus.exe`.

**Command Prompt:**

```bat
build.bat
```

**Git Bash or WSL:**

```bash
./build.sh .exe
```

With no argument on Windows, `./build.sh` defaults to `.exe`.

## Project layout

```
Nexus/
├── track.py           # Main app (run or entry for PyInstaller)
├── track.spec         # PyInstaller spec (Mac .app / Windows .exe)
├── requirements.txt
├── build.sh           # Cross-platform build: .dmg (Mac) or .exe (Windows)
├── build_mac_app.sh   # Mac-only: .app + DMG
├── build.bat          # Windows-only: .exe
├── icon.png           # Optional 1024×1024 app icon
├── models/            # Filled by build (hand.task, face.task, object_detector.task)
└── README.md
```

## Controls

| Key | Action |
|-----|--------|
| Q | Quit |
| C | Start gesture capture (type a name, then S to save) |
| R | Start/stop recording the graph panel to video |

Recordings and output go to `~/Desktop/Nexus_Output` (or `out/` when run from source).

## License

MIT
