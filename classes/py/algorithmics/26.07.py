def check_if_symmetrical(matrix):
    for i in range(len(matrix) - 1):
        for j in range(i + 1, len(matrix[i])):
            if matrix[i][j] != matrix[j][i]:
                return False
    return True

# ⬆️ O(n^2)

mat2 = [
    [3, 4, 5, 9],
    [4, 5, 0, 8],
    [5, 0, 1, 2],
    [9, 8, 2, 7]
]

# print(check_if_symmetrical(mat2))

def check_if_has_sequence(string):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(string)):
        ind = alphabet.index(string[i])
        if string[i:i+4] == alphabet[ind:ind+4]:
            return True
    return False

# ⬆️ O(n)

# print(check_if_has_sequence('gyhuijolacdjnmwyzol'))

def matrix_product(matrix):
    if len(matrix) != 3:
        return 0
    else:
        for i in range(len(matrix)):
            if len(matrix[i]) != 3:
                return 0
    bigest = 0
    for i in range(3):
        product1 = 1
        product2 = 1
        for j in range(3):
            product1 *= matrix[i][j]
            product2 *= matrix[j][i]
        if product1 > bigest: bigest = product1
        if product2 > bigest: bigest = product2
    return bigest

# ⬆️ O(1)

def count_same_substrings(string):
    len_str = len(string)
    for i in range(1, (len_str//2) + 1):
        sub = len_str//i
        if string[:i] * sub == string:
            return sub
    return 0
        
# ⬆️ O(n^2)

# print(count_same_substrings('abcabc'))

mat3 = [
    [1, 2, 3],
    [5, 6, 7],
    [8, 6, 9]
]


def sum_exists(lst, n):
    if n == 0:
        return True
    for i in range(len(lst)):
        if lst[i] > n:
            continue
        if sum_exists(lst[i+1:], n-lst[i]):
            return True
    return False

print(sum_exists([9, 1, 3, 5, 4], 11))

