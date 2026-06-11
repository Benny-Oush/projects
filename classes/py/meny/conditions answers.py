# 1
num = int(input("Enter a number: "))
if num % 2 != 0:
    print(num, 'is odd')
else:
    print(num, 'is even')

# 2
num = int(input('Enter a number: '))
if num < 0:
    print(num, 'is negative')
elif num == 0:
    print('It is 0')
else:
    print(num, 'is positive')

# 3
year = int(input('Enter a year: '))
if (year % 100 != 0 and year % 4 == 0) or year % 400 == 0:
    print('Leap year')

# 4
num = int(input('Enter a number: '))
num2 = int(input('Enter a second number: '))
if num > num2:
    print(num, 'is bigger')
elif num2 > num:
    print(num2, 'is bigger')
else:
    print('Equal')

# 5
age = int(input('Enter a age: '))
print('Can vote' if age >= 18 else "Can't vote")

# 6
score = int(input('Enter your score: '))
print('You passed' if score >= 60 else 'You failed')

# 7
num = int(input('Enter a number: '))
if num % 3 == 0 and num % 5 == 0:
    print(num, 'is dividable by both 3 and 5')
else:
    print(num, 'is not dividable by both 3 and 5')

# 8
letter = input('Enter a letter: ')
print(letter, end=' is Uppercase\n' if letter.isupper() else ' is Lowercase\n')

# 9
angle = int(input('Enter an angle: '))
angle += int(input('Enter a second angle: '))
angle += int(input('Enter a third angle: '))

print('It is a triangle' if angle == 180 else 'It is not a triangle')

# 10
num = int(input('Enter a number: '))
print('Lucky number!' if num % 10 == 7 else 'Plain number')

# 11
num1 = int(input('Enter a number: '))
num2 = int(input('Enter a second number: '))
num3 = int(input('Enter a third number: '))

if num1 < num2 < num3:
    print('Numbers are ascending')
elif num1 > num2 > num3:
    print('Numbers are in descending')
else:
    print('Numbers not ordered')

# 12
day = int(input('Enter a day: '))
month = int(input('Enter a month: '))
year = int(input('Enter a year: '))

is_leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

days_in_month = [31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

if year > 0 and 1 <= month <= 12 and 1 <= day <= days_in_month[month - 1]:
    print('Valid date')
else:
    print('Date is not valid')

# 13
a = int(input('Enter first length: '))
b = int(input('Enter second length: '))
c = int(input('Enter third length: '))

if a + b > c and a + c > b and b + c > a:
    if a == b == c:
        print('Equilateral triangle')
    elif a == b or b == c or a == c:
        print('Isosceles triangle')
    else:
        print('Scalene triangle')
else:
    print('Not a triangle')

# 14
num = int(input('Enter a three-digit number: '))
digit_sum = num // 100 + (num // 10) % 10 + num % 10
print('Sum is even' if digit_sum % 2 == 0 else 'Sum is odd')

# 15
num = int(input('Enter a number: '))
div_by_3 = num % 3 == 0
ends_with_3 = num % 10 == 3

if div_by_3 and ends_with_3:
    print('Very special')
elif div_by_3 or ends_with_3:
    print('Special number')
else:
    print('Not special')