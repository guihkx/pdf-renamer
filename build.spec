# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

SELF_PATH = str(Path(".").absolute())

if sys.platform == 'win32':
    binaries_to_add: list[tuple[Path, str]] = [
        (Path('./env/deps/tesseract/tesseract.exe'), '.'),
        (Path('./env/deps/poppler/pdfinfo.exe'), '.'),
        (Path('./env/deps/poppler/pdftoppm.exe'), '.'),
        # (Path('./env/deps/poppler/pdftocairo.exe'), 'poppler')
    ]
    datas_to_add: list[tuple[Path, str]] = [
        (Path('./env/deps/tesseract/tessdata/por.traineddata'), 'tessdata')
    ]
else:
    binaries_to_add: list[tuple[Path, str]] = [
        (Path('/usr/bin/tesseract'), '.'),
        (Path('/usr/bin/pdfinfo'), '.'),
        (Path('/usr/bin/pdftoppm'), '.'),
        # (Path('/usr/bin/pdftocairo'), 'poppler')
    ]
    datas_to_add: list[tuple[Path, str]] = [
        (Path('/usr/share/tessdata/por.traineddata'), 'tessdata')
    ]

binaries = []
datas = []

for source_path, dest_path in binaries_to_add:
    if not source_path.exists():
        raise FileNotFoundError(str(source_path))
    binaries.append((source_path, dest_path))

for source_path, dest_path in datas_to_add:
    if not source_path.exists():
        raise FileNotFoundError(str(source_path))
    datas.append((source_path, dest_path))

a = Analysis(
    ['pdf_renamer.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pdf_renamer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
