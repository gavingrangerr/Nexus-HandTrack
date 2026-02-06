@echo off
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%
set APP_NAME=Nexus

set TARGET=%~1
if "%TARGET%"=="" set TARGET=.exe
if /i "%TARGET%"=="exe" set TARGET=.exe
if /i "%TARGET%"==".exe" set TARGET=.exe
if not "%TARGET%"==".exe" (
    echo Usage: build.bat [.exe]
    exit /b 1
)

echo ==^> Target: %TARGET%
echo ==^> Project root: %PROJECT_ROOT%

if not exist "venv\Scripts\activate.bat" (
    echo ==^> Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo ==^> Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

if not exist "models" mkdir models
echo ==^> Downloading MediaPipe models...
python -c "import urllib.request,os; m=('hand.task','face.task','object_detector.task'); u=('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task','https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task','https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite'); o=('models/hand.task','models/face.task','models/object_detector.task'); [urllib.request.urlretrieve(u[i], o[i]) if not os.path.isfile(o[i]) else None for i in range(3)]"
if not exist "models\object_detector.task" python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite', 'models/object_detector.task')"

echo ==^> Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo ==^> Running PyInstaller (Windows)...
pyinstaller --noconfirm track.spec

set EXE_PATH=%PROJECT_ROOT%\dist\%APP_NAME%\%APP_NAME%.exe
if not exist "%EXE_PATH%" set EXE_PATH=%PROJECT_ROOT%\dist\%APP_NAME%.exe
if not exist "%EXE_PATH%" (
    echo ERROR: Nexus.exe not found in dist\
    exit /b 1
)

echo.
echo ==^> Done (Windows).
echo     Exe:  %EXE_PATH%
if defined USERPROFILE (
    set DOWNLOAD_EXE=%USERPROFILE%\Downloads\Nexus.exe
    copy /Y "%EXE_PATH%" "%DOWNLOAD_EXE%" >nul 2>&1 && echo     Copy: %DOWNLOAD_EXE%
)
exit /b 0
