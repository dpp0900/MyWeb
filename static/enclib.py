import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import os

class eel:
    def __init__(self, key):
        self.key = key
        self.salt = None

    def encode_base64(self, message):
        return base64.b64encode(message)

    def decode_base64(self, encoded_message):
        return base64.b64decode(encoded_message)

    def encrypt_aes(self, plaintext):
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(plaintext)
        return (iv, ciphertext)

    def decrypt_aes(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext

    def salting(self):
        salt = os.urandom(16)
        hashed_password = hashlib.pbkdf2_hmac('sha512', self.key.encode('utf-8'), salt, 189389)
        self.salt = salt
        self.key = hashed_password
        return (salt, hashed_password)
        