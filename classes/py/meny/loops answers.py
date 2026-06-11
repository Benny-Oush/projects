# 1

num = int(input('Enter a number: '))

while num < 1:
    print('Invailed number!')
    num = int(input('Enter a number: '))

div = int(input('Enter a divisor: '))

while div == 0:
    print('Divisor cannot be zero!')
    div = int(input('Enter a divisor: '))

for i in range(1, num+1):
    if i % div == 0:
        print(i)

# 2

count = 0

while True:
    num = int(input('Enter a number: '))

    if num == -1:
        print(count)
        break
    if num >= 0:
        count += 1

    
# 3

result = 'Series is ascending'

num = int(input('Enter a number: '))

count = 0

prev = -1

while True:
    if num == -1:
        break

    count += 1

    if num <= prev:
        result = 'Series is not ascending'
        break
    prev = num

    num = int(input('Enter a number: '))

if count == 0:
    print('No sequence of numbers was entered.')

elif count == 1:
    print('Only one number was entered')

else:
    print(result)


# 4

n = int(input('Enter N: '))

prev = -1

result = 'Series is ascending'

for i in range(n):
    num = int(input(f'Enter number {i+1}#: '))
    if num <= prev:
        result = 'Series is not ascending'
        break
    prev = num

if n < 2:
    print('No comparison was made')
else:
    print(result)

# 5

largest = -1
second_largest = -1
count = 0

while True:
    num = int(input('Enter a number: '))

    if num == -1:
        break

    if num > largest:
        second_largest = largest
        largest = num

    elif num > second_largest and num != largest:
        second_largest = num
    
    count += 1
    
if count < 2:
    print('Largest:', largest)
    print('No other number')
elif second_largest == -1:
    print('Largest:', largest)
else:
    print(f'Largest: {largest}\n Tow largest: {largest}, {second_largest}')


# 6
num = int(input('Enter a number: '))

largest = -1
right_appearance = 0
left_appearance = 0
i = 0

if num != 0:
    while num:
        digit = num % 10
        if digit > largest:
            largest = digit
            right_appearance = i
            left_appearance = i
        elif digit == largest:
            left_appearance = i
        
        i += 1
        num //= 10

    if largest != -1:
        print('Largest digit:', largest)
    print('Right appearance:', right_appearance)
    if left_appearance != 0:
        print('Left appearance:', left_appearance)
else:
    print('Largest: 0')
    print('Right appearance: 0')

# 7 
total_RTL = 0
total_LTR = 0
power = 1

num = []

while True:
    digit = int(input('Enter 1 or 0 (Enter -1 to end): '))
    if digit == -1:
        break
    total_LTR = (total_LTR * 2) + digit

    total_RTL = total_RTL + (digit * power)
    power *= 2 


print(f'The number is:')
print('Right to left', total_RTL)
print('Left to right:', total_LTR)

# 8
# הפתרון הכי פשוט עם אופרטור + בלבד

maxi = int(input('Enter a number: '))
mini = int(input('Enter a second number: '))

if maxi < mini:
    mini, maxi = maxi, mini

total = 0

for _ in range(mini):
    total += maxi

print("The result is:", total)


# הפתרון הכי יעיל (חיבור לוגריתמי)

maxi = int(input('Enter a number: '))
mini = int(input('Enter a second number: '))

if maxi < mini:
    mini, maxi = maxi, mini

total = 0

current_value = maxi

while mini > 0:
    if mini % 2 != 0:
        total += current_value
        mini -= 1
    
    if mini > 0:
        current_value = current_value + current_value
        mini //= 2

print("The result is:", total)