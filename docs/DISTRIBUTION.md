# Creating a Distribution-Ready DMG

## Overview

The DMG build process creates a **self-contained** macOS application that includes all dependencies. Recipients can simply drag the app to Applications and run it - no Python installation or package management needed.

## Quick Build

```bash
cd /Users/gavingranger/Documents/MPHF-T
./scripts/build_dmg.sh
```

The DMG will be created in: `~/Downloads/Nexus.dmg`

## What's Included

The DMG contains:
- ✅ **Nexus.app** - The complete application
- ✅ **All Python dependencies** - MediaPipe, OpenCV, NumPy (bundled inside app)
- ✅ **All MediaPipe models** - Hand, face, object detection models
- ✅ **README.txt** - Installation instructions
- ✅ **Applications symlink** - For easy drag-and-drop installation

## How It Works

### PyInstaller Bundling

PyInstaller packages everything into a single `.app` bundle:
- Python interpreter
- All Python packages (MediaPipe, OpenCV, NumPy, etc.)
- All shared libraries and dependencies
- MediaPipe models
- Application code

### Self-Contained App

The resulting `.app` bundle:
- **No Python required** - Python is bundled inside
- **No pip installs** - All packages are included
- **No model downloads** - Models are bundled
- **Works offline** - No internet needed after installation

## Distribution Process

### 1. Build the DMG

```bash
./scripts/build_dmg.sh
```

This will:
1. Install dependencies in virtual environment
2. Download MediaPipe models
3. Build app icon
4. Create app bundle with PyInstaller
5. Create DMG with app and README

### 2. Test the DMG

1. Open the DMG: `open ~/Downloads/Nexus.dmg`
2. Drag `Nexus.app` to Applications
3. Open Applications → Nexus.app
4. Verify it works

### 3. Distribute

- **Email**: Attach DMG file
- **Cloud**: Upload to Google Drive, Dropbox, etc.
- **Website**: Host for download
- **USB**: Copy DMG file

## What Recipients See

When someone receives the DMG:

1. **Double-click DMG** → Opens disk image
2. **See**: Nexus.app and Applications folder
3. **Drag** Nexus.app to Applications
4. **Open** Applications → Nexus.app
5. **Grant** camera permission when prompted
6. **Use** the app immediately!

## File Size

Expected DMG size: **200-400 MB**
- App bundle: ~150-300 MB (includes all dependencies)
- DMG compression: Reduces size by ~30%

## Verification Checklist

Before distributing, verify:
- [ ] App opens without errors
- [ ] Camera access works
- [ ] Hand detection works
- [ ] Face detection works
- [ ] Object detection works
- [ ] No console errors
- [ ] Models load correctly
- [ ] App runs on clean macOS (test on different Mac if possible)

## Troubleshooting

### "App is damaged and can't be opened"

**Solution**: This is macOS Gatekeeper. Recipients should:
1. Right-click app → Open
2. Click "Open" in dialog
3. Or: System Settings → Privacy & Security → Allow app

### "Python not found" errors

**Solution**: This shouldn't happen if built correctly. Rebuild with:
```bash
./scripts/build_dmg.sh
```

### Models not found

**Solution**: Ensure models are downloaded before building:
```bash
# Models are downloaded automatically by build script
# But you can verify:
ls models/*.task
```

### Large file size

**Solution**: This is normal - MediaPipe and OpenCV are large. The DMG is compressed.

## Advanced: Code Signing (Optional)

For distribution outside App Store, you can code sign:

```bash
# Requires Apple Developer account
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/Nexus.app

# Notarize (optional)
xcrun notarytool submit dist/Nexus.app \
  --apple-id your@email.com \
  --team-id YOUR_TEAM_ID \
  --password YOUR_APP_PASSWORD
```

## Alternative: Create Installer Package

For more professional installation:

```bash
# Create .pkg installer
pkgbuild --root dist/Nexus.app \
  --identifier com.nexus.app \
  --version 1.0 \
  --install-location /Applications \
  Nexus.pkg
```

## Summary

The DMG build process creates a **truly self-contained** application:
- ✅ No Python installation needed
- ✅ No package installation needed  
- ✅ No model downloads needed
- ✅ Works immediately after drag-and-drop
- ✅ Professional DMG layout
- ✅ Easy distribution

Just build and share the DMG file!
