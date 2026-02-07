# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

models_dir = os.path.join(SPECPATH, 'models')
datas = [(models_dir, 'models')] if os.path.isdir(models_dir) else []
binaries = []

try:
    mp_datas, mp_binaries, mp_hidden = collect_all('mediapipe')
    datas += mp_datas
    binaries += mp_binaries
    mp_hiddenimports = mp_hidden
except Exception:
    mp_hiddenimports = []

a = Analysis(
    ['track.py'],
    pathex=[SPECPATH],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'cv2',
        'numpy',
        'mediapipe',
        'mediapipe.tasks',
        'mediapipe.tasks.python',
        'mediapipe.tasks.python.vision',
        'mediapipe.tasks.python.vision.pose_landmarker',
        'mediapipe.tasks.python.core',
        'mediapipe.tasks.python.core.optional_dependencies',
        'mediapipe.python',
        'mediapipe.python._framework_bindings',
        'mediapipe.calculators',
        'mediapipe.framework',
        'mediapipe.framework.formats',
        'mediapipe.modules',
    ] + (list(mp_hiddenimports) if mp_hiddenimports else []),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Nexus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Nexus',
)

if sys.platform == 'darwin':
    _icon_path = os.path.join(SPECPATH, 'icon.icns')
    app = BUNDLE(
        coll,
        name='Nexus.app',
        icon=_icon_path if os.path.isfile(_icon_path) else None,
        bundle_identifier='com.nexus.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': True,
            'CFBundleName': 'Nexus',
            'CFBundleDisplayName': 'Nexus',
            'CFBundleGetInfoString': 'Hand and face tracking with MediaPipe',
            'CFBundleVersion': '1.0.0',
            'NSCameraUsageDescription': 'This app uses the camera for hand and face tracking.',
        },
    )
