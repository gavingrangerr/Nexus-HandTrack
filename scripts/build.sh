#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
APP_NAME="Nexus"
DMG_NAME="Nexus"

TARGET="${1:-}"
if [[ -z "$TARGET" ]]; then
    case "$(uname -s)" in
        Darwin)  TARGET=".dmg" ;;
        *)       TARGET=".exe" ;;
    esac
fi
case "$TARGET" in
    dmg|.dmg) TARGET=".dmg" ;;
    exe|.exe) TARGET=".exe" ;;
    *) echo "Usage: $0 [.dmg|.exe]"; exit 1 ;;
esac

echo "==> Target: $TARGET  (project root: $PROJECT_ROOT)"

VENV_DIR="$PROJECT_ROOT/venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "==> Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
if [[ -f "$VENV_DIR/Scripts/activate" ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

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
    if command -v curl >/dev/null 2>&1; then
        curl -sSL -o "$out" "$url"
    else
        python -c "import urllib.request; urllib.request.urlretrieve('$url', '$out')"
    fi
}

echo "==> Downloading MediaPipe models..."
download_model "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" "$MODELS_DIR/hand.task"
download_model "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" "$MODELS_DIR/face.task"
download_model "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite" "$MODELS_DIR/object_detector.task"

echo "==> Cleaning previous build..."
rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist"

if [[ "$TARGET" == ".dmg" ]]; then
    if [[ "$(uname -s)" != "Darwin" ]]; then
        echo "ERROR: Build .dmg on macOS. Use: ./build.sh .exe on Windows."
        exit 1
    fi
    ICON_PNG="$PROJECT_ROOT/icon.png"
    ICON_ICNS="$PROJECT_ROOT/icon.icns"
    if [[ -f "$ICON_PNG" ]]; then
        echo "==> Building app icon from icon.png..."
        ICONSET="$PROJECT_ROOT/icon.iconset"
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
    echo "==> Running PyInstaller (Mac)..."
    pyinstaller --noconfirm track.spec
    APP_PATH="$PROJECT_ROOT/dist/$APP_NAME.app"
    if [[ ! -d "$APP_PATH" ]]; then
        echo "ERROR: $APP_NAME.app not found in dist/"
        exit 1
    fi
    echo "==> Creating DMG..."
    DMG_STAGE="$PROJECT_ROOT/dmg_stage"
    rm -rf "$DMG_STAGE"
    mkdir -p "$DMG_STAGE"
    cp -R "$APP_PATH" "$DMG_STAGE/"
    ln -s /Applications "$DMG_STAGE/Applications"
    DOWNLOAD_DMG="${HOME}/Downloads/${DMG_NAME}.dmg"
    rm -f "$DOWNLOAD_DMG"
    hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_STAGE" -ov -format UDZO "$DOWNLOAD_DMG"
    rm -rf "$DMG_STAGE"
    echo ""
    echo "==> Done (Mac)."
    echo "    App:  $APP_PATH"
    echo "    DMG:  $DOWNLOAD_DMG"
    exit 0
fi

if [[ "$TARGET" == ".exe" ]]; then
    if [[ "$(uname -s)" == "Darwin" ]]; then
        echo "ERROR: Build .exe on Windows. Use: ./build.sh .dmg on Mac."
        exit 1
    fi
    echo "==> Running PyInstaller (Windows)..."
    pyinstaller --noconfirm track.spec
    EXE_PATH="$PROJECT_ROOT/dist/$APP_NAME.exe"
    if [[ ! -f "$EXE_PATH" ]]; then
        EXE_PATH="$PROJECT_ROOT/dist/$APP_NAME/$APP_NAME.exe"
    fi
    if [[ ! -f "$EXE_PATH" ]]; then
        echo "ERROR: Nexus.exe not found in dist/"
        exit 1
    fi
    echo ""
    echo "==> Done (Windows)."
    echo "    Exe:  $EXE_PATH"
    if [[ -n "$USERPROFILE" ]]; then
        DOWNLOAD_EXE="${USERPROFILE}/Downloads/${DMG_NAME}.exe"
        cp "$EXE_PATH" "$DOWNLOAD_EXE" 2>/dev/null && echo "    Copy: $DOWNLOAD_EXE" || true
    fi
    exit 0
fi
