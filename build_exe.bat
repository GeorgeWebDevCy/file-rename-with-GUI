@echo off
echo ===========================================
echo       File Renamer GUI - Builder
echo ===========================================
echo.

echo [1/3] Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Building Executable...
pyinstaller --noconfirm --onefile --windowed --name "FileRenamer" --clean gui_app.py
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller failed.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Build Complete!
echo The executable is located in the 'dist' folder.
echo.
pause
