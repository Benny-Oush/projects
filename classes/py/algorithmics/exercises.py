# # exercise 1
# while True:
#     try:
#         num_1 = int(input("please enter a number: "))
#         num_2 = int(input("please enter a second number, bigger than the first one: "))
#         add = 0
#         if num_1 > num_2:
#             print("the second number must be bigger than the first one! \ndo as you are told!")
#         else:
#             break
#         for current in range(num_1, num_2 + 1):
#                 add += current
#         print(f"the sum of the numbers between {num_1}-{num_2} is:")
#         print(add)
#     except:
#         print("please use numbers!\n")

# # exercise 2
# max = 0
# min = 100
# num_of_students = int(input("how many students are in the group? "))
# for i in range(num_of_students):
#     student_age = int(input("how old is the student? "))
#     if student_age > max:
#         max = student_age
#     if student_age < min:
#         min = student_age
# if (max - min) > 3:
#     print("this group is heterogeneous")
# else:
#     print("this group is homogeneous")
#
# # exercise 3:
# # first way:
#
# while True:
#     num_of_nums = int(input("how many numbers do you want to enter? "))
#     max_result = int(input("what is the max result allowed? "))
#
#     if (num_of_nums > 1) and (max_result > 1):
#         break
#     else:
#         print("\nboth numbers must be greater than 1\n")
#
# bigest_num = int(input("enter number 1: "))
#
# found = False
#
# for i in range(num_of_nums - 1):
#     new_num = int(input(f"enter number {i+2}: "))
#     if new_num + bigest_num > max_result:
#         print(f"\nfound a pair over the allowed max result. \nthe pair is {bigest_num} and {new_num}")
#         found = True
#         break
#     if new_num > bigest_num:
#         bigest_num = new_num
#
# if not found:
#     print(f"\nall of the pairs are under the allowed max result.")
#
# # second way:
#
# while True:
#     requiredMax = int(input("What is the max result allowed (M)? "))
#     numOfInputs = int(input("How many numbers to enter (N)? "))
#
#     if (numOfInputs > 1) and (requiredMax > 1):
#         break
#     else:
#         print("\nBoth numbers must be greater than 1\n")
#
# numbers_list = []
# for i in range(numOfInputs):
#     currentNum = int(input(f"Enter number {i+1}: "))
#     numbers_list.append(currentNum)
#
# pairFound = False
#
# for i in range(len(numbers_list)):
#     for j in range(i + 1, len(numbers_list)):
#         if numbers_list[i] + numbers_list[j] > requiredMax:
#             print(f"\nFound a pair over the limit: {numbers_list[i]} + {numbers_list[j]} = {numbers_list[i] + numbers_list[j]}")
#             pairFound = True
#             break
#     if pairFound:
#         break
#
# if not pairFound:
#     print(f"\nAll pairs are under the limit of {requiredMax}.")
#
# # exercise 4
# number = int(input("please enter a number of seconds smaller than 86,400: "))
# hours = number//3600
# tmp = number % 3600
# minutes = tmp//60
# seconds = tmp % 60
# print(f"{hours}:{minutes}:{seconds}")
#
# # exercise 5
#
# print("Geometric Progression: ")
# a1 = int(input("enter the first term (a1): "))
# q = int(input("enter the common ratio (q): "))
# position = int(input("enter the term index (n): "))
# print(f"the terms of this Geometric Progression is: ")
# for i in range(position):
#     term = a1 * (q**(i))
#     print(term)
#
# # exercise 6
#
# sum = 0
# for i in range(1, 1000):
#     if (i) % 3 == 0 or i % 5 == 0:
#         sum += i
# print(sum)
#
# #  exercise 7
# while True:
#     in_num = int(input("please enter a number between 1 and 18: "))
#     if 1 <= in_num <= 18:
#         break
#     print("do as you are told!")
# print(f"the sum of the digits of the numbers below  is exactly {in_num}")
# for i in range(10, 100):
#     s_num = str(i)
#     dig_1 = int(s_num[0])
#     dig_2 = int(s_num[1])
#
#     if (dig_1 + dig_2) == in_num:
#         print(i)