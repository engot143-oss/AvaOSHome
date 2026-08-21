"""
Data encryption for AVA OS - encrypt sensitive data at rest.

Encrypts:
- Conversation history (optional)
- Personal profile data (optional)
- API keys
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
from datetime import datetime


class DataEncryption:
    """Handle encryption/decryption of sensitive data."""

    def __init__(self, key_path: Path | None = None):
        """Initialize encryption with key file."""
        if key_path is None:
            key_path = Path.home() / '.ava_os' / '.encryption_key'

        self.key_path = key_path
        self.cipher_suite = self._load_or_create_key()

    def _load_or_create_key(self) -> Fernet:
        """Load existing key or create new one."""
        if self.key_path.exists():
            key = self.key_path.read_bytes()
        else:
            # Generate new key
            key = Fernet.generate_key()
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            self.key_path.write_bytes(key)
            # Restrict permissions (Unix only)
            try:
                os.chmod(self.key_path, 0o600)
            except (AttributeError, OSError):
                pass  # Windows doesn't support chmod

        return Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        if isinstance(data, str):
            data = data.encode()
        encrypted = self.cipher_suite.encrypt(data)
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode()

    def encrypt_file(self, file_path: Path) -> Path:
        """Encrypt a file in place."""
        content = file_path.read_text()
        encrypted = self.encrypt(content)
        encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
        encrypted_path.write_text(encrypted)

        # Securely delete original
        try:
            os.remove(file_path)
        except OSError:
            pass

        return encrypted_path

    def decrypt_file(self, encrypted_path: Path) -> Path:
        """Decrypt a file."""
        encrypted_content = encrypted_path.read_text()
        decrypted = self.decrypt(encrypted_content)
        original_path = encrypted_path.with_suffix('')

        original_path.write_text(decrypted)
        return original_path

    def encrypt_json(self, data: dict) -> str:
        """Encrypt a JSON object."""
        json_str = json.dumps(data)
        return self.encrypt(json_str)

    def decrypt_json(self, encrypted_json: str) -> dict:
        """Decrypt a JSON object."""
        decrypted = self.decrypt(encrypted_json)
        return json.loads(decrypted)


class EncryptedStorage:
    """Store and retrieve encrypted data."""

    def __init__(self, storage_dir: Path, encryption: DataEncryption | None = None):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.encryption = encryption or DataEncryption()

    def save_encrypted(self, key: str, data: dict) -> None:
        """Save encrypted data."""
        encrypted = self.encryption.encrypt_json(data)
        encrypted_path = self.storage_dir / f'{key}.enc'
        encrypted_path.write_text(encrypted)

    def load_encrypted(self, key: str) -> dict:
        """Load encrypted data."""
        encrypted_path = self.storage_dir / f'{key}.enc'
        if not encrypted_path.exists():
            return {}

        encrypted = encrypted_path.read_text()
        return self.encryption.decrypt_json(encrypted)

    def delete_encrypted(self, key: str) -> None:
        """Delete encrypted data."""
        encrypted_path = self.storage_dir / f'{key}.enc'
        if encrypted_path.exists():
            encrypted_path.unlink()


def encrypt_conversation_history(memory_dir: Path, encryption: DataEncryption | None = None) -> None:
    """Encrypt conversation history file."""
    if encryption is None:
        encryption = DataEncryption()

    history_file = memory_dir / 'conversation_history.jsonl'
    if history_file.exists():
        content = history_file.read_text()
        encrypted = encryption.encrypt(content)
        encrypted_file = history_file.with_suffix('.jsonl.enc')
        encrypted_file.write_text(encrypted)

        # Log encryption
        log_file = memory_dir / 'encryption.log'
        with open(log_file, 'a') as f:
            f.write(f'{datetime.now().isoformat()} - Encrypted conversation_history.jsonl\n')

        # Keep original for now (remove after verification)
        # os.remove(history_file)


def decrypt_conversation_history(memory_dir: Path, encryption: DataEncryption | None = None) -> str:
    """Decrypt conversation history file."""
    if encryption is None:
        encryption = DataEncryption()

    encrypted_file = memory_dir / 'conversation_history.jsonl.enc'
    if encrypted_file.exists():
        encrypted = encrypted_file.read_text()
        return encryption.decrypt(encrypted)

    # Fallback to unencrypted file
    history_file = memory_dir / 'conversation_history.jsonl'
    if history_file.exists():
        return history_file.read_text()

    return ''
