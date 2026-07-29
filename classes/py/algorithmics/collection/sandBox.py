import time


# def sumOfDigits(num):
#     sum = 0
#     while num > 0:
#         sum += num % 10
#         num //= 10
#     return sum
#
# num = int(input("Enter a number: "))
# result = sumOfDigits(num)
# print(f"The digits sum of {num} is {result}")
from cmath import inf
from operator import index

from pandas.util.version import Infinity


#
# def sumOfKind(num_input):
#     even_count = 0
#     odd_count = 0
#     for num in num_input:
#
#         if num % 2 == 0:
#             even_count += 1
#         else:
#             odd_count += 1
#
#     if even_count > odd_count:
#         return "evens"
#     elif even_count < odd_count:
#         return "odds"
#     else:
#         return "equal"
#
# num_input = int(input("Please enter a number "))
# result = sumOfKind(num_input)
# if result == "evens":
#     print(f"There are more even numbers in {num_input} than odd numbers ")
# elif result == "equal":
#     print(f"There is an equal number of odd and even numbers in {num_input} ")
# else:
#     print(f"There are more odd numbers in {num_input} than even numbers ")


# sol 1
# def reverse(num_input):
#     return num_input[::-1]

# num_input = input("Please enter a number ")
# result = reverse(num_input)
# print(f"The reversed number is {result} ")

# # sol 2
# def reverse(num):
#     reversed = 0
#     while num > 0:
#         reversed = (reversed * 10) + num % 10
#         num //= 10
#     return reversed
#
# num = int(input("Enter a number: "))
# result = reverse(num)
# print(f"The reversed number is {result} ")

# def reverse(num):
#     reversed = 0
#     while num > 0:
#         reversed = (reversed * 10) + num % 10
#         num //= 10
#     return reversed
#
# def merge(num1, num2):
#     r1 = reverse(num1)
#     r2 = reverse(num2)
#
#     merged = 0
#
#     while r1 > 0 or r2 > 0:
#         if r1 > 0:
#             merged = (merged * 10) + r1 % 10
#             r1 //= 10
#
#         if r2 > 0:
#             merged = (merged * 10) + r2 % 10
#             r2 //= 10
#     return merged
#
# n1 = int(input("Enter a number: "))
# n2 = int(input("Enter a second number: "))
#
# print(f"The merged number is {merge(n1,n2)}")

#
# def check_special_property(n):
#     right_part = n % 100
#     left_part = n // 100
#     return (left_part + right_part) ** 2 == n
#
# for i in range(1000, 10000):
#     if check_special_property(i):
#         print(i)
#
# def NumOfNums():
#     while True:
#         try:
#             num_of_nums = int(input("how many times do you want this program to run? "))
#             if num_of_nums >= 0:
#                 return num_of_nums
#             else:
#                 print("\nError! Please enter a positive number.\n ")
#         except ValueError:
#             print("\nError! Please use positive numbers only!\n")
#
# two_digit_count = 0
# even_sum = 0
#
# run_times = NumOfNums()
#
# for i in range(run_times):
#     while True:
#         try:
#             n = int(input(f"Please enter number {i + 1}: "))
#             if n >= 0:
#                 if 10 <= n <= 99:
#                     two_digit_count += 1
#                 if n % 2 == 0:
#                     even_sum += n
#                 break
#             else:
#                 print("\nError! Please use positive numbers only\n")
#         except ValueError:
#             print("\nError! Please use positive numbers only\n")
#
# print(f"\nOf the numbers you entered, {two_digit_count} were two digits numbers."
#       f" \nThe sum of the even numbers you entered is {even_sum}. ")
# sol 1
# sol 1
# def get_largest_sum():
#     while True:
#         try:
#             left = int(input("Please enter a number: "))
#             if left < 0:
#                 raise ValueError
#             else:
#                 break
#         except ValueError:
#             print("Error! Please use positive numbers only\n")
#
#     while True:
#         try:
#             right = int(input("Please enter a second, bigger number: "))
#             if right < left:
#                 raise ValueError
#             else:
#                 break
#         except ValueError:
#             print("The number must be bigger than the first one \n")
#     winner = left
#     largest_sum = left
#     for current_num in range(left, right+1):
#         current_total = 0
#         temp = current_num
#         while temp > 0:
#             current_total += temp % 10
#             temp //= 10
#
#         if current_total > largest_sum:
#             largest_sum = current_total
#             largest_num = current_num
#
#     return largest_num
#
# print(f"the number that has the largest digits sum in the given range is {get_largest_sum()}")

# sol 2

# def get_largest_sum():
#     left = int(input("Enter the start of the desired range: "))
#     right = int(input("Enter the desired end of the range: "))
#     largest_num = left
#     largest_sum = 0
#     for current_num in range(left, right+1):
#         current_total = 0
#         temp = current_num
#         while temp > 0:
#             current_total += temp % 10
#             temp //= 10
#         if current_total > largest_sum:
#             largest_sum = current_total
#             largest_num = current_num
#     return largest_num
#
# print(f"the number that has the largest digits sum in the given range is {get_largest_sum()}")

# arr = [0, 1, 3, -2, 0, 0, 7, 2, 0]
#
# def removeZeros(numbers):
#     newArr = []
#     for num in numbers:
#         if num != 0:
#             newArr.append(num)
#     return newArr
# print(removeZeros(arr))

# def sum_of_met(met):
#     sum = 0
#     for arr in met:
#         for num in arr:
#             sum += num
#     return sum
# met = [
#     [4, 7, 1, 2],
#     [2, 3, 5, 7],
#     [8, 2, 5, 1],
#     [3, 6, 5, 6]
# ]
# sumOfMet = sum_of_met(met)
# print(sumOfMet)

