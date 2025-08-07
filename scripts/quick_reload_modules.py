"""Simple one-command reload script"""
import sys
from pathlib import Path

# Add root directory to path (going up one level from scripts folder)
root_dir = Path(__file__).resolve().parents[1]  # parent of the scripts directory = root
sys.path.insert(0, str(root_dir))

from app.utils.module_manager import ModuleManager

if __name__ == '__main__':
    print("Reloading all modules...")
    manager = ModuleManager()
    manager.full_reload()
    print("Done!")