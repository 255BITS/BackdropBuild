import os
from cryptography.fernet import Fernet

class CredentialsService:
    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("No encryption key found in environment variables.")
        self.fernet = Fernet(key)

    def encrypt(self, message: str) -> str:
        return self.fernet.encrypt(message.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()
# Example Usage
if __name__ == "__main__":
    # Make sure to set the ENCRYPTION_KEY in your environment variables
    service = CredentialsService()

    # Encrypt a message
    secret = service.encrypt("Hello, World!")
    print(f"Encrypted: {secret}")

    # Decrypt the message
    decrypted = service.decrypt(secret)
    print(f"Decrypted: {decrypted}")

