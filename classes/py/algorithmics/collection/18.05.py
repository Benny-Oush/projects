def count_consonants(txt):
    vowels = ('a', 'e', 'i', 'o', 'u')
    count = 0
    for char in txt:
        if 96 < ord(char) < 123:
            if char.lower() not in vowels:
                count += 1
    return count

def is_one_a_digit(txt):
    for char in txt:
        if 47 < ord(char) < 58:
            return True
    return False
        

def count_spaces(txt):
    count = 0
    for char in txt:
        if char == ' ':
            count += 1
    return count

def return_uppercase(txt):
    for i in range(len(txt)):
        if txt[i] == ' ':
            return i
    return False


def return_all_uppercases(txt, c):
    new_string = ''
    for char in txt:
        if char == ' ':
            new_string += c
        else:
            new_string += char
    return new_string

def return_all_up(txt, c):
    return txt.replace(' ', c)
    
def are_the_same(txt):
    count = 0
    for char in txt:
        if char == txt[0]:
            count += 1
    return count

def remove_all_last(txt, c1, c2):
    new_string = '' 
    for char in txt:
        if char == c1:
            new_string += c2
        else:
            new_string += char
    return new_string


def longest_space_sequence(txt):
    longest = 0
    tmp = 0
    for i in range(len(txt)):
        if txt[i] == ' ':
            tmp += 1
        else:
            if tmp > longest:
                longest = tmp
            tmp = 0

    return longest 

def longest_vowels_sequence(txt):
    longest = 1
    tmp = 1
    prev = txt[0]
    for char in txt[1:]:
        if char.lower() == prev.lower():
            tmp += 1
            if tmp > longest:
                longest = tmp
        else:
            prev = char
            tmp = 1
    return longest


def reverse_str(txt):
    new_string = ''
    for i in range(len(txt) -1, -1, -1):
        new_string += txt[i]
    return new_string == txt
    
def move_first_char(txt):
    return txt[3:] + txt[3:]


def move_chars(txt, n):
    return txt[-n:] + txt[:-n]

def get_next_letter(c):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return alphabet[(alphabet.index(c) + 1) % len(alphabet)]

def get_next_letter(c):
    if c == 'z': return 'a'
    if c == 'Z': return 'A'
    return chr(ord(c)+1)

def get_next_letter2(c):
    base = ord('A') if c.isupper() else ord('a')
    return chr((ord(c) - base + 1) % 26 + base)

def replase_with_next(txt):
    new_string = ''
    for char in txt:
        if char == 'z':
            new_string += 'a'
        elif char == 'Z':
            new_string += 'A'
        else:
            new_string += chr(ord(char) + 1)
    return new_string


def words_counter(txt):
    count = 0
    string_list = txt.split()
    for word in string_list:
        count += 1
    return count

# def words_counter2(txt):
#     count = 1
#     for char in txt:
#         if char == ' ':
#             count += 1
#     return count

def get_longest(txt):
    string_list = txt.split()
    shortest = string_list[0]
    for word in string_list:
        if len(word) < len(shortest):
            shortest = word
    return shortest

def are_all_vowels_in(txt):
    vowels = ('a', 'e', 'i', 'o', 'u')
    for char in vowels:
        if char not in txt:
            return False
    return True

def are_all_digits_in(txt):
    for i in range(48, 58):
        if chr(i) not in txt:
            return False
    return True

# print(are_all_digits_in('a0 g123456789KH Loeipk ludoz'))
# print(ord("A"), ord("Z"))


