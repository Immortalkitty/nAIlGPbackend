import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def load_private_key():
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    return private_key

def decrypt_message(encrypted_message):
    private_key = load_private_key()

    try:
        encrypted_bytes = base64.b64decode(encrypted_message)
        decrypted_data = private_key.decrypt(
            encrypted_bytes,
            padding.PKCS1v15()
        )
        return decrypted_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
