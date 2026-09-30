"""
key_vault.py - Cryptographic Key Management & Password-Protected Vault
Provides:
  - Cryptographically secure random key generation (Hex, Base64, Alphanumeric, Passphrase)
  - AES-256-GCM + PBKDF2 password encryption for key export
  - Vault file parsing and password verification
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
import os
import secrets
import string
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PASSPHRASE_WORDS = [
    "cipher", "matrix", "falcon", "orbit", "phoenix", "shield", "quantum",
    "stellar", "nebula", "vortex", "cascade", "horizon", "beacon", "aurora",
    "solstice", "zenith", "apex", "echo", "pulsar", "titan", "vector",
    "prism", "entropy", "chaos", "dynamo", "eclipse", "strata", "flux",
    "vertex", "glacier", "bastion", "monolith", "radiant", "obsidian",
    "spectrum", "hyperion", "cortex", "synapse", "sentinel", "valiant"
]


def generate_key(key_type: str = "hex_256", length: int = 32) -> str:
    """Generate a high-entropy secret key according to the specified type.
    
    Types:
      - hex_256: 64-character hex string (256 bits entropy)
      - hex_128: 32-character hex string (128 bits entropy)
      - base64: URL-safe Base64 random token (32 bytes)
      - alphanumeric: Mixed letters, digits, and safe punctuation
      - passphrase: Memorable 5-word Diceware-style passphrase
    """
    if key_type == "hex_256":
        return secrets.token_hex(32)
    elif key_type == "hex_128":
        return secrets.token_hex(16)
    elif key_type == "base64":
        return secrets.token_urlsafe(32)
    elif key_type == "alphanumeric":
        chars = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
        return "".join(secrets.choice(chars) for _ in range(max(12, length)))
    elif key_type == "passphrase":
        word_count = max(3, min(length, 8)) if length <= 8 else 5
        words = [secrets.choice(PASSPHRASE_WORDS) for _ in range(word_count)]
        suffix_num = secrets.randbelow(900) + 100
        return f"{'-'.join(words)}-{suffix_num}"
    else:
        return secrets.token_hex(32)


def encrypt_key_with_password(
    secret_key: str, password: str, key_label: str = "Team Shared Secret Key"
) -> dict[str, Any]:
    """Encrypt a secret key using PBKDF2-HMAC-SHA256 and AES-256-GCM.
    Returns a dictionary suitable for JSON export (.keyvault file).
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    if not secret_key:
        raise ValueError("Secret key cannot be empty.")

    salt = os.urandom(16)
    nonce = os.urandom(12)
    iterations = 100_000

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    aes_key = kdf.derive(password.encode("utf-8"))
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, secret_key.encode("utf-8"), None)

    vault_payload = {
        "format": "SecureKeyVault",
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "key_label": key_label or "Secret Key",
        "kdf": {
            "algorithm": "PBKDF2-HMAC-SHA256",
            "iterations": iterations,
            "salt_hex": salt.hex(),
        },
        "cipher": {
            "algorithm": "AES-256-GCM",
            "nonce_hex": nonce.hex(),
            "ciphertext_hex": ciphertext.hex(),
        },
    }
    return vault_payload


def decrypt_key_from_vault(vault_data: dict[str, Any] | str, password: str) -> str:
    """Decrypt a secret key from a vault dictionary or JSON string.
    Raises ValueError if password is wrong or format is invalid.
    """
    if isinstance(vault_data, str):
        try:
            vault_data = json.loads(vault_data)
        except Exception as e:
            raise ValueError(f"Invalid vault JSON format: {e}") from e

    if not isinstance(vault_data, dict) or vault_data.get("format") != "SecureKeyVault":
        raise ValueError("Unrecognized vault file format. Must be a valid SecureKeyVault export.")

    kdf_info = vault_data.get("kdf", {})
    cipher_info = vault_data.get("cipher", {})

    try:
        salt = bytes.fromhex(kdf_info["salt_hex"])
        iterations = int(kdf_info.get("iterations", 100_000))
        nonce = bytes.fromhex(cipher_info["nonce_hex"])
        ciphertext = bytes.fromhex(cipher_info["ciphertext_hex"])
    except (KeyError, ValueError) as e:
        raise ValueError(f"Corrupted vault parameters: {e}") from e

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    aes_key = kdf.derive(password.encode("utf-8"))
    aesgcm = AESGCM(aes_key)

    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError("Incorrect password or corrupted vault file.") from e
