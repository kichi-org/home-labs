import os
import shutil
import re
import sys

# Configuration
SOURCE_DIR = "/mnt/data/torrents/"
DESTINATION_DIR = "/mnt/data/videos/TVB/"

def find_existing_folder(show_name, base_dir):
    """Check if a folder starting with show_name already exists."""
    if not os.path.exists(base_dir):
        return None
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path) and folder.startswith(show_name):
            return folder_path
    return None

def extract_episode_number(filename):
    """Extract episode number using regex."""
    # Try patterns: EP01, E01, or digits before .mp4
    match = re.search(r'EP?(\d+)', filename, re.IGNORECASE)
    if match:
        return match.group(1).zfill(2)
    
    # Fallback: get last number in filename
    match = re.search(r'(\d+)(?=\.mp4$)', filename)
    return match.group(1).zfill(2) if match else None

def process_files(dry_run=True):
    """Process all TVBOXNOW directories."""
    if not os.path.exists(SOURCE_DIR):
        print(f"ERROR: Source directory not found: {SOURCE_DIR}")
        return
    
    print(f"Running in {'DRY-RUN' if dry_run else 'LIVE'} mode\n")
    files_moved = 0
    
    for item in os.listdir(SOURCE_DIR):
        item_path = os.path.join(SOURCE_DIR, item)
        
        if not os.path.isdir(item_path) or not item.startswith("TVBOXNOW"):
            continue
        
        # Extract clean show name
        show_name = (item.replace("TVBOXNOW ", "")
                         .replace(" H265", "")
                         .replace("_H265", "")
                         .strip())
        
        # Check for existing folder or create new one
        existing_folder = find_existing_folder(show_name, DESTINATION_DIR)
        
        if existing_folder:
            destination_folder = existing_folder
            print(f"Using existing folder: {os.path.basename(destination_folder)}")
        else:
            from datetime import datetime
            year = datetime.now().year
            destination_folder = os.path.join(DESTINATION_DIR, f"{show_name} ({year})")
            
            if dry_run:
                print(f"[DRY-RUN] Would create: {destination_folder}")
            else:
                os.makedirs(destination_folder, exist_ok=True)
                print(f"Created: {destination_folder}")
        
        # Process MP4 files
        for file in os.listdir(item_path):
            if not file.endswith(".mp4"):
                continue
            
            episode_number = extract_episode_number(file)
            if not episode_number:
                print(f"WARNING: Could not extract episode from {file}")
                continue
            
            new_filename = f"{show_name} {episode_number}.mp4"
            source_path = os.path.join(item_path, file)
            destination_path = os.path.join(destination_folder, new_filename)
            
            if dry_run:
                print(f"[DRY-RUN] {file} -> {new_filename}")
            else:
                try:
                    shutil.move(source_path, destination_path)
                    print(f"Moved: {file} -> {new_filename}")
                    files_moved += 1
                except Exception as e:
                    print(f"ERROR moving {file}: {e}")
    
    print(f"\nCompleted. Files moved: {files_moved}")

if __name__ == "__main__":
    # Get dry-run setting from environment variable or command line
    dry_run_env = os.getenv("DRY_RUN", "true").lower()
    dry_run = dry_run_env in ["true", "1", "yes"]
    
    # Override with command line argument if provided
    if len(sys.argv) > 1:
        dry_run = sys.argv[1].lower() not in ["false", "0", "no", "live"]
    
    process_files(dry_run=dry_run)