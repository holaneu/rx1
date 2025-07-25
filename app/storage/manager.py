import os
import hashlib
from typing import Dict, List, Optional, Set
from .models import FileSystemItem

class FileStorageManager:
    def __init__(self, base_path: str, skip_folders: Optional[List[str]] = None):
        self.base_path = os.path.abspath(base_path)
        # Store skip_folders as a set of lowercase names for fast lookup
        self.skip_folders: Set[str] = set(f.lower() for f in (skip_folders or []))

    def _generate_id(self, path: str) -> str:
        """Generate a unique ID for a file/folder based on its path"""
        return hashlib.md5(path.encode()).hexdigest()[:12]

    def scan_directory(self) -> Dict[str, FileSystemItem]:
        items: Dict[str, FileSystemItem] = {}
        folders: List[tuple] = []
        files: List[tuple] = []
        
        for root, dirs, filenames in os.walk(self.base_path):
            # Filter out skipped folders from dirs so os.walk won't descend into them
            dirs[:] = [d for d in dirs if d.lower() not in self.skip_folders]
            # Skip processing if current directory is a skipped folder
            if os.path.basename(root).lower() in self.skip_folders:
                continue

            # Process current directory
            if root != self.base_path:  # Skip base directory itself
                dir_id = self._generate_id(root)
                parent_dir = os.path.dirname(root)
                parent_id = self._generate_id(parent_dir) if parent_dir != self.base_path else None
                folder_item = FileSystemItem.from_path(
                    self.base_path, root, dir_id, parent_id
                )
                # Use folder name for sorting instead of full path
                folder_name = os.path.basename(root).lower()
                folders.append((folder_name, dir_id, folder_item))

            # Process files in current directory
            for file in filenames:
                # Skip files inside skipped folders
                if os.path.basename(root).lower() in self.skip_folders:
                    continue
                full_path = os.path.join(root, file)
                file_id = self._generate_id(full_path)
                parent_id = None if root == self.base_path else self._generate_id(root)
                file_item = FileSystemItem.from_path(
                    self.base_path, full_path, file_id, parent_id
                )
                # Use filename for sorting instead of full path
                files.append((file.lower(), file_id, file_item))

        # Sort folders and files by their names
        folders.sort(key=lambda x: x[0])
        files.sort(key=lambda x: x[0])
        
        # Add folders first
        for _, dir_id, folder_item in folders:
            items[dir_id] = folder_item
            
        # Then add files
        for _, file_id, file_item in files:
            items[file_id] = file_item

        return items

    def get_structure(self) -> Dict:
        """Returns a JSON-serializable structure of the file system"""
        items = self.scan_directory()
        return {
            'items': list(items.values()),
            'total': len(items)
        }
