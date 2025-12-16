import customtkinter as ctk
import os
import sys
import shutil
import winshell
from win32com.client import Dispatch
from pathlib import Path
import threading
import time

# Configure appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

APP_NAME = "FileRenamer"
EXE_NAME = "FileRenamer.exe"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} Setup")
        self.geometry("600x400")
        self.resizable(False, False)

        # Install Path: AppData/Local/Programs/FileRenamer
        self.install_dir = Path(os.getenv('LOCALAPPDATA')) / "Programs" / APP_NAME
        
        self.init_ui()

    def init_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, height=80)
        self.header.pack(side="top", fill="x")
        
        self.title_lbl = ctk.CTkLabel(self.header, text=f"Install {APP_NAME}", font=("Arial", 24, "bold"))
        self.title_lbl.place(relx=0.05, rely=0.5, anchor="w")

        # Main Content
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        self.info_lbl = ctk.CTkLabel(self.content, text=f"This wizard will install {APP_NAME} on your computer.\n\nClick Install to continue.", font=("Arial", 14), justify="left")
        self.info_lbl.pack(pady=40)
        
        # Progress Bar (Hidden initially)
        self.progress = ctk.CTkProgressBar(self.content, width=400)
        self.progress.set(0)
        
        # Bottom Bar
        self.bottom_bar = ctk.CTkFrame(self, height=60)
        self.bottom_bar.pack(side="bottom", fill="x")

        self.btn_cancel = ctk.CTkButton(self.bottom_bar, text="Cancel", fg_color="gray", command=self.destroy)
        self.btn_cancel.pack(side="left", padx=20, pady=15)

        self.btn_install = ctk.CTkButton(self.bottom_bar, text="Install", command=self.start_install)
        self.btn_install.pack(side="right", padx=20, pady=15)

    def create_shortcut(self, target_path, shortcut_path):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(target_path)
        shortcut.WorkingDirectory = str(target_path.parent)
        shortcut.IconLocation = str(target_path)
        shortcut.save()

    def start_install(self):
        self.btn_install.configure(state="disabled")
        self.btn_cancel.configure(state="disabled")
        self.info_lbl.configure(text="Installing...")
        self.progress.pack(pady=20)
        
        thread = threading.Thread(target=self.run_installation)
        thread.start()

    def run_installation(self):
        try:
            # 1. Prepare Directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.update_progress(0.2)

            # 2. Copy Executable
            src_exe = resource_path(EXE_NAME)
            if not os.path.exists(src_exe):
                raise FileNotFoundError(f"Installer corrupted: {EXE_NAME} not found inside bundle.")
            
            dst_exe = self.install_dir / EXE_NAME
            shutil.copy2(src_exe, dst_exe)
            self.update_progress(0.6)

            # 3. Create Shortcuts
            # Desktop
            desktop = Path(winshell.desktop())
            self.create_shortcut(dst_exe, desktop / f"{APP_NAME}.lnk")
            
            # Start Menu
            start_menu = Path(winshell.programs())
            self.create_shortcut(dst_exe, start_menu / f"{APP_NAME}.lnk")
            
            self.update_progress(1.0)
            self.after(0, self.installation_complete)

        except Exception as e:
            self.after(0, lambda: self.installation_failed(str(e)))

    def update_progress(self, val):
        self.after(0, lambda: self.progress.set(val))

    def installation_complete(self):
        self.info_lbl.configure(text="Installation Complete!\n\nYou can find the app on your Desktop and Start Menu.")
        self.btn_install.configure(text="Exit", state="normal", command=self.destroy)
        self.progress.pack_forget()

    def installation_failed(self, error):
        self.info_lbl.configure(text=f"Installation Failed:\n{error}", text_color="red")
        self.btn_cancel.configure(state="normal")

if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
