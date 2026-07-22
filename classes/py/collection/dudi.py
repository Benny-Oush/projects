def matrix_sum(matrix):
    total = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            total += matrix[i][j]
    return total

def check_if_symmetrical(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] != matrix[j][i]:
                return False
    return True

def order_diagonal(matrix):
    for i in range(len(matrix)):
        mini = float('inf')
        ind = 0
        for j in range(len(matrix[i])):
            if matrix[i][j] < mini:
                mini = matrix[i][j]
                ind = j
        matrix[i][i], matrix[i][ind] = matrix[i][ind], matrix[i][i]
    return matrix

def check_for_same_lines(mat1, mat2):
    same_lst = []
    for i in range(len(mat1)):
        for j in range(len(mat2)):
            same = True
            for k in range(len(mat2[j])):
                if mat2[k][j] != mat1[i][k]:
                    same = False
                    break
            if same:
                same_lst.append((i, j))
    return same_lst


def cells_sum(matrix):
    new_mat = [[0 for j in range(len(matrix[0]))] for i in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    new_i, new_j = di + i, dj + j
                    if not (0 <= new_i < len(matrix)) or not (0 <= new_j < len(matrix[new_i])):
                        continue
                    new_mat[i][j] += matrix[new_i][new_j]
    return new_mat
                    
def is_dirty(matrix):
    values = []
    for i in range(len(matrix) - 1):
        for j in range(len(matrix[i]) - 1):
            num = matrix[i][j]
            if num == matrix[i][j + 1]:
                if num == matrix[i+1][j] == matrix[i+1][j+1]:
                    if num not in values:
                        values.append(num) 
                        if len(values) > 3:
                            return True
    return False

def count_value(mat, column, value):
    count = 0
    for i in range(len(mat)):
        if mat[i][column] == value:
            count += 1
    return count


def is_pair(mat, arr):
    if len(arr) != len(mat[0]):
        return False
    for i in range(len(mat[0])):
        if count_value(mat, i, arr[i]) != i:
            return False
    return True


def check_for_sad_num(mat):
    maxi = None

    for i in range(1, len(mat) - 1):
        for j in range(1, len(mat[i]) - 1):
            val = mat[i][j]
            if (10 <= val < 100):
                is_sad = True
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        if di == 0 and dj == 0:
                            continue
                        if mat[i + di][j + dj] == val:
                            is_sad = False
                            break
                    if not is_sad:
                        break
                if is_sad:
                    if maxi is None or val > maxi:
                        maxi  = val
    if maxi is not None:
        print(maxi)
    else:
        print('There is no sad two digit number')




mat = [
    [5,  4,  1,  0,   0, 3],
    [1, 10,  7,  1, 123, 3],
    [6,  1,  7,  0,   0, 2],
    [1, 10, 21,  5,   5, 2],
    [1, 10,  1, 10,  10, 1]
]

arr = [5, 12, 4, 15]

mat2 = [
    [4, 9, 3, 2],
    [7, 2, 6, 0],
    [1, 5, 5, 3],
    [2, 0, 6, 0]
]
check_for_sad_num(mat)

