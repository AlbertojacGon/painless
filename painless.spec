# -*- mode: python ; coding: utf-8 -*-
from os import path
import shutil
import mne
import eeglabio

global DISTPATH

block_cipher = None

script_1 = Analysis(
    ['1_Thresholds5.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
script_1.datas += Tree(path.dirname(mne.__file__), prefix='mne', excludes='__pycache__')
script_1.datas += Tree(path.dirname(eeglabio.__file__), prefix='eeglabio', excludes='__pycache__')
script_1_pyz = PYZ(script_1.pure, script_1.zipped_data, cipher=block_cipher)
script_1_exe = EXE(
    script_1_pyz,
    script_1.scripts,
    [],
    exclude_binaries=True,
    name='1_Thresholds5',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

script_2 = Analysis(
    ['2_TSP_CPM.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
script_2_pyz = PYZ(script_2.pure, script_2.zipped_data, cipher=block_cipher)
script_2_exe = EXE(
    script_2_pyz,
    script_2.scripts,
    [],
    exclude_binaries=True,
    name='2_TSP_CPM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

script_3 = Analysis(
    ['3_HPT_CDT_CPT.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
script_3_pyz = PYZ(script_3.pure, script_3.zipped_data, cipher=block_cipher)
script_3_exe = EXE(
    script_3_pyz,
    script_3.scripts,
    [],
    exclude_binaries=True,
    name='3_HPT_CDT_CPT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

script_4 = Analysis(
    ['4_Offset_Analgesia.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
script_4_pyz = PYZ(script_4.pure, script_4.zipped_data, cipher=block_cipher)
script_4_exe = EXE(
    script_4_pyz,
    script_4.scripts,
    [],
    exclude_binaries=True,
    name='4_Offset_Analgesia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

script_5 = Analysis(
    ['5_resting_EEG_COLD.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
script_5_pyz = PYZ(script_5.pure, script_5.zipped_data, cipher=block_cipher)
script_5_exe = EXE(
    script_5_pyz,
    script_5.scripts,
    [],
    exclude_binaries=True,
    name='5_resting_EEG_COLD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

script_6 = Analysis(
    ['6_Cheps_EEG.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
script_6.datas += Tree(path.dirname(mne.__file__), prefix='mne', excludes='__pycache__')
script_6.datas += Tree(path.dirname(eeglabio.__file__), prefix='eeglabio', excludes='__pycache__')
script_6_pyz = PYZ(script_6.pure, script_6.zipped_data, cipher=block_cipher)
script_6_exe = EXE(
    script_6_pyz,
    script_6.scripts,
    [],
    exclude_binaries=True,
    name='6_Cheps_EEG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    script_1_exe,
    script_1.binaries,
    script_1.zipfiles,
    script_1.datas,
    script_2_exe,
    script_2.binaries,
    script_2.zipfiles,
    script_2.datas,
    script_3_exe,
    script_3.binaries,
    script_3.zipfiles,
    script_3.datas,
    script_4_exe,
    script_4.binaries,
    script_4.zipfiles,
    script_4.datas,
    script_5_exe,
    script_5.binaries,
    script_5.zipfiles,
    script_5.datas,
    script_6_exe,
    script_6.binaries,
    script_6.zipfiles,
    script_6.datas,
    name='painless'
)

icon_location = path.join('.', 'painlessLogo.ico')
#target_location = path.join(DISTPATH, 'script_overview', 'painless')
#shutil.copy(icon_location, target_location)
target_location = path.join(DISTPATH, 'painless')
shutil.copy(icon_location, target_location)