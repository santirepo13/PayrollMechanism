"""
Encrypted vault management for BroadSpec Payment Calculator.
"""
import os
import json
import zipfile
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore

try:
    from cryptography.fernet import Fernet as _Fernet, InvalidToken as _InvalidToken
    HAS_CRYPTO = True
except ImportError:
    _Fernet = None
    _InvalidToken = Exception
    HAS_CRYPTO = False

from core.models import VaultEntry
from core.exceptions import VaultError, ConfigurationError


class VaultRepository:
    """Repository pattern for vault operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize vault repository with configuration."""
        self.config = config or {}
        
        if not HAS_CRYPTO:
            raise ConfigurationError("cryptography package not available")
        
        # Set up paths
        self.secure_store_dir = self.config.get('storage', {}).get('vault_path', '.secure_store')
        self.secure_key_path = os.path.join(self.secure_store_dir, "key.key")
        self.single_vault_path = os.path.join(self.secure_store_dir, "single_vault.zip.enc")
        self.vault_index_path = os.path.join(self.secure_store_dir, "vault_index.json.enc")
        
        # Initialize vault
        self.vault_index: List[Dict[str, Any]] = []
        self.fernet: Optional['Fernet'] = None
        self._ensure_vault_setup()
    
    def _ensure_vault_setup(self) -> None:
        """Ensure vault directory and encryption key are set up."""
        try:
            os.makedirs(self.secure_store_dir, exist_ok=True)
            
            # Generate or load encryption key
            if not os.path.exists(self.secure_key_path):
                key = _Fernet.generate_key()
                with open(self.secure_key_path, "wb") as f:
                    f.write(key)
            else:
                with open(self.secure_key_path, "rb") as f:
                    key = f.read()
            
            self.fernet = _Fernet(key)
            
            # Ensure vault file exists
            if not os.path.exists(self.single_vault_path):
                empty_zip = BytesIO()
                with zipfile.ZipFile(empty_zip, 'w') as z:
                    pass
                enc = self.fernet.encrypt(empty_zip.getvalue())
                with open(self.single_vault_path, 'wb') as f:
                    f.write(enc)
            
            # Ensure index file exists
            if not os.path.exists(self.vault_index_path):
                self.vault_index = []
                self._save_vault_index()
                
        except Exception as e:
            raise VaultError(f"Failed to initialize vault: {str(e)}")
    
    def load_index(self) -> List[Dict[str, Any]]:
        """Load and decrypt the vault index."""
        try:
            if not os.path.exists(self.vault_index_path):
                self.vault_index = []
                return self.vault_index
            
            with open(self.vault_index_path, "rb") as f:
                enc = f.read()
            
            if not enc:
                self.vault_index = []
                return self.vault_index
            
            data = self.fernet.decrypt(enc)
            self.vault_index = json.loads(data.decode("utf-8"))
            return self.vault_index
            
        except _InvalidToken:
            raise VaultError("Vault index exists but cannot be decrypted (invalid key)")
        except Exception as e:
            raise VaultError(f"Failed to load vault index: {str(e)}")
    
    def _save_vault_index(self) -> None:
        """Encrypt and save the vault index."""
        try:
            data = json.dumps(self.vault_index, ensure_ascii=False).encode("utf-8")
            enc = self.fernet.encrypt(data)
            with open(self.vault_index_path, "wb") as f:
                f.write(enc)
        except Exception as e:
            raise VaultError(f"Failed to save vault index: {str(e)}")
    
    def rebuild_index_from_vault(self) -> None:
        """Rebuild vault index by reading filenames from the vault."""
        try:
            if not os.path.exists(self.single_vault_path):
                self.vault_index = []
                self._save_vault_index()
                return
            
            with open(self.single_vault_path, "rb") as f:
                enc = f.read()
            
            if not enc:
                self.vault_index = []
                self._save_vault_index()
                return
            
            data = self.fernet.decrypt(enc)
            zbuf = BytesIO(data)
            
            with zipfile.ZipFile(zbuf, 'r') as z:
                names = z.namelist()
                new_index = []
                
                for name in names:
                    parsed = self._parse_filename_metadata(name)
                    metadata = {
                        "vault_filename": name,
                        "orig_filename": name,
                        "model_id": parsed.get("model_id", ""),
                        "model_name": parsed.get("model_name", ""),
                        "tokens": parsed.get("tokens", ""),
                        "date": parsed.get("date", ""),
                        "saved_at": None
                    }
                    new_index.append(metadata)
                
                self.vault_index = new_index
                self._save_vault_index()
                
        except Exception as e:
            raise VaultError(f"Failed to rebuild index from vault: {str(e)}")
    
    def add_file(self, source_filepath: str, metadata: Dict[str, Any]) -> VaultEntry:
        """Add a file to the vault."""
        try:
            # Read source file
            with open(source_filepath, 'rb') as f:
                file_bytes = f.read()
            
            # Decrypt existing vault
            existing_zip_bytes = self._decrypt_vault()
            
            # Create new zip with existing content plus new file
            new_zip_buf = BytesIO()
            with zipfile.ZipFile(new_zip_buf, 'w') as new_zip:
                # Copy existing entries
                if existing_zip_bytes:
                    old_buf = BytesIO(existing_zip_bytes)
                    try:
                        with zipfile.ZipFile(old_buf, 'r') as old_zip:
                            for name in old_zip.namelist():
                                new_zip.writestr(name, old_zip.read(name))
                    except Exception:
                        # If old zip is invalid, start fresh
                        pass
                
                # Add new file with unique name
                orig_name = os.path.basename(source_filepath)
                safe_name = self._sanitize_filename(orig_name)
                candidate = safe_name
                counter = 1
                
                # Get existing names to avoid conflicts
                existing_names = set()
                if existing_zip_bytes:
                    old_buf = BytesIO(existing_zip_bytes)
                    try:
                        with zipfile.ZipFile(old_buf, 'r') as old_zip:
                            existing_names = set(old_zip.namelist())
                    except Exception:
                        pass
                
                while candidate in existing_names:
                    base, ext = os.path.splitext(safe_name)
                    candidate = f"{base} ({counter}){ext}"
                    counter += 1
                
                new_zip.writestr(candidate, file_bytes)
            
            # Encrypt and save new vault
            new_zip_bytes = new_zip_buf.getvalue()
            enc = self.fernet.encrypt(new_zip_bytes)
            with open(self.single_vault_path, 'wb') as f:
                f.write(enc)
            
            # Create vault entry
            entry = VaultEntry(
                vault_filename=candidate,
                orig_filename=orig_name,
                model_id=metadata.get("model_id", ""),
                model_name=metadata.get("model_name", ""),
                tokens=metadata.get("tokens", ""),
                date=metadata.get("date", ""),
                saved_at=datetime.now().isoformat()
            )
            
            # Add to index
            self.vault_index.append({
                "vault_filename": entry.vault_filename,
                "orig_filename": entry.orig_filename,
                "model_id": entry.model_id,
                "model_name": entry.model_name,
                "tokens": entry.tokens,
                "date": entry.date,
                "saved_at": entry.saved_at
            })
            
            self._save_vault_index()
            return entry
            
        except Exception as e:
            raise VaultError(f"Failed to add file to vault: {str(e)}")
    
    def retrieve_file(self, vault_filename: str) -> bytes:
        """Retrieve a file from the vault."""
        try:
            vault_bytes = self._decrypt_vault()
            zbuf = BytesIO(vault_bytes)
            
            with zipfile.ZipFile(zbuf, 'r') as z:
                if vault_filename not in z.namelist():
                    raise VaultError(f"File not found in vault: {vault_filename}")
                return z.read(vault_filename)
                
        except Exception as e:
            raise VaultError(f"Failed to retrieve file from vault: {str(e)}")
    
    def delete_files(self, vault_filenames: List[str]) -> int:
        """Delete files from the vault."""
        try:
            if not vault_filenames:
                return 0
            
            # Decrypt existing vault
            vault_bytes = self._decrypt_vault()
            old_buf = BytesIO(vault_bytes)
            new_buf = BytesIO()
            
            # Create new vault without specified files
            with zipfile.ZipFile(old_buf, 'r') as old_zip:
                with zipfile.ZipFile(new_buf, 'w') as new_zip:
                    for name in old_zip.namelist():
                        if name not in vault_filenames:
                            new_zip.writestr(name, old_zip.read(name))
            
            # Encrypt and save new vault
            new_zip_bytes = new_buf.getvalue()
            enc = self.fernet.encrypt(new_zip_bytes)
            with open(self.single_vault_path, 'wb') as f:
                f.write(enc)
            
            # Remove entries from index
            original_count = len(self.vault_index)
            self.vault_index = [
                entry for entry in self.vault_index 
                if entry.get('vault_filename') not in vault_filenames
            ]
            deleted_count = original_count - len(self.vault_index)
            
            self._save_vault_index()
            return deleted_count
            
        except Exception as e:
            raise VaultError(f"Failed to delete files from vault: {str(e)}")
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all vault entries."""
        return self.vault_index.copy()
    
    def get_vault_size(self) -> int:
        """Get the size of the encrypted vault file."""
        try:
            if os.path.exists(self.single_vault_path):
                return os.path.getsize(self.single_vault_path)
            return 0
        except Exception:
            return 0
    
    def _decrypt_vault(self) -> bytes:
        """Decrypt the vault file."""
        try:
            with open(self.single_vault_path, 'rb') as f:
                enc = f.read()
            
            if not enc:
                return b""
            
            return self.fernet.decrypt(enc)
            
        except _InvalidToken:
            raise VaultError("Cannot decrypt vault (invalid key)")
        except Exception as e:
            raise VaultError(f"Failed to decrypt vault: {str(e)}")
    
    def _parse_filename_metadata(self, filename: str) -> Dict[str, str]:
        """Extract metadata from filename."""
        try:
            if not filename:
                return {"model_id": "", "model_name": "", "tokens": "", "date": ""}
            
            base = os.path.basename(filename)
            base = base.rsplit(".pdf", 1)[0]
            
            # Extract date
            import re
            date = ""
            m = re.search(r'(\d{4}-\d{2}-\d{2})$', base)
            if m:
                date = m.group(1)
                base_wo_date = base[:m.start()].rstrip(' -')
            else:
                base_wo_date = base
            
            # Split parts
            parts = [p.strip() for p in base_wo_date.split(" - ") if p.strip() != ""]
            model_id = parts[0] if len(parts) >= 1 else ""
            tokens = ""
            model_name = ""
            
            # Find token-like segment
            token_index = None
            for i in range(len(parts) - 1, 0, -1):
                if re.search(r'\b\d[\d,\.]*\s*(TKS)?\b', parts[i], re.IGNORECASE):
                    token_index = i
                    break
            
            if token_index is not None:
                tokens = parts[token_index]
                if token_index > 1:
                    model_name = " - ".join(parts[1:token_index])
                else:
                    model_name = parts[1] if len(parts) > 1 else ""
            else:
                if len(parts) >= 3:
                    tokens = parts[-1]
                    model_name = " - ".join(parts[1:-1])
                else:
                    tokens = ""
                    model_name = " - ".join(parts[1:]) if len(parts) > 1 else ""
            
            return {"model_id": model_id, "model_name": model_name, "tokens": tokens, "date": date}
            
        except Exception:
            return {"model_id": "", "model_name": "", "tokens": "", "date": ""}
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename by removing forbidden characters."""
        if not name:
            return "unnamed"
        
        import re
        # Replace forbidden characters with underscore
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
        # Remove trailing spaces and dots
        sanitized = sanitized.rstrip(' .')
        return sanitized