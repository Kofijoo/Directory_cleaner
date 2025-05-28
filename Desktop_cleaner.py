import os
import shutil
import logging
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Global State
source_dir = config.get("source_directory", os.path.expanduser("~/Desktop"))
extension_groups = config["extension_groups"]
log_file = os.path.join(source_dir, "desktop_cleaner.log")
history_file = os.path.join(source_dir, "move_history.json")

# Setup logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Core Logic
def get_file_category(name, is_dir):
    if is_dir:
        return "Folder"
    extension = os.path.splitext(name)[1].lower()
    for category, extensions in extension_groups.items():
        if extension in extensions:
            return category
    return "Other"

def create_category_folders(base_path):
    for category in list(extension_groups.keys()) + ["Other"]:
        os.makedirs(os.path.join(base_path, category), exist_ok=True)

def move_file_to_category(file_path, category, base_path, history):
    dest_folder = os.path.join(base_path, category)
    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    try:
        shutil.move(file_path, dest_path)
        logging.info(f"Moved: {file_path} → {dest_path}")
        history.append({
            "original_path": file_path,
            "new_path": dest_path,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Failed to move {file_path}: {e}")

def save_history(history):
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

def organize_files(directory):
    logging.info(f"--- Starting desktop organization in: {directory} ---")
    create_category_folders(directory)
    history = []

    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name in extension_groups.keys():
                continue
            category = get_file_category(entry.name, entry.is_dir())
            if category != "Folder":
                move_file_to_category(entry.path, category, directory, history)

    save_history(history)
    logging.info(f"--- Completed desktop organization ---")

def undo_last_organize():
    if not os.path.exists(history_file):
        return False

    with open(history_file, "r") as f:
        history = json.load(f)

    for record in history:
        try:
            shutil.move(record["new_path"], record["original_path"])
            logging.info(f"Restored: {record['new_path']} → {record['original_path']}")
        except Exception as e:
            logging.error(f"Failed to restore {record['new_path']}: {e}")

    os.remove(history_file)
    logging.info("History cleared after undo.")
    return True

# GUI
class CleanerGUI:
    def __init__(self, master):
        self.master = master
        master.title("🧹 Desktop Cleaner")
        master.geometry("500x300")

        self.label = tk.Label(master, text="Selected Directory:")
        self.label.pack(pady=(10, 0))

        self.dir_var = tk.StringVar(value=source_dir)
        self.entry = tk.Entry(master, textvariable=self.dir_var, width=60)
        self.entry.pack(pady=5)

        self.browse_button = tk.Button(master, text="📁 Browse", command=self.browse)
        self.browse_button.pack(pady=5)

        self.organize_button = tk.Button(master, text="🚀 Organize", command=self.run_organize)
        self.organize_button.pack(pady=5)

        self.undo_button = tk.Button(master, text="↩️ Undo Last", command=self.run_undo)
        self.undo_button.pack(pady=5)

        self.log_button = tk.Button(master, text="📄 View Log", command=self.view_log)
        self.log_button.pack(pady=5)

        self.quit_button = tk.Button(master, text="🛑 Exit", command=master.quit)
        self.quit_button.pack(pady=5)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_var.set(path)

    def run_organize(self):
        dir_to_clean = self.dir_var.get()
        if os.path.exists(dir_to_clean):
            organize_files(dir_to_clean)
            messagebox.showinfo("Success", f"Organized files in:\n{dir_to_clean}")
        else:
            messagebox.showerror("Error", "Invalid directory.")

    def run_undo(self):
        if undo_last_organize():
            messagebox.showinfo("Undo", "Restored all files from last operation.")
        else:
            messagebox.showwarning("Undo", "No history file found to undo.")

    def view_log(self):
        if not os.path.exists(log_file):
            messagebox.showinfo("Log", "No log file found.")
            return
        with open(log_file, "r") as f:
            content = f.read()
        log_window = tk.Toplevel(self.master)
        log_window.title("📄 Cleaner Log")
        text_area = scrolledtext.ScrolledText(log_window, width=80, height=25)
        text_area.pack(padx=10, pady=10)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)

# Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerGUI(root)
    root.mainloop()
