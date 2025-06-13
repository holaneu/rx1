from dataclasses import dataclass, field
from typing import Optional
import os

@dataclass
class FileSystemItem:
    id: str
    type: str  # 'file' or 'folder'
    title: str
    file_path: str

    @classmethod
    def from_path(cls, base_path: str, full_path: str, item_id: str, parent_id: Optional[str] = None) -> 'FileSystemItem':
        rel_path = os.path.relpath(full_path, base_path)
        item = cls(
            id=item_id,
            type='folder' if os.path.isdir(full_path) else 'file',
            title=os.path.basename(full_path),
            file_path=rel_path.replace('\\', '/')
        )
        
        if parent_id:
            setattr(item, 'parent', parent_id)
            
        if os.path.basename(full_path).startswith('.'):
            setattr(item, 'is_hidden', True)
            
        return item
