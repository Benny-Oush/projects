def list_convolution(arr, mask):
    if len(mask) > len(arr):
        arr, mask = mask, arr

    result = []
    for i in range(len(arr) - len(mask) + 1):
        total = 0
        for j in range(len(mask)):
            total += arr[i + j] * mask[j]
        result.append(total)

    return result

l1 = [5, 7, 2, 8, 4, 3]
l2 = [2, 4, 5, 4]

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

arr = [1, 2, 3, 4, 5]

def is_matrix(lst):
    length = 0

    if type(lst[0]) == list:
        length = len(lst[0])
    else:
        return False

    for elm in lst:
        if type(elm) == list:
            if len(elm) != length:
                return False
        else:
            return False
    return True
        

def multiply_matrix(lst, n):
    if not is_matrix(lst):
        return 'The given list is not a matrix'
        
    new_matrix = []

    for i in range(len(lst)):
        new_matrix.append([])
        for j in range(len(lst[i])):
            new_matrix[i].append(lst[i][j]*n)

    return new_matrix

# res = multiply_matrix(matrix, 3)


# for row in res:
#     for item in row:
#         print(f'{item:3}', end=' ')
#     print()


def routate_matrix(lst):
    if not is_matrix(lst):
        return 'The given list is not a matrix'
    
    new_matrix = []

    for i in range(len(lst[0])):
        new_matrix.append([])

        for j in range(len(lst) -1, -1, -1):
            new_matrix[i].append(lst[j][i])

    return new_matrix


matrix_2 = [
    [1, 2, 3, 9],
    [7, 8, 1, 6],
    [6, 0, 9, 5],
    [4, 2, 5, 3]
]

mask = [
    [2, 4],
    [7, 3]
]

# res = routate_matrix(matrix_2)

# for row in res:
#     for item in row:
#         print(f'{item:3}', end=' ')
#     print()



def matrix_convolution(matrix, mask):
    result = []
    for i in range(len(matrix) - len(mask) + 1): 
        result.append([])
        for j in range(len(matrix[0]) - len(mask[0]) + 1):
            total = 0
            for k in range(len(mask)): 
                for l in range(len(mask[0])):
                    total += matrix[i + k][j + l] * mask[k][l]
            result[i].append(total)
    return result

matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]

mask = [
    [6, 1],
    [4, 3]
]

# res = matrix_convolution(matrix, mask)

# for row in res:
#     for item in row:
#         print(f'{item:3}', end=' ')
#     print()


def matrix_average(matrix):
    result = []
    for i in range(len(matrix)):
        result.append([])
        for j in range(len(matrix[0])):
            count = 0
            total = 0
            if j - 1 >= 0:
                total += matrix[i][j - 1]
                count += 1
            if j + 1 < len(matrix[0]):
                total += matrix[i][j + 1]
                count += 1
            if i - 1 >= 0:
                total += matrix[i - 1][j]
                count += 1
            if i + 1 < len(matrix):
                total += matrix[i + 1][j]
                count += 1
            
            if total / count == matrix[i][j]:
                result[i].append(1)
            else:
                result[i].append(0)
    return result


matrix = [
    [3, 2, 1],
    [5, 4, 2],
    [8, 7, 1]
]
# res = matrix_average(matrix)

# for row in res:
#     for item in row:
#         print(f'{item:3}', end=' ')
#     print()


def check_sudoku(sudoku):
    for i in range(9):
        seen = []
        seen2 =  []
        for j in range(9):
            num = sudoku[i][j]
            num2 = sudoku[j][i]
            if num in seen or num2 in seen2 or num < 1 or num > 9:
                return False
            seen.append(num)
            seen2.append(num2)
    
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            seen = []
            for i2 in range(3):
                for j2 in range(3):
                    num = sudoku[i+i2][j+j2]
                    if num in seen:
                        return False
                    seen.append(num)
    return True

sudoku = [

    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9]
]

# print(check_sudoku(sudoku))


def check_sequence(value, longest, tmp_longest):
    if value == 0:
        tmp_longest += 1
        if tmp_longest > longest:
            longest = tmp_longest
    else:
        tmp_longest = 0
    
    return longest, tmp_longest

def matrix_sequence(matrix):
    longest = 0

    if not matrix or not matrix[0]:
        return 'Matrix not valid'

    for line in matrix:
        if len(line) != len(matrix[0]):
            return 'Matrix not valid'

    if len(matrix) == len(matrix[0]):
        tmp_longest = 0
        for i in range(len(matrix)):
            value = matrix[i][i]
            longest, tmp_longest = check_sequence(value, longest, tmp_longest)

        tmp_longest = 0
        for i in range(len(matrix)):
            value = matrix[i][len(matrix)-1-i]
            longest, tmp_longest = check_sequence(value, longest, tmp_longest)


    for line in range(len(matrix)):
        tmp_longest = 0
        for cell in range(len(matrix[line])):
            value = matrix[line][cell]
            longest, tmp_longest = check_sequence(value, longest, tmp_longest)

 
    for cell in range(len(matrix[0])):
        tmp_longest = 0
        for column in range(len(matrix)):
            value = matrix[column][cell]
            longest, tmp_longest = check_sequence(value, longest, tmp_longest)


    return longest



matrix = [
    [0, 2, 0, 0, 0, 5],
    [0, 3, 0, 5, 0, 0],
    [0, 0, 0, 3, 4, 5],
    [5, 2, 3, 6, 4, 0],
    [0, 0, 0, 2, 0, 0],
    [0, 0, 5, 0, 0, 0]
]

# print(matrix_sequence(matrix))