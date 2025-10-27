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
        """Initialize file operations with configuration."""
        self.config = config or {}
        self.receipts_path = self.config.get('storage', {}).get('receipts_path', 'Receipts')
    
    def ensure_directory_exists(self, directory: str) -> None:
        """Ensure a directory exists, create if it doesn't."""
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise StorageError(f"Failed to create directory {directory}: {str(e)}")
    
    def save_file(self, filepath: str, content: bytes) -> None:
        """
        Save content to a file.
        
        Args:
            filepath: Path to the file
            content: Content to save
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory:
                self.ensure_directory_exists(directory)
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(content)
                
        except Exception as e:
            raise StorageError(f"Failed to save file {filepath}: {str(e)}")
    
    def load_file(self, filepath: str) -> bytes:
        """
        Load content from a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            File content as bytes
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(filepath):
                raise StorageError(f"File not found: {filepath}")
            
            with open(filepath, 'rb') as f:
                return f.read()
                
        except Exception as e:
            raise StorageError(f"Failed to load file {filepath}: {str(e)}")
    
    def copy_file(self, source: str, destination: str) -> None:
        """
        Copy a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(source):
                raise StorageError(f"Source file not found: {source}")
            
            # Ensure destination directory exists
            directory = os.path.dirname(destination)
            if directory:
                self.ensure_directory_exists(directory)
            
            shutil.copy2(source, destination)
            
        except Exception as e:
            raise StorageError(f"Failed to copy file from {source} to {destination}: {str(e)}")
    
    def move_file(self, source: str, destination: str) -> None:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(source):
                raise StorageError(f"Source file not found: {source}")
            
            # Ensure destination directory exists
            directory = os.path.dirname(destination)
            if directory:
                self.ensure_directory_exists(directory)
            
            shutil.move(source, destination)
            
        except Exception as e:
            raise StorageError(f"Failed to move file from {source} to {destination}: {str(e)}")
    
    def delete_file(self, filepath: str) -> None:
        """
        Delete a file.
        
        Args:
            filepath: Path to the file
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(filepath):
                return  # File doesn't exist, nothing to delete
            
            os.remove(filepath)
            
        except Exception as e:
            raise StorageError(f"Failed to delete file {filepath}: {str(e)}")
    
    def get_file_size(self, filepath: str) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            filepath: Path to the file
            
        Returns:
            File size in bytes
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(filepath):
                return 0
            
            return os.path.getsize(filepath)
            
        except Exception as e:
            raise StorageError(f"Failed to get file size for {filepath}: {str(e)}")
    
    def file_exists(self, filepath: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(filepath)
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory matching a pattern.
        
        Args:
            directory: Directory path
            pattern: File pattern (e.g., "*.pdf")
            
        Returns:
            List of file paths
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(directory):
                return []
            
            from glob import glob
            return glob(os.path.join(directory, pattern))
            
        except Exception as e:
            raise StorageError(f"Failed to list files in {directory}: {str(e)}")
    
    def create_temp_file(self, content: bytes, suffix: str = ".tmp") -> str:
        """
        Create a temporary file with the given content.
        
        Args:
            content: Content to write to temp file
            suffix: File suffix (e.g., ".pdf")
            
        Returns:
            Path to the temporary file
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                return tmp.name
                
        except Exception as e:
            raise StorageError(f"Failed to create temporary file: {str(e)}")
    
    def open_with_system(self, filepath: str) -> None:
        """
        Open a file with the system default application.
        
        Args:
            filepath: Path to the file
            
        Raises:
            StorageError: If file operation fails
        """
        try:
            if not os.path.exists(filepath):
                raise StorageError(f"File not found: {filepath}")
            
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            else:  # Unix-like
                try:
                    shutil.which('xdg-open') and os.system(f'xdg-open "{filepath}"')
                except Exception:
                    raise StorageError("Failed to open file with system application")
                    
        except Exception as e:
            raise StorageError(f"Failed to open file {filepath}: {str(e)}")
    
    def validate_filepath(self, filepath: str) -> bool:
        """
        Validate a file path for security.
        
        Args:
            filepath: File path to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for null bytes
            if '\x00' in filepath:
                return False
            
            # Check for path traversal attempts
            normalized = os.path.normpath(filepath)
            if '..' in normalized.split(os.sep):
                return False
            
            # Check absolute path (optional security measure)
            if os.path.isabs(filepath):
                # You might want to restrict to certain directories
                pass
            
            return True
            
        except Exception:
            return False
    
    def get_safe_filename(self, filename: str) -> str:
        """
        Get a safe filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not filename:
            return "unnamed"
        
        import re
        # Replace forbidden characters with underscore
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
        # Remove trailing spaces and dots
        sanitized = sanitized.rstrip(' .')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed"
        
        return sanitized
    
    def get_file_extension(self, filepath: str) -> str:
        """
        Get the file extension from a file path.
        
        Args:
            filepath: File path
            
        Returns:
            File extension (including the dot)
        """
        return os.path.splitext(filepath)[1].lower()
    
    def ensure_receipts_directory(self) -> str:
        """
        Ensure the receipts directory exists and return its path.
        
        Returns:
            Path to the receipts directory
        """
        self.ensure_directory_exists(self.receipts_path)
        return self.receipts_path
    
    def get_unique_filepath(self, directory: str, filename: str) -> str:
        """
        Get a unique file path in the specified directory.
        
        Args:
            directory: Target directory
            filename: Desired filename
            
        Returns:
            Unique file path
        """
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return filepath
        
        # If file exists, add a counter
        base, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{base} ({counter}){ext}"
            new_filepath = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_filepath):
                return new_filepath
            
            counter += 1
