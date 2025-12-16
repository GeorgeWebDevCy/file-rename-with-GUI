import sys
import os
import customtkinter
from cx_Freeze import setup, Executable

# Find customtkinter location
ctk_path = os.path.dirname(customtkinter.__file__)

build_exe_options = {
    "packages": ["customtkinter", "file_renamer", "threading", "re", "shutil", "pathlib", "uuid"],
    "include_files": [
        "README.md",
        (ctk_path, "customtkinter")  # Copy ctk data to lib/customtkinter
    ],
    "excludes": []
}

# Base set to "Win32GUI" to hide console
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="FileRenamer",
    version="1.0",
    description="Bulk File Renamer Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("gui_app.py", base=base, target_name="FileRenamer.exe")]
)
