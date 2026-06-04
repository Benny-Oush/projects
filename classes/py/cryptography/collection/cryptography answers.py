import random

# A function that accepts a string and returns 6 new strings that
# end with the first 3 letters of the previous string 

def expand_key(txt):
    current = txt
    hashed = []
    for i in range(6):
        current = current[-3:] + current[:-3]
        hashed.append(current)
    return hashed

# A function that accepts a string and a list of indexes and returns a new
# string in which all of the letters of the original string are placed according
# to the indexes list

def permutation(txt, places):
    hashed = ''
    for i in places:
        hashed += txt[i]
    return hashed



def backwards_permutation(txt, places):
    dec = ''
    for i in range(len(txt)):
        dec += txt[places.index(i)]
    return dec


abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
swt = 'FDIPTNRHOXVZQJGUEWAKLYSMBC'

def switch(txt):
    res = ''
    for c in txt:
        i = abc.index(c)
        res += swt[i]
    return res


# A function that does the opposite of the switch function

def reverse_switch(txt):
    res = ''
    for c in txt:
        i = swt.index(c)
        res += abc[i]
    return res

# A function that creates a new string based on the
# indexes generated from the 2 given strings

def mod26(txt1, txt2):
    res = ''
    base = ord('A')
    for i in range(len(txt1)):
        i1 = ord(txt1[i]) - base
        i2 = ord(txt2[i]) - base
        res += chr(((i1 + i2) % 26) + base)
    return res

def reverse_mod26(msg, key):
    res = ''
    for i in range(8):
        c = abc.index(msg[i]) - abc.index(key[i])
        c %= 26
        res += abc[c]
    return res

def move(msg, n):
    return msg[-n:] + msg[:-n]


def reverse_move(msg, n):
    return msg[n:] + msg[:n]

def random_key():
    key = ''
    for _ in range(8):
        key += chr(random.randint(65, 90))
    return key

def net(msg, key):
    step1 = switch(msg)
    step2 = mod26(step1, key)
    step3 = permutation(step2, [7, 2, 4, 1, 6, 5, 0, 3])
    return step3

def reverse_net(cipher, key):
    step1 = reverse_switch(cipher)
    step2 = reverse_mod26(step1, key)
    step3 = reverse_switch(step2)
    return step3


def feistel(msg, key):
    left = msg[:8]
    right = msg[8:]
    keys = expand_key(key)
    for k in keys:
        new_left = right
        net_result = net(right, k)
        new_right = mod26(left, net_result)
        left, right = new_left, new_right
    return left + right

def reverse_feistel(cipher, key):
    left = cipher[:8]
    right = cipher[8:]
    keys = expand_key(key)
    for k in keys[::-1]:
        prev_right = left
        net_result = net(prev_right, k)
        prev_left = reverse_mod26(right, net_result)
        left, right = prev_left, prev_right
    return left + right


my_key = random_key()

print(f'My key: {my_key}')

cipher = feistel('AHOYGUYSEVERYDAY', my_key)

print(f'Cipher: {cipher}')

message = reverse_feistel(cipher, my_key)

print(f'The message was: {message}')
