# q1

def digits_sum(num):
    total = 0
    while num:
        digit = num % 10
        num //= 10
        total += digit
    return total

def find_largest_digits_sum(left, right):
    if left > right:
        left, right = right, left
    largest = 0
    largest_sum = 0
    for num in range(left, right + 1):
        total = digits_sum(num)
        if total > largest_sum:
            largest = num
            largest_sum = total
    print(largest)

left = int(input('Enter starting number: '))
right = int(input('Enter ending number: '))
find_largest_digits_sum(left, right)


# q2

num = int(input('Enter a number: '))

odd = 0
even = 0

while num:
    digit = num % 10
    num //= 10
    if digit % 2 == 0:
        even += 1
    else:
        odd += 1

if odd == even:
    print('שווה')
elif odd > even:
    print('קטן')
else:
    print('גדול')


# q3

def reverse(x: int) -> int:
    res = 0
    while x:
        res *= 10
        res += x % 10
        x //= 10
    return res


# q4

def count_digits(n):
    count = 0
    while n:
        count += 1
        n //= 10
    return count if count else 1

def merge(a: int, b: int) -> int:
    res = 0
    a_len = count_digits(a)
    b_len = count_digits(b)
    a = reverse(a)
    b = reverse(b)
    while a_len > 0 or b_len > 0:
        if a_len > 0:
            res *= 10
            res += a % 10
            a //= 10
            a_len -= 1
        if b_len > 0:
            res *= 10
            res += b % 10
            b //= 10
            b_len -= 1
    return res

print(merge(1000, 352))

# q5

found = []

for i in range(1000, 9901):
    if ((i // 100) + (i % 100)) ** 2 == i:
        found.append(i)
print(found)


# q6
from math import pi

small_radius = float(input('Enter the small radius: '))
big_radius = float(input('Enter the big radius: '))

small_size = (small_radius**2) * pi
big_size = (big_radius**2) * pi
diff1 = big_size - small_size

thickness = big_radius - small_radius
average = ((((small_radius*2) * pi) + ((big_radius*2) * pi))) / 2
diff2 = average * thickness

is_correct = diff1 == diff2


# q7
def convert_to_fahrenheit(c):
    return ((c * 9) / 5) + 32

def convert_to_celsius(f):
    return ((5 * f) - 160) / 9


for i in range(-273, 102, 11):
    print('+--------+--------+')
    print(f'| {convert_to_fahrenheit(i):6.1f} |  {i:4}  |')    
print('+--------+--------+')


# q8
for i in range(100, 1000):
    num = i
    total = 0
    while num:
        total += (num % 10)**3
        num //= 10
    if total == i:
        print(i)


# q9
for i in range(10000, 100000):
    if reverse(i) == i*4:
        print(i)


# q10
total = 0
for i in range(8):
    num = int(input(f'Enter digit {i+1}: '))
    if i % 2 == 0:
        total += num
        continue
   
    if (num * 2) > 9:
        num = num * 2
        while num:
            total += num % 10
            num //= 10
        continue
    total += num * 2

final = int(input('Enter the final digit: '))
check = (total % 10) + final