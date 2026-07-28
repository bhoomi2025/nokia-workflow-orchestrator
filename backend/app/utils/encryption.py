from cryptography.fernet import Fernet


SECRET_KEY = b"qJlHADwT6r6gzyAvXQrlbI-gb2AjV_KmijY9D15lLv8="

fernet = Fernet(SECRET_KEY)


def encrypt_secret(plain_text: str) -> str:
    return fernet.encrypt(plain_text.encode()).decode()


def decrypt_secret(encrypted_text: str) -> str:
    return fernet.decrypt(encrypted_text.encode()).decode()