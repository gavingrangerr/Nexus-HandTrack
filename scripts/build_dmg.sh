#!/bin/bash

# Build self-contained DMG for distribution
# Creates a DMG that can be sent to anyone - all dependencies included

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

APP_NAME="Nexus"
DMG_NAME="Nexus"

echo "=========================================="
echo "Building Self-Contained DMG"
echo "=========================================="
echo ""

# Check if on macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Error: DMG can only be built on macOS"
    exit 1
fi

# Setup virtual environment
VENV_DIR="$PROJECT_ROOT/venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "[1/7] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "[2/7] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "[3/7] Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pyinstaller

# Download models
MODELS_DIR="$PROJECT_ROOT/models"
mkdir -p "$MODELS_DIR"

download_model() {
    local url="$1"
    local out="$2"
    if [[ -f "$out" ]]; then
        echo "   [skip] $(basename "$out")"
        return
    fi
    echo "   downloading $(basename "$out")..."
    curl -sSL -o "$out" "$url"
}

echo "[4/7] Downloading MediaPipe models..."
download_model "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" "$MODELS_DIR/hand.task"
download_model "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" "$MODELS_DIR/face.task"
download_model "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite" "$MODELS_DIR/object_detector.task"

# Build icon
ICON_PNG="$PROJECT_ROOT/assets/icon.png"
ICON_ICNS="$PROJECT_ROOT/assets/icon.icns"
if [[ -f "$ICON_PNG" ]]; then
    echo "[5/7] Building app icon..."
    ICONSET="$PROJECT_ROOT/assets/icon.iconset"
    rm -rf "$ICONSET" "$ICON_ICNS"
    mkdir -p "$ICONSET"
    for size in 16 32 128 256 512; do
        sips -z $size $size "$ICON_PNG" --out "$ICONSET/icon_${size}x${size}.png" 2>/dev/null || true
    done
    sips -z 32 32   "$ICON_PNG" --out "$ICONSET/icon_16x16@2x.png" 2>/dev/null || true
    sips -z 64 64   "$ICON_PNG" --out "$ICONSET/icon_32x32@2x.png" 2>/dev/null || true
    sips -z 256 256 "$ICON_PNG" --out "$ICONSET/icon_128x128@2x.png" 2>/dev/null || true
    sips -z 512 512 "$ICON_PNG" --out "$ICONSET/icon_256x256@2x.png" 2>/dev/null || true
    sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET/icon_512x512@2x.png" 2>/dev/null || true
    iconutil -c icns "$ICONSET" -o "$ICON_ICNS" 2>/dev/null || true
    rm -rf "$ICONSET"
fi

# Clean previous builds
echo "[6/7] Cleaning previous builds..."
rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist"

# Build with PyInstaller
echo "[7/7] Building application with PyInstaller..."
echo "   This bundles all dependencies (MediaPipe, OpenCV, NumPy, etc.)"
pyinstaller --noconfirm config/nexus.spec

APP_PATH="$PROJECT_ROOT/dist/$APP_NAME.app"
if [[ ! -d "$APP_PATH" ]]; then
    echo "ERROR: $APP_NAME.app not found in dist/"
    exit 1
fi

echo ""
echo "=========================================="
echo "Creating DMG..."
echo "=========================================="

# Create DMG staging area
DMG_STAGE="$PROJECT_ROOT/dmg_stage"
rm -rf "$DMG_STAGE"
mkdir -p "$DMG_STAGE"

# Copy app
cp -R "$APP_PATH" "$DMG_STAGE/"

# Create Applications symlink
ln -s /Applications "$DMG_STAGE/Applications"

# Create README for DMG
cat > "$DMG_STAGE/README.txt" << 'EOF'
Nexus - Advanced Tracking Division
==================================

INSTALLATION:
1. Drag "Nexus.app" to the "Applications" folder
2. Open Applications folder and double-click Nexus.app
3. Grant camera permission when prompted

FEATURES:
- Hand landmark tracking
- Face mesh overlay
- Object detection
- Real-time graphs and visualizations

SYSTEM REQUIREMENTS:
- macOS 10.15 or later
- Camera (built-in or external)
- No additional software needed - everything is included!

TROUBLESHOOTING:
If the app won't open:
1. Right-click the app → Open
2. Click "Open" in the security dialog
3. Or: System Settings → Privacy & Security → Allow app

For support, visit: https://github.com/gavingrangerr/Nexus-HandTrack
EOF

# Create DMG
DMG_PATH="${HOME}/Downloads/${DMG_NAME}.dmg"
rm -f "$DMG_PATH"

echo "Creating DMG image..."
hdiutil create -volname "$APP_NAME" \
    -srcfolder "$DMG_STAGE" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "$DMG_PATH"

# Cleanup
rm -rf "$DMG_STAGE"

echo ""
echo "=========================================="
echo "✅ DMG Created Successfully!"
echo "=========================================="
echo ""
echo "Location: $DMG_PATH"
echo ""
echo "The DMG is self-contained and includes:"
echo "  ✅ All Python dependencies (MediaPipe, OpenCV, NumPy)"
echo "  ✅ All MediaPipe models"
echo "  ✅ Everything needed to run"
echo ""
echo "To distribute:"
echo "  1. Send the DMG file to anyone"
echo "  2. They open it and drag Nexus.app to Applications"
echo "  3. They can run it immediately - no installation needed!"
echo ""
