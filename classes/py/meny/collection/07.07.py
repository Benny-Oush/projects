matrix = []

limit = int(input('Enter the number of lists in the matrix: '))

start = int(input('Enter the first number: '))

for i in range(limit):
    matrix.append([])
    
    for j in range(limit):
        matrix[i].append(start)
        start += 1    

print('\nOriginal:')
for row in matrix:
    for item in row:
        print(f'{item:3} ', end='')
    print()

snake = []

for i in range(len(matrix)):
    snake.append([])

    for j in range(len(matrix[i])):
        if i % 2 == 0:
            snake[i].append(matrix[i][j])
        else:
            snake[i].append(matrix[i][len(matrix[i]) - 1 - j])

print('\nSnake:')
for row in snake:
    for item in row:
        print(f'{item:3} ', end='')
    print()

