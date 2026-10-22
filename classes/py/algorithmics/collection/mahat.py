# # 1
# for i in range(1, 1001):
#     num = i
#     total = 0
#     while num:
#         total += num % 10
#         num //= 10
#     if i % total == 0:
#         print(i)

# 2
# phone_num = ''
# is_valid = False
# count = 0
# numbers = '0123456789'
# while not is_valid:
#     phone_num = input("Enter a valid phone number: ")
#     count += 1
#     if len(phone_num) != 11 or phone_num[0:2] != "05" or phone_num[2] == "9" or phone_num[3] != "-":
#         continue
#     all_are_numbers = True
#     for i in range(2, 11):
#         if i == 3:
#             continue
#         in_numbers = False
#         for j in range(10):
#             if phone_num[i] == numbers[j]:
#                 in_numbers = True
#                 break
#         if not in_numbers:
#             all_are_numbers = False
#             break
#     if all_are_numbers:
#         is_valid = True

# print(f"Valid phone number!\nTotal inputs: {count}")

# # 3

def is_ordered(arr):
    seen_odd = False
    for i in range(len(arr)):
        if arr[i] % 2 == 0:
            if seen_odd:
                return False
        else:
            seen_odd = True
    return True

import random
def build_ordered(size, x, y):
    arr = []
    seen_odd = False
    while len(arr) < size:
        next_num = random.randint(x, y)
        if next_num % 2 == 0:
            if seen_odd:
                continue
        else:
            seen_odd = True
        arr.append(next_num)
    return arr

def get_bigest_num(arr):
    """Even indexes ascending, odd indexes descending, even arr length"""
    if not arr or len(arr) % 2 != 0:
        return
    return arr[1] if arr[1] > arr[-2] else arr[-2]

def secret(s): 
    for i in range(0, len(s), 2): 
        if s[i]>='A' and s[i]<='Z': 
           return False 
    for i in range(1, len(s), 2): 
        if s[i]<'A' or s[i]>'Z': 
            return False 
    return True 

def mystery(a): 
    for i in range(0,len(a),2): 
        if secret(a[i]) == secret(a[i+1]): 
            return False 
    return True 

