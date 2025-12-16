# Bulk File Renamer GUI

A modern, cross-platform GUI application for batch renaming files and folders based on specific capitalization and numbering rules.

## Features

- **Recursive Renaming**: Processes all files and subfolders in a selected directory.
- **Rules**:
    - **Folders**: Converted to ALL CAPS. Trailing ` (n)` is removed.
    - **Files**: First letter capitalized, rest lowercase. Trailing ` (n)` removed. Extension preserved.
- **Dry Run Mode**: Preview changes safely with a detailed log before applying them.
- **Conflict Handling**: Automatically handles file/folder collisions by merging or renaming via temporary paths.

## Installation

1.  **Install Python**: Ensure you have Python 3.7+ installed.
2.  **Install Dependencies**:
    ```bash
    pip install customtkinter
    ```
    *(Optional) If you want to build the executable yourself:*
    ```bash
    pip install pyinstaller
    ```

## Usage

### Running from Source
1.  Open a terminal in this folder.
2.  Run the app:
    ```bash
    python gui_app.py
    ```
3.  **Select Target Folder**: Click the button to choose the directory you want to clean up.
4.  **Dry Run**: Use the toggle to stay in "Dry Run" mode (default). Click "RUN RENAMER" to see what would happen in the log.
5.  **Apply**: Switch to "Apply Changes". The button will turn red to warn you. Click to rename everything effectively.

### Building the Executable (Windows)
Double-click `build_exe.bat` (if available) or run:
```bash
pyinstaller --noconfirm --onefile --windowed --name "FileRenamer" --clean gui_app.py
```
The standalone `.exe` will be in the `dist` folder.

### Creating a Setup Wizard (Installer)
To create a standard `setup.exe` that installs the program to "Program Files":
1.  **Download Inno Setup**: [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php).
2.  **Build the Exe**: Run `build_exe.bat` first to ensure `dist/FileRenamer.exe` exists.
3.  **Compile Script**: Right-click `setup.iss` and choose "Compile".
4.  **Result**: The installer (`FileRenamer_Setup.exe`) will appear in the `installer` folder.
