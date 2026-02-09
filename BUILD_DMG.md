# Building a Distribution-Ready DMG

## Quick Start

Build a self-contained DMG that anyone can use:

```bash
cd /Users/gavingranger/Documents/MPHF-T
./scripts/build_dmg.sh
```

The DMG will be created in: `~/Downloads/Nexus.dmg`

## What Makes It Self-Contained?

The build process uses **PyInstaller** to bundle everything:

✅ **Python interpreter** - Bundled inside the app  
✅ **All dependencies** - MediaPipe, OpenCV, NumPy (all included)  
✅ **MediaPipe models** - Hand, face, object models (bundled)  
✅ **Shared libraries** - All required system libraries  

**Result**: A single `.app` file that works on any Mac without installing anything!

## Distribution Process

### Step 1: Build

```bash
./scripts/build_dmg.sh
```

This creates:
- `dist/Nexus.app` - The application bundle
- `~/Downloads/Nexus.dmg` - Distribution DMG

### Step 2: Test

1. Open the DMG: `open ~/Downloads/Nexus.dmg`
2. Drag `Nexus.app` to Applications
3. Test the app
4. Verify everything works

### Step 3: Share

Send the DMG file to anyone:
- **Email**: Attach DMG
- **Cloud**: Upload to Drive/Dropbox
- **Website**: Host for download
- **USB**: Copy file

## What Recipients Do

1. **Receive** the DMG file
2. **Double-click** to open
3. **Drag** `Nexus.app` to Applications folder
4. **Open** Applications → Nexus.app
5. **Grant** camera permission
6. **Use** immediately!

**No Python installation needed!**  
**No package installation needed!**  
**No model downloads needed!**

## DMG Contents

The DMG contains:
- `Nexus.app` - Complete application (all dependencies inside)
- `Applications` - Symlink for easy installation
- `README.txt` - Installation instructions

## File Size

Expected size: **200-400 MB**
- App bundle: ~150-300 MB (includes all dependencies)
- DMG compression: Reduces size

This is normal - MediaPipe and OpenCV are large libraries.

## Verification

Before distributing, test:
- [ ] App opens without errors
- [ ] Camera works
- [ ] Hand detection works
- [ ] Face detection works
- [ ] Object detection works
- [ ] No Python errors
- [ ] Models load correctly

## Troubleshooting

### "App is damaged"

**Solution**: macOS Gatekeeper. Recipients should:
- Right-click → Open → Click "Open"
- Or: System Settings → Privacy & Security → Allow

### Large file size

**Normal**: MediaPipe + OpenCV are large. The app is self-contained.

### Models missing

**Solution**: Models are bundled automatically. If missing, rebuild:
```bash
./scripts/build_dmg.sh
```

## Technical Details

### PyInstaller Configuration

The `config/nexus.spec` file configures:
- What to bundle (all MediaPipe, OpenCV, NumPy)
- Model files to include
- App metadata (name, icon, permissions)
- macOS-specific settings

### App Bundle Structure

```
Nexus.app/
├── Contents/
│   ├── MacOS/
│   │   └── Nexus          # Executable
│   ├── Resources/
│   │   ├── models/        # MediaPipe models
│   │   └── ...            # Python packages
│   └── Info.plist         # App metadata
```

Everything is inside the `.app` bundle!

## Summary

The DMG build creates a **professional, self-contained** macOS application:

✅ **One file** - Everything included  
✅ **Easy installation** - Drag and drop  
✅ **No dependencies** - Works immediately  
✅ **Professional** - Standard macOS DMG format  

Just build and share!
