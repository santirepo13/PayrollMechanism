"""
File operations for BroadSpec Payment Calculator.
"""
import os
import shutil
import tempfile
from typing import List, Optional, Tuple
from pathlib import Path

from broadspec.core.exceptions import StorageError, ValidationError


class FileOperations:
    """Handles file I/O operations."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.receipts_path = self.config.get('storage', {}).get('receipts_path', 'Receipts')
    
    def ensure_directory_exists(self, directory: str) -> None:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise StorageError(f"Failed to create directory {directory}: {str(e)}")
    
    def save_file(self, filepath: str, content: bytes) -> None:
        try:
            directory = os.path.dirname(filepath)
            if directory:
                self.ensure_directory_exists(directory)
            
            with open(filepath, 'wb') as f:
                f.write(content)
                
        except Exception as e:
            raise StorageError(f"Failed to save file {filepath}: {str(e)}")
    
    def load_file(self, filepath: str) -> bytes:
        try:
            if not os.path.exists(filepath):
                raise StorageError(f"File not found: {filepath}")
            
            with open(filepath, 'rb') as f:
                return f.read()
                
        except Exception as e:
            raise StorageError(f"Failed to load file {filepath}: {str(e)}")
    
    def copy_file(self, source: str, destination: str) -> None:
        try:
            if not os.path.exists(source):
                raise StorageError(f"Source file not found: {source}")
            
            directory = os.path.dirname(destination)
            if directory:
                self.ensure_directory_exists(directory)
            
            shutil.copy2(source, destination)
            
        except Exception as e:
            raise StorageError(f"Failed to copy file from {source} to {destination}: {str(e)}")
    
    def move_file(self, source: str, destination: str) -> None:
        try:
            if not os.path.exists(source):
                raise StorageError(f"Source file not found: {source}")
            
            directory = os.path.dirname(destination)
            if directory:
                self.ensure_directory_exists(directory)
            
            shutil.move(source, destination)
            
        except Exception as e:
            raise StorageError(f"Failed to move file from {source} to {destination}: {str(e)}")
    
    def delete_file(self, filepath: str) -> None:
        try:
            if not os.path.exists(filepath):
                return
            
            os.remove(filepath)
            
        except Exception as e:
            raise StorageError(f"Failed to delete file {filepath}: {str(e)}")
    
    def get_file_size(self, filepath: str) -> int:
        try:
            if not os.path.exists(filepath):
                return 0
            
            return os.path.getsize(filepath)
            
        except Exception as e:
            raise StorageError(f"Failed to get file size for {filepath}: {str(e)}")
    
    def file_exists(self, filepath: str) -> bool:
        return os.path.exists(filepath)
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        try:
            if not os.path.exists(directory):
                return []
            
            from glob import glob
            return glob(os.path.join(directory, pattern))
            
        except Exception as e:
            raise StorageError(f"Failed to list files in {directory}: {str(e)}")
    
    def create_temp_file(self, content: bytes, suffix: str = ".tmp") -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                return tmp.name
                
        except Exception as e:
            raise StorageError(f"Failed to create temporary file: {str(e)}")
    
    def open_with_system(self, filepath: str) -> None:
        try:
            if not os.path.exists(filepath):
                raise StorageError(f"File not found: {filepath}")
            
            if os.name == 'nt':
                os.startfile(filepath)
            else:
                try:
                    shutil.which('xdg-open') and os.system(f'xdg-open "{filepath}"')
                except Exception:
                    raise StorageError("Failed to open file with system application")
                    
        except Exception as e:
            raise StorageError(f"Failed to open file {filepath}: {str(e)}")
    
    def validate_filepath(self, filepath: str) -> bool:
        try:
            if '\x00' in filepath:
                return False
            
            normalized = os.path.normpath(filepath)
            if '..' in normalized.split(os.sep):
                return False
            
            if os.path.isabs(filepath):
                pass
            
            return True
            
        except Exception:
            return False
    
    def get_safe_filename(self, filename: str) -> str:
        if not filename:
            return "unnamed"
        
        import re
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
        sanitized = sanitized.rstrip(' .')
        
        if not sanitized:
            sanitized = "unnamed"
        
        return sanitized
    
    def get_file_extension(self, filepath: str) -> str:
        return os.path.splitext(filepath)[1].lower()
    
    def ensure_receipts_directory(self) -> str:
        self.ensure_directory_exists(self.receipts_path)
        return self.receipts_path
    
    def get_unique_filepath(self, directory: str, filename: str) -> str:
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{base} ({counter}){ext}"
            new_filepath = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_filepath):
                return new_filepath
            
            counter += 1
