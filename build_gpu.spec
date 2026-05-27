import os 
import site
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

nvidia_dlls = []
try:
    for sp in site.getsitepackages():
        nvidia_path = os.path.join(sp, 'nvidia')
        if os.path.exists(nvidia_path):
            for root, dirs, files in os.walk(nvidia_path):
                for file in files:
                    if file.endswith('.dll'):
                        nvidia_dlls.append((os.path.join(root, file), '.'))
except Exception:
    pass

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=collect_dynamic_libs('ctranslate2') + nvidia_dlls,
    datas=collect_data_files('customtkinter'),
    hiddenimports=['faster_whisper', 'ctranslate2', 'sounddevice', 'groq', 'dotenv', 'omegaconf'] + collect_submodules('faster_whisper'),
)

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name='LangForge_GPU_Nvidia',
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name='LangForge_GPU_Nvidia')