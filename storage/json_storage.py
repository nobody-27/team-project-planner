import json
import os
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exceptions import StorageError

# Platform-specific imports
if os.name != 'nt':  # Unix/Linux
    import fcntl

class JsonStorage:
    """
    Handle JSON file storage operations with atomic writes and file locking
    This was honestly the hardest part - making sure data doesn't get corrupted
    """
    
    def __init__(self, db_path: str = "db"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)  # create db folder if it doesn't exist
        
    def _get_file_path(self, filename: str) -> Path:
        """Get full path for a database file"""
        return self.db_path / f"{filename}.json"
    
    def _acquire_lock(self, file_handle):
        """Acquire exclusive lock on file (Windows/Unix compatible)"""
        if os.name == 'nt':  # Windows
            import msvcrt
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:  # Unix/Linux
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    
    def _release_lock(self, file_handle):
        """Release file lock"""
        if os.name == 'nt':  # Windows
            import msvcrt
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:  # Unix/Linux
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
    
    def read(self, filename: str) -> List[Dict[str, Any]]:
        """Read data from JSON file"""
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                if os.name != 'nt':  # Skip locking on Windows for reads
                    self._acquire_lock(f)
                try:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
                finally:
                    if os.name != 'nt':
                        self._release_lock(f)
        except Exception as e:
            raise StorageError(f"Failed to read {filename}: {str(e)}")
    
    def write(self, filename: str, data: List[Dict[str, Any]]):
        """Write data to JSON file atomically - learned this pattern from stackoverflow"""
        file_path = self._get_file_path(filename)
        
        try:
            # Write to temporary file first to avoid corruption
            with tempfile.NamedTemporaryFile(mode='w', dir=self.db_path, 
                                           delete=False, suffix='.tmp') as tmp_file:
                json.dump(data, tmp_file, indent=2)  # pretty print for debugging
                tmp_path = tmp_file.name
            
            # Atomic rename - this ensures we never have half-written files
            if os.name == 'nt':  # Windows needs special handling
                if file_path.exists():
                    os.remove(file_path)  # Windows can't rename over existing files
            os.rename(tmp_path, file_path)
            
        except Exception as e:
            # Clean up temp file if something went wrong
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise StorageError(f"Failed to write {filename}: {str(e)}")
    
    def find_by_id(self, filename: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Find a record by ID"""
        data = self.read(filename)
        for record in data:
            if record.get('id') == id_value:
                return record
        return None
    
    def find_by_field(self, filename: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Find records by field value"""
        data = self.read(filename)
        return [record for record in data if record.get(field) == value]
    
    def create(self, filename: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        data = self.read(filename)
        data.append(record)
        self.write(filename, data)
        return record
    
    def update(self, filename: str, id_value: str, updates: Dict[str, Any]) -> bool:
        """Update a record by ID"""
        data = self.read(filename)
        for i, record in enumerate(data):
            if record.get('id') == id_value:
                data[i].update(updates)
                self.write(filename, data)
                return True
        return False
    
    def delete(self, filename: str, id_value: str) -> bool:
        """Delete a record by ID"""
        data = self.read(filename)
        original_length = len(data)
        data = [record for record in data if record.get('id') != id_value]
        
        if len(data) < original_length:
            self.write(filename, data)
            return True
        return False