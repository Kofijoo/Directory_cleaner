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

# Config values
source_dir = config.get("source_directory", os.path.expanduser("~/Desktop"))
extension_groups = config.get("extension_groups", {})
excluded_files = config.get("excluded_files", [])
custom_folder_names = config.get("custom_folder_names", {})
archive_config = config.get("archive", {})
archive_enabled = archive_config.get("enabled", False)
archive_days_old = archive_config.get("days_old", 30)


# Log & history paths
log_file = os.path.join(source_dir, "desktop_cleaner.log")
history_file = os.path.join(source_dir, "move_history.json")

# Setup logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 🧱 Resolve custom folder name or default
def resolve_folder_name(category):
    return custom_folder_names.get(category, category)

# 🧱 Categorize file
def get_file_category(name, is_dir):
    if is_dir:
        return "Folder"
    extension = os.path.splitext(name)[1].lower()
    for category, extensions in extension_groups.items():
        if extension in extensions:
            return category
    return "Other"

# 🧱 Create folders
def create_category_folders(base_path):
    for category in list(extension_groups.keys()) + ["Other"]:
        folder_name = resolve_folder_name(category)
        os.makedirs(os.path.join(base_path, folder_name), exist_ok=True)

# 🧱 Move files
def move_file_to_category(file_path, category, base_path, history):
    folder_name = resolve_folder_name(category)
    dest_folder = os.path.join(base_path, folder_name)
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

# 🧱 Save history
def save_history(history):
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

# 🧱 Organize entry point
def organize_files(directory):
    logging.info(f"--- Starting organization in: {directory} ---")
    create_category_folders(directory)
    history = []

    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.name in excluded_files:
                logging.info(f"Skipped (excluded): {entry.name}")
                continue
            if entry.is_dir() and entry.name in extension_groups.keys():
                continue

            category = get_file_category(entry.name, entry.is_dir())
            if category != "Folder":
                move_file_to_category(entry.path, category, directory, history)

    save_history(history)
    archive_old_files(directory)
    logging.info(f"--- Completed organization ---")

# 🧱 Undo move operation
def undo_last_organize():
    if not os.path.exists(history_file):
        return False

    with open(history_file, "r") as f:
        history = json.load(f)

    for record in history:
        original_name = os.path.basename(record["original_path"])
        if original_name in excluded_files:
            logging.info(f"Skipped restore (excluded): {record['original_path']}")
            continue
        try:
            shutil.move(record["new_path"], record["original_path"])
            logging.info(f"Restored: {record['new_path']} → {record['original_path']}")
        except Exception as e:
            logging.error(f"Failed to restore {record['new_path']}: {e}")

    os.remove(history_file)
    logging.info("History cleared after undo.")
    return True

# 🧱 GUI Interface
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
    import time
from zipfile import ZipFile

def archive_old_files(base_path):
    if not archive_enabled:
        return

    threshold_seconds = archive_days_old * 86400  # Convert days to seconds
    now = time.time()
    archived_files = []

    for category in list(extension_groups.keys()) + ["Other"]:
        folder_name = resolve_folder_name(category)
        category_path = os.path.join(base_path, folder_name)
        if not os.path.exists(category_path):
            continue

        zip_path = os.path.join(base_path, f"{folder_name}_Archive.zip")
        with ZipFile(zip_path, 'a') as archive:
            for item in os.listdir(category_path):
                item_path = os.path.join(category_path, item)
                if os.path.isfile(item_path):
                    age = now - os.path.getmtime(item_path)
                    if age > threshold_seconds:
                        try:
                            archive.write(item_path, arcname=os.path.join(folder_name, item))
                            os.remove(item_path)
                            archived_files.append(item)
                            logging.info(f"Archived: {item_path} → {zip_path}")
                        except Exception as e:
                            logging.error(f"Failed to archive {item_path}: {e}")

    if archived_files:
        logging.info(f"Archived {len(archived_files)} files.")


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

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerGUI(root)
    root.mainloop()
