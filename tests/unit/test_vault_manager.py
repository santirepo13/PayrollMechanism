"""
Unit tests for vault manager.
"""
import pytest
import os
import tempfile
import zipfile
from io import BytesIO
from unittest.mock import patch, MagicMock

from broadspec.storage.vault_manager import VaultRepository
from broadspec.core.exceptions import VaultError, ConfigurationError


class TestVaultRepository:
    """Test cases for VaultRepository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'storage': {
                'vault_path': self.temp_dir
            }
        }
        
        # Mock cryptography if not available
        with patch('broadspec.storage.vault_manager.HAS_CRYPTO', True):
            with patch('broadspec.storage.vault_manager.Fernet') as mock_fernet:
                # Create a mock Fernet instance
                self.mock_fernet_instance = MagicMock()
                mock_fernet.return_value = self.mock_fernet_instance
                
                # Configure mock encryption/decryption
                self.mock_fernet_instance.encrypt.return_value = b'encrypted_data'
                self.mock_fernet_instance.decrypt.return_value = b'decrypted_data'
                
                self.vault = VaultRepository(self.config)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directories(self):
        """Test that initialization creates necessary directories."""
        assert os.path.exists(self.temp_dir)
        assert os.path.exists(os.path.join(self.temp_dir, "key.key"))
        assert os.path.exists(os.path.join(self.temp_dir, "single_vault.zip.enc"))
        assert os.path.exists(os.path.join(self.temp_dir, "vault_index.json.enc"))
    
    def test_init_without_crypto_raises_error(self):
        """Test that initialization fails without cryptography."""
        with patch('broadspec.storage.vault_manager.HAS_CRYPTO', False):
            with pytest.raises(ConfigurationError) as exc_info:
                VaultRepository(self.config)
            
            assert "cryptography package not available" in str(exc_info.value)
    
    def test_load_index_empty(self):
        """Test loading an empty index."""
        self.mock_fernet_instance.decrypt.return_value = b'[]'
        
        index = self.vault.load_index()
        
        assert index == []
        self.mock_fernet_instance.decrypt.assert_called_once()
    
    def test_load_index_with_data(self):
        """Test loading index with data."""
        test_data = b'[{"vault_filename": "test.pdf"}]'
        self.mock_fernet_instance.decrypt.return_value = test_data
        
        index = self.vault.load_index()
        
        assert len(index) == 1
        assert index[0]['vault_filename'] == 'test.pdf'
    
    def test_load_index_file_not_exists(self):
        """Test loading index when file doesn't exist."""
        # Remove index file
        os.remove(self.vault.vault_index_path)
        
        index = self.vault.load_index()
        
        assert index == []
    
    def test_save_index(self):
        """Test saving index."""
        self.vault.vault_index = [{"vault_filename": "test.pdf"}]
        
        self.vault._save_vault_index()
        
        self.mock_fernet_instance.encrypt.assert_called_once()
        # Check that the encrypted data was written to file
        call_args = self.mock_fernet_instance.encrypt.call_args[0][0]
        assert b'test.pdf' in call_args
    
    def test_rebuild_index_from_vault(self):
        """Test rebuilding index from vault."""
        # Create a mock zip file content
        mock_zip_content = BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as z:
            z.writestr("12345 - Test Model - 1000 - 2025-01-20.pdf", b"pdf content")
        
        self.mock_fernet_instance.decrypt.return_value = mock_zip_content.getvalue()
        
        self.vault.rebuild_index_from_vault()
        
        assert len(self.vault.vault_index) == 1
        entry = self.vault.vault_index[0]
        assert entry['model_id'] == '12345'
        assert entry['model_name'] == 'Test Model'
        assert entry['tokens'] == '1000'
        assert entry['date'] == '2025-01-20'
    
    def test_add_file(self):
        """Test adding a file to vault."""
        # Create a temporary file
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"test pdf content")
        
        # Mock empty vault
        self.mock_fernet_instance.decrypt.return_value = b''
        
        metadata = {
            'model_id': '12345',
            'model_name': 'Test Model',
            'tokens': '1000',
            'date': '2025-01-20'
        }
        
        entry = self.vault.add_file(test_file, metadata)
        
        assert entry.model_id == '12345'
        assert entry.model_name == 'Test Model'
        assert entry.tokens == '1000'
        assert entry.date == '2025-01-20'
        assert entry.orig_filename == 'test.pdf'
        assert entry.vault_filename == 'test.pdf'
        assert entry.saved_at is not None
        
        # Check that file was added to index
        assert len(self.vault.vault_index) == 1
        assert self.vault.vault_index[0]['vault_filename'] == 'test.pdf'
    
    def test_add_file_with_conflict(self):
        """Test adding a file with name conflict."""
        # Create a temporary file
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"test pdf content")
        
        # Mock vault with existing file
        mock_zip_content = BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as z:
            z.writestr("test.pdf", b"existing content")
        
        self.mock_fernet_instance.decrypt.return_value = mock_zip_content.getvalue()
        
        metadata = {
            'model_id': '12345',
            'model_name': 'Test Model',
            'tokens': '1000',
            'date': '2025-01-20'
        }
        
        entry = self.vault.add_file(test_file, metadata)
        
        # Should have created a unique name
        assert entry.vault_filename == 'test (1).pdf'
        assert entry.orig_filename == 'test.pdf'
    
    def test_retrieve_file(self):
        """Test retrieving a file from vault."""
        # Create a mock zip with test file
        mock_zip_content = BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as z:
            z.writestr("test.pdf", b"test pdf content")
        
        self.mock_fernet_instance.decrypt.return_value = mock_zip_content.getvalue()
        
        file_bytes = self.vault.retrieve_file("test.pdf")
        
        assert file_bytes == b"test pdf content"
    
    def test_retrieve_file_not_found(self):
        """Test retrieving a file that doesn't exist."""
        # Create empty mock zip
        mock_zip_content = BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as z:
            pass
        
        self.mock_fernet_instance.decrypt.return_value = mock_zip_content.getvalue()
        
        with pytest.raises(VaultError) as exc_info:
            self.vault.retrieve_file("nonexistent.pdf")
        
        assert "File not found in vault" in str(exc_info.value)
    
    def test_delete_files(self):
        """Test deleting files from vault."""
        # Create a mock zip with test files
        mock_zip_content = BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as z:
            z.writestr("test1.pdf", b"content1")
            z.writestr("test2.pdf", b"content2")
            z.writestr("test3.pdf", b"content3")
        
        self.mock_fernet_instance.decrypt.return_value = mock_zip_content.getvalue()
        
        # Add entries to index
        self.vault.vault_index = [
            {'vault_filename': 'test1.pdf'},
            {'vault_filename': 'test2.pdf'},
            {'vault_filename': 'test3.pdf'}
        ]
        
        deleted_count = self.vault.delete_files(['test2.pdf'])
        
        assert deleted_count == 1
        assert len(self.vault.vault_index) == 2
        assert all(entry['vault_filename'] != 'test2.pdf' for entry in self.vault.vault_index)
    
    def test_delete_files_multiple(self):
        """Test deleting multiple files from vault."""
        # Create a mock zip with test files
        mock_zip_content = BytesIO()
        with zipfile.ZipFile(mock_zip_content, 'w') as z:
            z.writestr("test1.pdf", b"content1")
            z.writestr("test2.pdf", b"content2")
            z.writestr("test3.pdf", b"content3")
        
        self.mock_fernet_instance.decrypt.return_value = mock_zip_content.getvalue()
        
        # Add entries to index
        self.vault.vault_index = [
            {'vault_filename': 'test1.pdf'},
            {'vault_filename': 'test2.pdf'},
            {'vault_filename': 'test3.pdf'}
        ]
        
        deleted_count = self.vault.delete_files(['test1.pdf', 'test3.pdf'])
        
        assert deleted_count == 2
        assert len(self.vault.vault_index) == 1
        assert self.vault.vault_index[0]['vault_filename'] == 'test2.pdf'
    
    def test_get_all_entries(self):
        """Test getting all vault entries."""
        self.vault.vault_index = [
            {'vault_filename': 'test1.pdf'},
            {'vault_filename': 'test2.pdf'}
        ]
        
        entries = self.vault.get_all_entries()
        
        assert len(entries) == 2
        assert entries[0]['vault_filename'] == 'test1.pdf'
        assert entries[1]['vault_filename'] == 'test2.pdf'
        
        # Check that it returns a copy
        entries.append({'vault_filename': 'test3.pdf'})
        assert len(self.vault.vault_index) == 2
    
    def test_get_vault_size(self):
        """Test getting vault size."""
        # Mock file size
        with patch('os.path.getsize', return_value=1024):
            size = self.vault.get_vault_size()
            assert size == 1024
        
        # Test when file doesn't exist
        with patch('os.path.exists', return_value=False):
            size = self.vault.get_vault_size()
            assert size == 0
    
    def test_parse_filename_metadata(self):
        """Test parsing metadata from filename."""
        filename = "12345 - Test Model - 1000 - 2025-01-20.pdf"
        metadata = self.vault._parse_filename_metadata(filename)
        
        assert metadata['model_id'] == '12345'
        assert metadata['model_name'] == 'Test Model'
        assert metadata['tokens'] == '1000'
        assert metadata['date'] == '2025-01-20'
    
    def test_parse_filename_metadata_with_tks(self):
        """Test parsing metadata from filename with TKS."""
        filename = "12345 - Test Model - 1000 TKS - 2025-01-20.pdf"
        metadata = self.vault._parse_filename_metadata(filename)
        
        assert metadata['model_id'] == '12345'
        assert metadata['model_name'] == 'Test Model'
        assert metadata['tokens'] == '1000 TKS'
        assert metadata['date'] == '2025-01-20'
    
    def test_parse_filename_metadata_empty(self):
        """Test parsing metadata from empty filename."""
        metadata = self.vault._parse_filename_metadata("")
        
        assert metadata['model_id'] == ''
        assert metadata['model_name'] == ''
        assert metadata['tokens'] == ''
        assert metadata['date'] == ''
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test with invalid characters
        invalid_name = "Test<>:\"/\\|?*Model"
        sanitized = self.vault._sanitize_filename(invalid_name)
        assert sanitized == "Test_________Model"
        
        # Test with trailing spaces and dots
        trailing_name = "Test Model   ... "
        sanitized = self.vault._sanitize_filename(trailing_name)
        assert sanitized == "Test Model"
        
        # Test with empty name
        sanitized = self.vault._sanitize_filename("")
        assert sanitized == "unnamed"
    
    def test_decrypt_vault_invalid_token(self):
        """Test vault decryption with invalid token."""
        from cryptography.fernet import InvalidToken
        
        self.mock_fernet_instance.decrypt.side_effect = InvalidToken()
        
        with pytest.raises(VaultError) as exc_info:
            self.vault._decrypt_vault()
        
        assert "Cannot decrypt vault (invalid key)" in str(exc_info.value)