import os
import shutil
import logging
from datetime import datetime

# Configuration
source_dir = r"C:\Users\Joshua\Desktop"
log_file = os.path.join(source_dir, "desktop_cleaner.log")

# Setup logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Extension groups
extension_groups = {
    "Image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "Video": [".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".wma"],
    "Document": [".pdf", ".docx", ".doc", ".txt", ".odt"],
    "Executable": [".exe", ".msi"]
}

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

def move_file_to_category(file_path, category, base_path):
    dest_folder = os.path.join(base_path, category)
    try:
        shutil.move(file_path, dest_folder)
        logging.info(f"Moved: {os.path.basename(file_path)} → {category}")
        print(f"✅ Moved: {os.path.basename(file_path):50} → {category}")
    except Exception as e:
        logging.error(f"Failed to move {file_path}: {e}")
        print(f"❌ Failed to move {file_path}: {e}")

def organize_files(directory):
    logging.info(f"--- Starting desktop organization in: {directory} ---")
    print(f"\n🗂️ Organizing files in: {directory}")
    create_category_folders(directory)

    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir() and entry.name in extension_groups.keys():
                continue  # Skip already created folders

            category = get_file_category(entry.name, entry.is_dir())
            logging.info(f"Categorized: {entry.name} → {category}")

            if category != "Folder":
                move_file_to_category(entry.path, category, directory)

    logging.info(f"--- Completed desktop organization ---\n")

# Run the organizer
organize_files(source_dir)
