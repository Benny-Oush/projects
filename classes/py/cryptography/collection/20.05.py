def inv(num, mod):
    for i in range(mod):
        if num * i % mod == 1:
            return i

def caesar_enc(msg, k):
    enced = ''
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for char in msg:
        char = char.lower()
        if char not in alphabet:
            enced += char
            continue
        enced += alphabet[(alphabet.index(char) + k) % len(alphabet)]
    return enced

def caesar_dec(cipher, k):
    return caesar_enc(cipher, -k)


def caesar_enc2(msg, k):
    enced = ''
    for char in msg:
        if char.isupper():
            base = ord('A')
        else:
            base = ord('a')
        if not (64 < ord(char) < 91 or 96 < ord(char) < 123):
            enced += char
            continue
        enced += chr((((ord(char) - base) + k) % 26) + base)
    return enced

def caesar_dec2(cipher):
    for k in range(1, 26):
        print(f'key: {k} --- "{caesar_enc2(cipher, -k)}"\n---')

def vigenere_enc(msg, key):
    char_count = 0
    cipher = ''
    key = key.lower()
    for char in msg:
        if not (64 < ord(char) < 91 or 96 < ord(char) < 123):
            cipher += char
        else:
            if char.isupper():
                base = ord("A")
            else:
                base = ord('a')
            char_ind = ord(char) - base
            key_char = key[char_count % len(key)]
            key_char_ind = ord(key_char) - ord('a')
            cipher_ind = (char_ind + key_char_ind) % 26
            cipher_char = chr(cipher_ind + base)
            cipher += cipher_char
            char_count += 1
    return cipher

print(vigenere_enc('Crypto is cool', 'sucks'))

# print(caesar_dec2('mobizdy sc myyv'))