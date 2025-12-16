import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import file_renamer

# Configure appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FileRenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Renamer GUI")
        self.geometry("800x600")

        self.selected_folder = None
        self.is_running = False

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Log area expands

        # 1. Header & Selection
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="Bulk File Renamer", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(side="top", pady=5)

        self.btn_select = ctk.CTkButton(self.header_frame, text="Select Target Folder", command=self.select_folder)
        self.btn_select.pack(side="left", padx=10, pady=10)

        self.label_path = ctk.CTkLabel(self.header_frame, text="No folder selected", text_color="gray")
        self.label_path.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # 2. Controls
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.mode_var = ctk.StringVar(value="Dry Run")
        self.switch_mode = ctk.CTkSegmentedButton(self.controls_frame, values=["Dry Run", "Apply Changes"], variable=self.mode_var, command=self.on_mode_change)
        self.switch_mode.pack(side="left", padx=10, pady=10)

        self.btn_run = ctk.CTkButton(self.controls_frame, text="RUN RENAMER", command=self.run_process, fg_color="green", state="disabled")
        self.btn_run.pack(side="right", padx=10, pady=10)

        # 3. Log Area
        self.textbox_log = ctk.CTkTextbox(self, width=760)
        self.textbox_log.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_log.configure(state="disabled", font=("Consolas", 12))

        # Initial log message
        self.log_message("Welcome! Select a folder to get started.\n")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = Path(folder)
            self.label_path.configure(text=str(self.selected_folder), text_color=("black", "white"))
            self.btn_run.configure(state="normal")
            self.log_message(f"Selected folder: {self.selected_folder}\n")

    def on_mode_change(self, value):
        if value == "Apply Changes":
            self.btn_run.configure(fg_color="#b30000", hover_color="#800000") # Red warning color
        else:
            self.btn_run.configure(fg_color="green", hover_color="#006400")

    def log_message(self, message):
        """Thread-safe logging to the text box."""
        def _update():
            self.textbox_log.configure(state="normal")
            self.textbox_log.insert("end", str(message) + "\n")
            self.textbox_log.see("end")
            self.textbox_log.configure(state="disabled")
        
        self.after(0, _update)

    def run_process(self):
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return

        if self.is_running:
            return

        mode = self.mode_var.get()
        dry_run = (mode == "Dry Run")
        
        if not dry_run:
            confirm = messagebox.askyesno("Confirm Apply", "This will PERMANENTLY rename files.\nAre you sure?")
            if not confirm:
                return

        self.is_running = True
        self.btn_run.configure(state="disabled", text="Running...")
        self.btn_select.configure(state="disabled")
        self.switch_mode.configure(state="disabled")
        
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("1.0", "end")
        self.textbox_log.configure(state="disabled")

        thread = threading.Thread(target=self.worker_task, args=(dry_run,))
        thread.start()

    def worker_task(self, dry_run):
        try:
            file_renamer.rename_tree(self.selected_folder, dry_run=dry_run, log_callback=self.log_message)
            self.log_message("\n--- DONE ---")
        except Exception as e:
            self.log_message(f"\nERROR: {e}")
        finally:
            self.after(0, self.on_process_finished)

    def on_process_finished(self):
        self.is_running = False
        self.btn_run.configure(state="normal", text="RUN RENAMER")
        self.btn_select.configure(state="normal")
        self.switch_mode.configure(state="normal")


if __name__ == "__main__":
    app = FileRenamerApp()
    app.mainloop()
