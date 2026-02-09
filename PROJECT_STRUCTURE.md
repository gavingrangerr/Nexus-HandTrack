# Project Structure

```
MPHF-T/
├── src/                    # Source code
│   └── nexus.py           # Main application
│
├── scripts/                # Build and utility scripts
│   ├── build.sh           # Linux build script
│   ├── build.bat          # Windows build script
│   └── build_mac_app.sh   # macOS app build script
│
├── config/                 # Configuration files
│   └── nexus.spec         # PyInstaller spec file
│
├── assets/                 # Application assets
│   ├── icon.png           # App icon (PNG)
│   └── icon.icns          # App icon (macOS)
│
├── models/                 # MediaPipe model files
│   ├── hand.task
│   ├── face.task
│   └── object_detector.task
│
├── docs/                   # Documentation
│   ├── UI_COLORS.txt     # UI color reference
│   └── setup/             # Setup guides
│       └── GITHUB_ACTIONS_SETUP.md
│
├── .github/                # GitHub configuration
│   └── workflows/         # CI/CD workflows
│
├── README.md              # Main project documentation
├── requirements.txt       # Python dependencies
├── run.sh                 # Quick run script
└── PROJECT_STRUCTURE.md   # This file
```

## Directory Descriptions

### `src/`
Main application source code. Contains the core `nexus.py` file with all the tracking logic.

### `scripts/`
Build and utility scripts for different platforms:
- `build.sh` - Linux/macOS build
- `build.bat` - Windows build
- `build_mac_app.sh` - macOS app bundle creation

### `config/`
Configuration files for building and packaging:
- `nexus.spec` - PyInstaller configuration

### `assets/`
Application assets like icons and images.

### `models/`
MediaPipe model files (`.task` and `.tflite`). Models are downloaded automatically on first run if not present.

### `docs/`
Documentation files:
- `UI_COLORS.txt` - Reference for UI colors
- `setup/` - Setup and installation guides

### `.github/`
GitHub-specific configuration:
- `workflows/` - GitHub Actions CI/CD workflows

## Running the Application

**Quick start:**
```bash
./run.sh
```

**Or directly:**
```bash
python3 src/nexus.py
```

## Building

See `scripts/` directory for platform-specific build scripts.
