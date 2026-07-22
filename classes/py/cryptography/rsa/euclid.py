
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y

def modinv(e, phi):
    g, x, _ = egcd(e, phi)
    if g != 1:
        raise ValueError("Inverse does not exist")
    return x % phi

def is_prime(n):
    if n == 2:
        return True
    if n < 2:
        return False
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**(0.5)) + 1, 2):
        if n % i == 0:
            return False
    return True

