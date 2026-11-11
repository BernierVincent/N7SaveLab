@echo off
setlocal
REM Install with: python -m pip install -e . pyinstaller
REM This starts with --onedir, which is easier to debug.
python -m PyInstaller --noconfirm --clean --onedir --name N7SaveLab --paths src launcher.py
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)
echo Built dist\N7SaveLab\N7SaveLab.exe
echo For a single EXE later, use --onefile instead of --onedir.
