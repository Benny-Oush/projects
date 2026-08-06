

# def find_common(arr):
#     count = -1
#     largest = float("-inf")
#     for num in arr:
#         if num > largest:
#             largest = num
#             count += 1
#     return count

# nested_list = [[1, 2, 3], [4, 5], [6, 7, 8]]
# arr = [1, 2, 3, 4, 5, 4, 7, 1, 9]
# arr2 = [1, 2, 3, 4, 5, 6, 3]
# arr3 = [34, 56, 54, 98, 543, 176, 3, 27, 65, 12]
# arr = ["apple", "banana", "cherry", "date", "elderberry", 
#                "fig", "grape", "honeydew", "kiwi", "lemon", 
#                "mango", "nectarine", "orange", "papaya", "quince"]
# print(find_common(arr3))

#13. Write a code that repeatedly asks the user for words and prints only those that
#  start with the letter 'a', stopping when the user enters "stop"

# num = int(input("Please enter a number: "))
# are_positive = True
# while num != 0:
#     if num < 0:
#         are_positive = False
#     num = int(input("Please enter a number: "))
# print(are_positive)

# import random

# score = 0
# for i in range(1, 11):
#     a = random.randint(1, 10)
#     b = random.randint(1, 10)
#     answer = int(input(f"Exercise {i}/10: {a}x{b}: "))
#     if answer == a * b:
#         score += 10
#     else:
#         score -= 4
#     while answer != a * b:
#         print("Wrong answer!")
#         answer = int(input(f"Exercise {i}/10: {a}x{b}: "))
# print(f"Score: {score} 🎉")







# def is_prime(num):
#     if num < 2:
#         return False
#     for i in range(2, int(num**0.5) + 1):
#         if num % i == 0:
#             return False
#     return True

# def print_primes(x):
#     count = 0
#     for i in range(2, x):
#         if is_prime(i):
#             print(i)
#             count += 1
#     print(count)

# print_primes(1000)




# def is_prime(num):
#     if num < 2:
#         return False
#     for i in range(2, int(num**0.5) + 1):
#         if num % i == 0:
#             return False
#     return True

# def print_prime_divisors(num):
#     for i in range(1, num + 1):
#         if num % i == 0 and is_prime(i):            
#             print(i)

# print_prime_divisors(18)


# def find_all_prime_divisors(n):
#     i = 2
#     while n > 1:
#         if n % i == 0:
#             print(i)
#             n //= i
#         else:
#             i += 1

# def are_not_foreigns(a, b):
#     i = min(a, b)
#     while i >= 2:
#         if a % i == 0 and b % i == 0:
#             return i
#         i -= 1
#     return 1

# print(are_not_foreigns(1001, 2003))

# def are_not_foreigns_fast(a, b):
#     if a < b:
#         a, b = b, a
#     while b:
#         a, b = b, a % b
#     return a

# print(are_not_foreigns_fast(1000000001, 2000000003))



# def gcd(a, b):
#     if a < b:
#         a, b = b, a
#     while b:
#         a, b = b, a % b
#     return a

# def euler(n):
#     count = 0
#     for i in range(1, n):
#         if gcd(n, i) == 1:
#             count += 1
#     return count


# print(euler(35))
