# Solve each question and find out what's your answer's complexity

# 1. Write a function that accepts a square matrix of numbers and returns the sum of the four corner elements.

def corner_sum(mat):
    total = 0
    for i in range(0, -2, -1):
        for j in range(0, -2, -1):
            total += mat[i][j]
    return total

# ⬆️ O(1)

# 2. Write a function that accepts a matrix of numbers and returns True if every row is sorted in ascending order.

def is_mat_ascending(mat):
    for i in range(1, len(mat)):
        is_ascending = True
        for j in range(1, len(mat[i])):
            if mat[i][j] < mat[i][j-1]:
                is_ascending = False
                break
        if not is_ascending:
            return False
    return True

# ⬆️ O(n*m)

# 3. Write a function that accepts a matrix of numbers and returns the index of the row whose sum is the largest.

def largest_row_sum(mat):
    total = 0
    ind = 0
    for i in range(len(mat)):
        tmp_total = 0
        for item in mat[i]:
            tmp_total += item
        if tmp_total > total:
            total = tmp_total
            ind = i
    return ind

# ⬆️ O(n*m)

# 4. Write a function that accepts a matrix of numbers and returns True if every row is a cyclic shift of the first row.
# For example, compare each row to the first row:

mat = [
    [1, 2, 3, 4],
    [3, 4, 1, 2],
    [4, 1, 2, 3],
    [2, 3, 4, 1]
]

def has_cyclic_shift(mat):
    for i in range(1, len(mat)):
        if len(mat[i]) != len(mat[0]):
            return False
        if mat[i] == mat[0]:
            return False
        is_shifted = False
        for j in range(1, len(mat[0])):
            if mat[i][-j:] + mat[i][:-j] == mat[0]:
                is_shifted = True
                break
        if not is_shifted:
            return False
    return True

# ⬆️ O(n*m^2)

# 5. Write a function that accepts a square matrix of numbers and returns True if every row and every column contains exactly the same set of numbers (possibly in a different order).

def my_sorting(lst):
    for i in range(len(lst)):
        for j in range(i, 0, -1):
            if lst[j] < lst[j-1]:
                lst[j], lst[j-1] = lst[j-1], lst[j]
            else:
                break
    return lst


def check_for_set(mat):
    main_set = my_sorting(mat[0][:])
    for i in range(len(mat)):
        row_set = mat[i][:]
        column_set = []
        for j in range(len(mat)):
            column_set.append(mat[j][i])
        if not my_sorting(row_set) == my_sorting(column_set) == main_set:
            return False
    return True

mat = [
    [1, 2, 3],
    [2, 3, 1],
    [3, 1, 2]
]

# ⬆️ O(n^2)

# 6. Write a function that accepts a matrix of numbers and returns the area (number of cells) of the largest rectangle consisting only even numbers.

mat = [
    [2, 2, 2],
    [1, 2, 2],
    [1, 2, 2] 
]

def largest_even_rectangle(mat):
    if not mat or not mat[0]: return 0

    best = 0
    rows = len(mat)
    columns = len(mat[0])

    for i in range(rows):
        for j in range(columns):
            if mat[i][j] % 2 != 0: continue

            max_width = columns - j

            for row in range(i, rows):
                current_width = 0  

                for column in range(j, j + max_width):
                    if mat[row][column] % 2 != 0:
                        break
                    current_width += 1

                if current_width == 0: break

                max_width = current_width
                height = row - i + 1
                area = max_width * height

                if area > best:
                    best = area
    return best

# ⬆️ O(n^(2) * m^(2))

# 7. Write a function that accepts a square matrix of numbers and returns the column whose elements have the largest greatest common divisor. The function returns the column as a list.

def my_gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def find_lst_gcd(lst):
    if not lst: return 0
    gcd = lst[0]
    for num in lst[1:]:
        if gcd == 1: return 1
        gcd = my_gcd(gcd, num)
    return gcd

def find_matrix_column_gcd(mat):
    if not mat or not mat[0]: return []
    greatest = -1
    column = []
    for i in range(len(mat)):
        c = [mat[j][i] for j in range(len(mat))]
        gcd = find_lst_gcd(c)
        if gcd > greatest:
            greatest = gcd
            column = c
    return column

# ⬆️ O(n^2) 

# 8. Write a function that accepts a matrix of numbers and a number n. The function returns a new matrix, same as the original - after filtering out every row and column which contains the number n.

def clean_matrix(mat, n): 
    rows_to_remove = []
    columns_to_remove = []
    clean_mat = []
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == n:
                rows_to_remove.append(i)
                columns_to_remove.append(j)
    for i in range(len(mat)):
        if i in rows_to_remove:
            continue
        new_row = []
        for j in range(len(mat[0])):
            if j not in columns_to_remove:
                new_row.append(mat[i][j])
        clean_mat.append(new_row)
    return clean_mat

# ⬆️ O(n*m)

# For example, if the function gets this matrix:

mat = [
    [1, 7, 6, 4],
    [8, 3, 0, 2],
    [5, 9, 1, 3],
    [8, 1, 2, 4]
 ]

# And if the second parameter is the number 8, then the function should filter the first column, the second row and the last row. It will return:

# 7 6 4
# 9 1 3

