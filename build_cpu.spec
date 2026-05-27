from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=collect_dynamic_libs('ctranslate2'),
    datas=collect_data_files('customtkinter'),
    hiddenimports=['faster_whisper', 'ctranslate2', 'sounddevice', 'groq', 'dotenv', 'omegaconf'] + collect_submodules('faster_whisper'),
)

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name='LangForge_CPU',
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name='LangForge_CPU')