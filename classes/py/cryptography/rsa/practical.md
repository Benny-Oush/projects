# Python practical cryptography

## Installation

```bash
pip install bcrypt cryptography
```

## Encoding/Decoding keys

For symmetric keys and nonces: convert bytes to base64 strings and backwards

### bytes -> base64

```python
import base64

def bytes_to_base64(*items: bytes) -> str:
    """
    Accepts any number of byte objects.
    Encodes each to Base64 and joins them with ':'.
    Returns a string.
    """
    encoded_parts = [
        base64.b64encode(b).decode('ascii')
        for b in items
    ]
    return ":".join(encoded_parts)
```

### base64 -> bytes

```python
import base64

def base64_to_bytes(data: str) -> tuple:
    """
    Splits colon-separated Base64 string,
    decodes each part back to bytes,
    returns tuple of bytes.
    """
    parts = data.split(":")
    decoded = tuple(
        base64.b64decode(p.encode('ascii'))
        for p in parts
    )
    return decoded
```

## SHA-256 (hashing)

```python
import hashlib

def sha256_hash(data: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(data)
    return h.digest()

```

## bcrypt (password hashing)

```python
import bcrypt

password = b"my_secret_password"

# Hash
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
print("Hashed:", hashed)

# Verify
ok = bcrypt.checkpw(password, hashed)
print("Password correct?", ok)
```

## RSA

### Key Generation

```python
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

priv, pub = generate_rsa_keys()
```

### Serialization

As `priv` and `pub` are objects, when sending the public key we need to send text.

This is called serialization.

from cryptography.hazmat.primitives import serialization

```python
def serialize_public_key(public_key) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
```

The reverese operation, converting a serialized public key into an object, is called deserialization.

```python
from cryptography.hazmat.primitives import serialization

def deserialize_public_key(data: bytes):
    return serialization.load_pem_public_key(data)

```

### Encrypt / Decrypt (OAEP padding)


```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

message = b"secret message"

ciphertext = pub.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

plaintext = priv.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

```

### Sign / Verify (PSS)

```python
from cryptography.exceptions import InvalidSignature

message = b"important data"

signature = priv.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

try:
    pub.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signature valid")
except InvalidSignature:
    print("Invalid signature")
```

## AES-GCM

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aes = AESGCM(key)

nonce = os.urandom(12)  # must be unique per encryption
data = b"top secret message"

ciphertext = aes.encrypt(nonce, data, None)
print("Ciphertext:", ciphertext.hex())

plaintext = aes.decrypt(nonce, ciphertext, None)
print("Decrypted:", plaintext)
```

## ChaCha20-Poly1305

```python
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os

key = ChaCha20Poly1305.generate_key()
chacha = ChaCha20Poly1305(key)

nonce = os.urandom(12)  # 96-bit nonce
data = b"secret stream cipher message"

ciphertext = chacha.encrypt(nonce, data, None)
print("Ciphertext:", ciphertext.hex())

plaintext = chacha.decrypt(nonce, ciphertext, None)
print("Decrypted:", plaintext)
```
