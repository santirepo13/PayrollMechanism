"""
Unit tests for file operations.
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open

from broadspec.storage.file_operations import FileOperations
from broadspec.core.exceptions import StorageError


class TestFileOperations:
    """Test cases for FileOperations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'storage': {
                'receipts_path': os.path.join(self.temp_dir, 'receipts')
            }
        }
        self.file_ops = FileOperations(self.config)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_config(self):
        """Test initialization with configuration."""
        assert self.file_ops.receipts_path == self.config['storage']['receipts_path']
    
    def test_init_without_config(self):
        """Test initialization without configuration."""
        file_ops = FileOperations()
        assert file_ops.receipts_path == 'Receipts'
    
    def test_ensure_directory_exists_new(self):
        """Test creating a new directory."""
        new_dir = os.path.join(self.temp_dir, 'new_directory')
        
        self.file_ops.ensure_directory_exists(new_dir)
        
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_ensure_directory_exists_existing(self):
        """Test ensuring an existing directory exists."""
        # Should not raise an error
        self.file_ops.ensure_directory_exists(self.temp_dir)
        
        assert os.path.exists(self.temp_dir)
    
    def test_save_file(self):
        """Test saving a file."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = b"test content"
        
        self.file_ops.save_file(test_file, test_content)
        
        assert os.path.exists(test_file)
        with open(test_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_save_file_creates_directory(self):
        """Test saving a file creates directory if needed."""
        test_file = os.path.join(self.temp_dir, 'new_dir', 'test.txt')
        test_content = b"test content"
        
        self.file_ops.save_file(test_file, test_content)
        
        assert os.path.exists(test_file)
        with open(test_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_save_file_error(self):
        """Test save file error handling."""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(StorageError) as exc_info:
                self.file_ops.save_file('test.txt', b'content')
            
            assert "Failed to save file" in str(exc_info.value)
    
    def test_load_file(self):
        """Test loading a file."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = b"test content"
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        loaded_content = self.file_ops.load_file(test_file)
        
        assert loaded_content == test_content
    
    def test_load_file_not_exists(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(StorageError) as exc_info:
            self.file_ops.load_file('nonexistent.txt')
        
        assert "File not found" in str(exc_info.value)
    
    def test_load_file_error(self):
        """Test load file error handling."""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(StorageError) as exc_info:
                self.file_ops.load_file('test.txt')
            
            assert "Failed to load file" in str(exc_info.value)
    
    def test_copy_file(self):
        """Test copying a file."""
        source_file = os.path.join(self.temp_dir, 'source.txt')
        dest_file = os.path.join(self.temp_dir, 'dest.txt')
        test_content = b"test content"
        
        with open(source_file, 'wb') as f:
            f.write(test_content)
        
        self.file_ops.copy_file(source_file, dest_file)
        
        assert os.path.exists(dest_file)
        with open(dest_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_copy_file_creates_directory(self):
        """Test copying a file creates destination directory."""
        source_file = os.path.join(self.temp_dir, 'source.txt')
        dest_file = os.path.join(self.temp_dir, 'new_dir', 'dest.txt')
        test_content = b"test content"
        
        with open(source_file, 'wb') as f:
            f.write(test_content)
        
        self.file_ops.copy_file(source_file, dest_file)
        
        assert os.path.exists(dest_file)
        with open(dest_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_copy_file_source_not_exists(self):
        """Test copying a file that doesn't exist."""
        with pytest.raises(StorageError) as exc_info:
            self.file_ops.copy_file('nonexistent.txt', 'dest.txt')
        
        assert "Source file not found" in str(exc_info.value)
    
    def test_move_file(self):
        """Test moving a file."""
        source_file = os.path.join(self.temp_dir, 'source.txt')
        dest_file = os.path.join(self.temp_dir, 'dest.txt')
        test_content = b"test content"
        
        with open(source_file, 'wb') as f:
            f.write(test_content)
        
        self.file_ops.move_file(source_file, dest_file)
        
        assert not os.path.exists(source_file)
        assert os.path.exists(dest_file)
        with open(dest_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_move_file_creates_directory(self):
        """Test moving a file creates destination directory."""
        source_file = os.path.join(self.temp_dir, 'source.txt')
        dest_file = os.path.join(self.temp_dir, 'new_dir', 'dest.txt')
        test_content = b"test content"
        
        with open(source_file, 'wb') as f:
            f.write(test_content)
        
        self.file_ops.move_file(source_file, dest_file)
        
        assert not os.path.exists(source_file)
        assert os.path.exists(dest_file)
        with open(dest_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_delete_file(self):
        """Test deleting a file."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        
        with open(test_file, 'wb') as f:
            f.write(b"test content")
        
        assert os.path.exists(test_file)
        
        self.file_ops.delete_file(test_file)
        
        assert not os.path.exists(test_file)
    
    def test_delete_file_not_exists(self):
        """Test deleting a file that doesn't exist (should not raise error)."""
        # Should not raise an error
        self.file_ops.delete_file('nonexistent.txt')
    
    def test_get_file_size(self):
        """Test getting file size."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = b"test content"
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        size = self.file_ops.get_file_size(test_file)
        
        assert size == len(test_content)
    
    def test_get_file_size_not_exists(self):
        """Test getting size of file that doesn't exist."""
        size = self.file_ops.get_file_size('nonexistent.txt')
        assert size == 0
    
    def test_file_exists(self):
        """Test checking if file exists."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        
        assert not self.file_ops.file_exists(test_file)
        
        with open(test_file, 'wb') as f:
            f.write(b"test content")
        
        assert self.file_ops.file_exists(test_file)
    
    def test_list_files(self):
        """Test listing files in directory."""
        # Create test files
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f'test{i}.txt')
            with open(test_file, 'wb') as f:
                f.write(f'content {i}'.encode())
        
        files = self.file_ops.list_files(self.temp_dir, '*.txt')
        
        assert len(files) == 3
        for i in range(3):
            assert any(f'test{i}.txt' in file for file in files)
    
    def test_list_files_directory_not_exists(self):
        """Test listing files in directory that doesn't exist."""
        files = self.file_ops.list_files('nonexistent_dir')
        assert files == []
    
    def test_list_files_error(self):
        """Test list files error handling."""
        with patch('glob.glob', side_effect=IOError("Permission denied")):
            with pytest.raises(StorageError) as exc_info:
                self.file_ops.list_files(self.temp_dir)
            
            assert "Failed to list files" in str(exc_info.value)
    
    def test_create_temp_file(self):
        """Test creating a temporary file."""
        test_content = b"test content"
        
        temp_path = self.file_ops.create_temp_file(test_content, '.txt')
        
        try:
            assert os.path.exists(temp_path)
            assert temp_path.endswith('.txt')
            with open(temp_path, 'rb') as f:
                assert f.read() == test_content
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_create_temp_file_error(self):
        """Test create temp file error handling."""
        with patch('tempfile.NamedTemporaryFile', side_effect=IOError("Permission denied")):
            with pytest.raises(StorageError) as exc_info:
                self.file_ops.create_temp_file(b'content')
            
            assert "Failed to create temporary file" in str(exc_info.value)
    
    @patch('os.startfile')
    @patch('os.name', 'nt')
    def test_open_with_system_windows(self, mock_startfile):
        """Test opening file with system on Windows."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'wb') as f:
            f.write(b"test content")
        
        self.file_ops.open_with_system(test_file)
        
        mock_startfile.assert_called_once_with(test_file)
    
    @patch('shutil.which')
    @patch('os.system')
    @patch('os.name', 'posix')
    def test_open_with_system_unix(self, mock_system, mock_which):
        """Test opening file with system on Unix."""
        mock_which.return_value = '/usr/bin/xdg-open'
        
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'wb') as f:
            f.write(b"test content")
        
        self.file_ops.open_with_system(test_file)
        
        mock_system.assert_called_once_with('xdg-open "test.txt"')
    
    def test_open_with_system_file_not_exists(self):
        """Test opening file that doesn't exist."""
        with pytest.raises(StorageError) as exc_info:
            self.file_ops.open_with_system('nonexistent.txt')
        
        assert "File not found" in str(exc_info.value)
    
    def test_validate_filepath_valid(self):
        """Test validating a valid file path."""
        valid_path = os.path.join(self.temp_dir, 'test.txt')
        assert self.file_ops.validate_filepath(valid_path) == True
    
    def test_validate_filepath_with_null_bytes(self):
        """Test validating file path with null bytes."""
        invalid_path = "test\x00.txt"
        assert self.file_ops.validate_filepath(invalid_path) == False
    
    def test_validate_filepath_with_traversal(self):
        """Test validating file path with path traversal."""
        invalid_path = "../../../etc/passwd"
        assert self.file_ops.validate_filepath(invalid_path) == False
    
    def test_get_safe_filename(self):
        """Test getting safe filename."""
        unsafe_name = "Test<>:\"/\\|?*Model"
        safe_name = self.file_ops.get_safe_filename(unsafe_name)
        assert safe_name == "Test_________Model"
    
    def test_get_safe_filename_empty(self):
        """Test getting safe filename from empty string."""
        safe_name = self.file_ops.get_safe_filename("")
        assert safe_name == "unnamed"
    
    def test_get_file_extension(self):
        """Test getting file extension."""
        filepath = "test.txt"
        ext = self.file_ops.get_file_extension(filepath)
        assert ext == ".txt"
        
        filepath = "test.TXT"
        ext = self.file_ops.get_file_extension(filepath)
        assert ext == ".txt"
        
        filepath = "test"
        ext = self.file_ops.get_file_extension(filepath)
        assert ext == ""
    
    def test_ensure_receipts_directory(self):
        """Test ensuring receipts directory exists."""
        receipts_path = self.file_ops.ensure_receipts_directory()
        
        assert receipts_path == self.file_ops.receipts_path
        assert os.path.exists(receipts_path)
        assert os.path.isdir(receipts_path)
    
    def test_get_unique_filepath_new(self):
        """Test getting unique filepath for new file."""
        directory = self.temp_dir
        filename = "test.txt"
        
        unique_path = self.file_ops.get_unique_filepath(directory, filename)
        
        assert unique_path == os.path.join(directory, filename)
    
    def test_get_unique_filepath_existing(self):
        """Test getting unique filepath when file exists."""
        directory = self.temp_dir
        filename = "test.txt"
        existing_file = os.path.join(directory, filename)
        
        # Create existing file
        with open(existing_file, 'wb') as f:
            f.write(b"content")
        
        unique_path = self.file_ops.get_unique_filepath(directory, filename)
        
        assert unique_path != existing_file
        assert unique_path == os.path.join(directory, "test (1).txt")
    
    def test_get_unique_filepath_multiple_conflicts(self):
        """Test getting unique filepath with multiple conflicts."""
        directory = self.temp_dir
        filename = "test.txt"
        
        # Create multiple existing files
        for i in range(3):
            existing_file = os.path.join(directory, f"test ({i}).txt" if i > 0 else "test.txt")
            with open(existing_file, 'wb') as f:
                f.write(b"content")
        
        unique_path = self.file_ops.get_unique_filepath(directory, filename)
        
        assert unique_path == os.path.join(directory, "test (3).txt")