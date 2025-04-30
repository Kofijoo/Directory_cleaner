import os

# Set your test directory here
source_dir = r"C:\Users\Joshua\Desktop"  # Use your full path here on Windows

# Define extension groups
image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]
video_extensions = [".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv"]
audio_extensions = [".mp3", ".wav", ".flac", ".aac", ".wma"]
document_extensions = [".pdf", ".docx", ".doc", ".txt", ".odt"]
app_extensions = [".exe", ".msi"]

def get_file_category(name, is_dir):
    if is_dir:
        return "Folder"
    
    extension = os.path.splitext(name)[1].lower()

    if extension in image_extensions:
        return "Image"
    elif extension in video_extensions:
        return "Video"
    elif extension in audio_extensions:
        return "Audio"
    elif extension in document_extensions:
        return "Document"
    elif extension in app_extensions:
        return "Executable"
    else:
        return "Other"

def scan_and_categorize_files(directory):
    print(f"📁 Scanning directory: {directory}\n")
    with os.scandir(directory) as entries:
        for entry in entries:
            category = get_file_category(entry.name, entry.is_dir())
            print(f"{entry.name:50} → {category}")

# Run the categorizer
scan_and_categorize_files(source_dir)
