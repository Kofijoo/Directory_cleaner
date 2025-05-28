import os
import shutil
import logging
import json
from datetime import datetime

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

source_dir = config["source_directory"]
extension_groups = config["extension_groups"]

log_file = os.path.join(source_dir, "desktop_cleaner.log")
history_file = os.path.join(source_dir, "move_history.json")

# Setup logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
        print(f"✅ Moved: {os.path.basename(file_path):50} → {category}")
    except Exception as e:
        logging.error(f"Failed to move {file_path}: {e}")
        print(f"❌ Failed to move {file_path}: {e}")

def save_history(history):
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

def organize_files(directory):
    logging.info(f"--- Starting desktop organization in: {directory} ---")
    print(f"\n🗂️ Organizing files in: {directory}")
    create_category_folders(directory)
    history = []

    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name in extension_groups.keys():
                continue

            category = get_file_category(entry.name, entry.is_dir())
            logging.info(f"Categorized: {entry.name} → {category}")

            if category != "Folder":
                move_file_to_category(entry.path, category, directory, history)

    save_history(history)
    logging.info(f"--- Completed desktop organization ---\n")

def undo_last_organize():
    if not os.path.exists(history_file):
        print("🚫 No history file found. Cannot undo.")
        return

    with open(history_file, "r") as f:
        history = json.load(f)

    print(f"\n🔄 Restoring {len(history)} files from history...")
    for record in history:
        try:
            shutil.move(record["new_path"], record["original_path"])
            logging.info(f"Restored: {record['new_path']} → {record['original_path']}")
            print(f"↩️ Restored: {os.path.basename(record['new_path'])}")
        except Exception as e:
            logging.error(f"Failed to restore {record['new_path']}: {e}")
            print(f"❌ Failed to restore {record['new_path']}: {e}")

    os.remove(history_file)
    logging.info("History cleared after undo.")

# Uncomment to run:
# organize_files(source_dir)
# undo_last_organize()
