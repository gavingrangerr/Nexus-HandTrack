#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
APP_NAME="Nexus"
DMG_NAME="Nexus"

echo "==> Project root: $PROJECT_ROOT"

VENV_DIR="$PROJECT_ROOT/venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "==> Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "==> Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

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

echo "==> Downloading MediaPipe models..."
download_model "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" "$MODELS_DIR/hand.task"
download_model "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" "$MODELS_DIR/face.task"
download_model "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite" "$MODELS_DIR/object_detector.task"

ICON_PNG="$PROJECT_ROOT/assets/icon.png"
ICON_ICNS="$PROJECT_ROOT/assets/icon.icns"
if [[ -f "$ICON_PNG" ]]; then
    echo "==> Building app icon from assets/icon.png..."
    ICONSET="$PROJECT_ROOT/assets/icon.iconset"
    rm -rf "$ICONSET" "$ICON_ICNS"
    mkdir -p "$ICONSET"
    for size in 16 32 128 256 512; do
        sips -z $size $size "$ICON_PNG" --out "$ICONSET/icon_${size}x${size}.png"
    done
    sips -z 32 32   "$ICON_PNG" --out "$ICONSET/icon_16x16@2x.png"
    sips -z 64 64   "$ICON_PNG" --out "$ICONSET/icon_32x32@2x.png"
    sips -z 256 256 "$ICON_PNG" --out "$ICONSET/icon_128x128@2x.png"
    sips -z 512 512 "$ICON_PNG" --out "$ICONSET/icon_256x256@2x.png"
    sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET/icon_512x512@2x.png"
    iconutil -c icns "$ICONSET" -o "$ICON_ICNS"
    rm -rf "$ICONSET"
else
    rm -f "$ICON_ICNS"
fi

echo "==> Cleaning previous build..."
rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist"

echo "==> Running PyInstaller..."
pyinstaller --noconfirm config/nexus.spec

APP_PATH="$PROJECT_ROOT/dist/$APP_NAME.app"
if [[ ! -d "$APP_PATH" ]]; then
    echo "ERROR: $APP_NAME.app not found in dist/"
    exit 1
fi
echo "==> Built: $APP_PATH"

echo "==> Creating DMG..."
DMG_STAGE="$PROJECT_ROOT/dmg_stage"
rm -rf "$DMG_STAGE"
mkdir -p "$DMG_STAGE"

# Copy app
cp -R "$APP_PATH" "$DMG_STAGE/"

# Create Applications symlink
ln -s /Applications "$DMG_STAGE/Applications"

# Create README
cat > "$DMG_STAGE/README.txt" << 'EOF'
Nexus - Advanced Tracking Division
==================================

INSTALLATION:
1. Drag "Nexus.app" to the "Applications" folder
2. Open Applications and double-click Nexus.app
3. Grant camera permission when prompted

FEATURES:
- Hand landmark tracking
- Face mesh overlay  
- Object detection
- Real-time graphs

SYSTEM REQUIREMENTS:
- macOS 10.15 or later
- Camera (built-in or external)
- No additional software needed!

TROUBLESHOOTING:
If app won't open:
- Right-click → Open → Click "Open"
- Or: System Settings → Privacy & Security → Allow app
EOF

DOWNLOAD_DMG="${HOME}/Downloads/${DMG_NAME}.dmg"
rm -f "$DOWNLOAD_DMG"

# Create DMG with better formatting
hdiutil create -volname "$APP_NAME" \
    -srcfolder "$DMG_STAGE" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "$DOWNLOAD_DMG"

rm -rf "$DMG_STAGE"

echo ""
echo "=========================================="
echo "✅ DMG Created Successfully!"
echo "=========================================="
echo ""
echo "App:  $APP_PATH"
echo "DMG:  $DOWNLOAD_DMG"
echo ""
echo "The DMG is self-contained - recipients can:"
echo "  1. Open the DMG"
echo "  2. Drag Nexus.app to Applications"
echo "  3. Run it immediately (no installation needed!)"
echo ""
