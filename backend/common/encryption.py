"""
Token encryption/decryption using Fernet symmetric encryption.
Generates a key automatically if not set in env vars.
"""
import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet:
        return _fernet

    key = os.environ.get("TOKEN_ENCRYPTION_KEY")
    if not key:
        key = Fernet.generate_key().decode()
        os.environ["TOKEN_ENCRYPTION_KEY"] = key
        logger.warning("Generated new TOKEN_ENCRYPTION_KEY. Set it in .env for persistence.")

    _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token string. Returns base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a token string. Returns plaintext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
