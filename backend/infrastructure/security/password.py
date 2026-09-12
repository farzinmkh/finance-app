"""
Password Hashing
=================
Uses Python's built-in hashlib.pbkdf2_hmac with SHA-256.

PBKDF2 with 100,000 iterations and a 32-byte random salt is a legitimate
production password hashing approach. It is available in Python's stdlib,
so no third-party package is required in this phase.

When passlib[bcrypt] is installed, replace this module with bcrypt.
The interface (hash_password, verify_password) remains identical.

Why not just use hashlib.sha256(password)?
  A simple SHA-256 hash is a fingerprint, not a password hash:
  - No salt → identical passwords produce identical hashes
  - No cost factor → a GPU can crack millions of passwords per second
  PBKDF2 addresses both problems: unique random salt + computational cost.
"""

import binascii
import hashlib
import hmac
import os


def hash_password(plaintext: str) -> str:
    """
    Hash a plaintext password using PBKDF2-SHA256.

    Returns a string in the format: "{salt_hex}:{dk_hex}"
    Both the salt and the derived key are stored together so that
    verify_password() has everything it needs without a separate lookup.
    """
    salt: bytes = os.urandom(32)
    dk: bytes = hashlib.pbkdf2_hmac(
        "sha256",
        plaintext.encode("utf-8"),
        salt,
        iterations=100_000,
    )
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


def verify_password(plaintext: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2 hash.

    Returns True if the password matches, False otherwise.
    Never raises an exception (returns False on malformed stored_hash).
    """
    try:
        salt_hex, dk_hex = stored_hash.split(":", 1)
        salt = binascii.unhexlify(salt_hex)
        expected_dk = binascii.unhexlify(dk_hex)
        actual_dk = hashlib.pbkdf2_hmac(
            "sha256",
            plaintext.encode("utf-8"),
            salt,
            iterations=100_000,
        )
        # Compare in constant time to prevent timing attacks.
        # hmac.compare_digest (not hashlib) is the correct stdlib function.
        return hmac.compare_digest(actual_dk, expected_dk)
    except (ValueError, binascii.Error):
        return False
