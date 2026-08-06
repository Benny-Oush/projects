import random
x = random.randint(0, 9)
y = random.randint(0, 9)
print(f'x = {x}, y = {y}')
if abs(x - y) == 3:
    print('the difference is 3')
