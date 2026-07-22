# q1
for _ in range(15):
    inp = input('Enter a string: ')
    if inp[0] == inp[-1]:
        print(inp)

# q2
str1 = input('Enter the first string: ')
str2 = input('Enter the second string: ')
if len(str1) > len(str2):
    str1, str2 = str2, str1

if len(str1)*2 <= len(str2):
    print(str2)
else:
    print(str1)

# q3
s1 = input('Enter a string: ')
s2 = input('Enter a substring: ')

count = 0

for i in range(len(s1)-len(s2)+1):
    if s1[i:i+len(s2)] == s2:
        count += 1
print(count)

# q4
def clean_noise(string):
    total = 0
    nums = '0123456789'
    num = ''

    for i in range(len(string)):
        if string[i] in nums:
            num += string[i]
        else:
            if num:
                total += int(num)
                num = ''
    if num:
        total += int(num)
    return total


# q5
def delete_char(st, ch):
    cleaned = ''
    for char in st:
        if char == ch:
            continue
        cleaned += char
    return cleaned

# q6
def enc(message, key):
    cipher = ''
    for char in message:
        base = ord('A') if ord(char) in range(65, 91) else ord('a')
        if ord(char) not in range(base, base + 26):
            cipher += char
            continue
        cipher += chr(((ord(char) + key - base) % 26) + base)
    print(cipher)

def dec(cipher, key):
    message = ''
    for char in cipher:
        base = ord('A') if ord(char) in range(65, 91) else ord('a')
        if ord(char) not in range(base, base + 26):
            message += char
            continue
        message += chr(((ord(char) - key - base) % 26) + base)
    print(message)

