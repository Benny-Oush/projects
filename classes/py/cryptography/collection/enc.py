from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

nonce = os.urandom(12)

data = input('Enter your data: ')

key = AESGCM.generate_key(bit_length=256)

aes = AESGCM(key)

cipher = aes.encrypt(nonce, data.encode(), None)

print(f'Your cipher is: {cipher}')

decrypted = aes.decrypt(nonce, cipher, None)

print(f'Your secret is: {decrypted.decode()}')