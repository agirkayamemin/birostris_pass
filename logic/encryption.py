from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os

# --- Password Hashing (for master password) ---
def hash_password(password: str, salt: bytes = None) -> (str, str):
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.b64encode(key).decode(), base64.b64encode(salt).decode()

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    salt_bytes = base64.b64decode(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=100_000,
        backend=default_backend()
    )
    try:
        kdf.verify(password.encode(), base64.b64decode(password_hash))
        return True
    except Exception:
        return False

# --- Encryption/Decryption (for password entries) ---
def generate_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

def encrypt_password(plain_password: str, master_password: str, salt: str) -> str:
    salt_bytes = base64.b64decode(salt)
    key = generate_key(master_password, salt_bytes)
    f = Fernet(key)
    encrypted = f.encrypt(plain_password.encode())
    return encrypted.decode()

def decrypt_password(encrypted_password: str, master_password: str, salt: str) -> str:
    salt_bytes = base64.b64decode(salt)
    key = generate_key(master_password, salt_bytes)
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_password.encode())
    return decrypted.decode()