# def arrange(met):
#     for i in range(len(met)):
#         row = met[i]
#         smallest_val = inf
#         smallest_index = -1
#
#         for j in range(len(row)):
#             if row[j] < smallest_val:
#                 smallest_val = row[j]
#                 smallest_index = j
#         row[i], row[smallest_index] = row[smallest_index], row[i]
#
#     return met
#
# met = [
#     [4, 7, 1, 2],
#     [2, 3, 5, 7],
#     [8, 2, 5, 1],
#     [3, 6, 5, 6]
# ]
#
# arranged = arrange(met)
# print(arranged)

# def removeZeros(numbers):
#     pointer = 0
#     for i in range(len(numbers)):
#         if numbers[i] != 0:
#             numbers[pointer] = numbers[i]
#             pointer += 1
#
#     return numbers
#
# arr = [0, 1, 3, -2, 0, 0, 7, 2, 0]

# zeroRemoved = removeZeros(arr)
# print(zeroRemoved)

# arr = [0, 1, 3, -2, 0, 0, 7, 2, 0]

# arr = [5, 6, 8, 4, 8, 2]
# arr2 = [3, 5, 6, 8, 4, 8, 2, 5, 9, 8]
#
# def is_contained(arr, arr2):
#     testArr = []
#     for i in range(len(arr)):
#         if arr[i] in arr2:
#             testArr.append(arr[i])
#     if testArr == arr:
#         return True
#     else:
#         return False
#
# resulte = isContained(arr, arr2)
# print(resulte)


# def find_char(str1, str2, str3, str4, str5):
#     all_strings = [str1, str2, str3, str4, str5]
#     for s in all_strings:
#         if s[0] == s[-1]:
#             print(s)
#
# findChar("Benny", "wow", "mom", "dad", "computer")

# def revers(str):
#     print(str[::-1])
# revers("Benny")


# # sol1
# def count_substrs(string, substr):
#     count = 0
#     test_string = ""
#     for character in range(len(string)):
#         test_string += string[character]
#         if len(test_string) > len(substr):
#             test_string = test_string[1:]
#         if test_string == substr:
#             count += 1
#     return count
#
# string1 = "cabc"
# string2 = "cabcabcacabcbbcabca"
# result = count_substrs(string2, string1)
# print(result)

# # sol2
# def count_substrs(string, substr):
#     count = 0
#     sub_len = len(substr)
#
#     for i in range(len(string) - sub_len + 1):
#
#         if string[i:i + sub_len] == substr:
#             count += 1
#     return count
#
# str1 = "cabc"
# str2 = "cabcabcacabcbbcabca"
# result = count_substrs(str2, str1)
# print(f"The string '{str1}' appears {result} times within the '{str2}' string.")

# def sum_of_integers(string):
#     integers = ""
#     sum = 0
#     for i in range(len(string)):
#         if string[i].isdigit():
#             integers += string[i]
#             if i == len(string) - 1 or not string[i + 1].isdigit():
#                 sum += int(integers)
#                 integers = ""
#     return sum
#
# string = "600cw580daba12ab"
# result = sum_of_integers(string)
# print(result)


# random_strings = [
#     "AALQ", "AFAF", "RUAA", "AOPA", "AKRA", "AACT", "ALMA",
#     "KAAZ", "BANA", "GALA", "FAAY", "SAVA", "WAAK", "AETA",
#     "RAHA", "AABX", "AXZA", "MAAS", "KANA", "GBAA", "AANO",
#     "AQUA", "PAAM"
# ]


# def check_for_A(string_list):
#     valid_list_count = 0
#     for string in string_list:
#         if "AA" not in string:
#             A_count = 0
#             for i in string:
#                 if i == "A":
#                     A_count += 1
#             if A_count > 1:
#                 valid_list_count += 1
#     return valid_list_count
#
# result = check_for_A(random_strings)
# print(result)

# string = "ABABABAB"
#
# def is_divisible(string, k):
#     if len(string) % k == 0:
#         len_of_substr = len(string) // k
#         target_substr = string[:len_of_substr]
#         for i in range(1, k):
#             start = i * len_of_substr
#             end = (i + 1) * len_of_substr
#             if string[start:end] != target_substr:
#                 return False
#         return True
#     else:
#         return False
# print(is_divisible(string,2))
#
# string = "AfBcAfBcAfBcN"
#
# def max_divisor(string):
#     n = len(string)
#     if n == 0:
#         return -1
#     for i in range(n,1,-1):
#         if n % i == 0:
#             length = n // i
#             if string[:length] * i == string:
#                 return i
#     return -1
# print(max_divisor(string))
#
#
# test_strings = [
#     "ABCDE",
#     "AAAAAA",
#     "123123",
#     "HELLO",
#     "PYTHON",
#     "AAAAA",
#     "10101010",
#     "MISSISSIPPI",
#     "ABCABCABCABC",
#     "Z",
#     "APPLE",
#     "WOW",
#     "abcabc",
#     "12345678",
# ]
#
# def check_for_not_divisible(strings):
#     not_divisible = []
#     for string in strings:
#         is_not_divisible = True
#         n = len(string)
#         if n == 0:
#             continue
#         for i in range(n,1,-1):
#             if n % i == 0:
#                 length = n // i
#                 if string[:length] * i == string:
#                     is_not_divisible = False
#                     break
#         if is_not_divisible:
#             not_divisible.append(string)
#     return not_divisible
# print(check_for_not_divisible(test_strings))








