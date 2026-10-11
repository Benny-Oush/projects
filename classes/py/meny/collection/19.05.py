# a = float(input("Enter A: "))
# b = float(input("Enter B: "))
# c = float(input("Enter C: "))
# delta =  (b ** 2) - (4 * a * c)
# if delta < 0:
#     print("Both solutions are complex")
# elif delta == 0:
#     print(f"Only one solution: x = {-b / (2 * a)}")
# else:
#     solutions = [
#         (-b + delta ** 0.5) / (2 * a),
#         (-b - delta ** 0.5) / (2 * a)
#     ]
#     for i in range(len(solutions)):
#         print(f"solution {i+1}: x = {solutions[i]}")

# mini = int(input("Enter a number: ")) 
# middle = int(input("Enter a second number: "))
# maxi = int(input("Enter a third number: "))

# # sol 1
# if not mini < middle < maxi:
#     if mini > maxi:
#         maxi, mini = mini, maxi
#     if not mini < middle < maxi:
#         if middle > maxi:
#             maxi, middle = middle, maxi
#         else:
#             mini, middle = middle, mini


# # sol 2
# if mini > middle:
#     mini, middle = middle, mini

# if middle > maxi:
#     middle, maxi = maxi, middle

# if mini > middle:
#     mini, middle = middle, mini

# print(mini, middle, maxi)


# num = int(input("Enter a number: "))
# total = 0
# num = int((num**2)**0.5)
# while num:
#     total += num % 10
#     num //= 10
# print(f"Sum of the digits: \n\t-{total}-")



# a = int(input('Enter an odd number: '))

# space = a // 2
# asterisk = 1

# for row in range(a//2 + 1):

#     for s in range(space):
#         print(' ', end=' ')
#     for star in range(asterisk):
#         print('*', end=' ')

#     space -= 1
#     asterisk += 2
#     print()



# # AI vers

# def print_pyramid(size: int):
#     """Prints a centered pyramid of '*' with the given odd size."""
#     space = size // 2
#     asterisk = 1

#     for _ in range(size // 2 + 1):
#         # Print leading spaces
#         for _ in range(space):
#             print(' ', end=' ')
#         # Print stars
#         for _ in range(asterisk):
#             print('*', end=' ')
#         # Move to next row
#         print()
#         space -= 1
#         asterisk += 2


# def get_odd_positive_int(prompt = "Enter an odd number: ") -> int:
#     """Prompts the user until they enter a valid odd positive integer."""
#     while True:
#         try:
#             num = int(input(prompt))
#             if num > 0 and num % 2 == 1:
#                 return num
#             else:
#                 print("❌ Please enter a positive odd integer.")
#         except ValueError:
#             print("❌ Invalid input. Please enter a number.")


# print_pyramid(get_odd_positive_int())


# size = int(input('Enter the size of the multiplication table: '))

# scale = len(str(size))+3
# line = "+" + ("-" * (scale + 2) + "+") * size
# print(line)


# for i in range(1, size + 1):
#     print('', end='')
#     for j in range(1, size + 1):
#         print('|' + f'{j*i:{scale}}', end='  ')
#     print('|')
#     print(line)


