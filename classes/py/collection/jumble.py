words = [
    "PYTHON",
    "CODE",
    "MATRIX",
    "ARRAY",
    "LOOP",
    "STACK",
    "QUEUE",
    "GRAPH"
]

jumble = [
    ['P', 'Y', 'T', 'H', 'O', 'N', 'A', 'B', 'C', 'M'],
    ['X', 'C', 'R', 'S', 'T', 'A', 'D', 'E', 'A', 'F'],
    ['S', 'H', 'O', 'P', 'Q', 'T', 'U', 'T', 'V', 'W'],
    ['T', 'N', 'O', 'D', 'X', 'Y', 'R', 'Z', 'A', 'B'],
    ['A', 'C', 'D', 'E', 'E', 'I', 'F', 'G', 'H', 'C'],
    ['C', 'I', 'J', 'K', 'X', 'M', 'X', 'N', 'O', 'D'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'E'],
    ['K', 'V', 'W', 'X', 'Y', 'Z', 'A', 'B', 'F', 'T'],
    ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'G', 'M', 'N'],
    ['O', 'P', 'Q', 'R', 'S', 'T', 'H', 'V', 'W', 'X']
]


words1 = [
    "PYTHON", "CODE", "MATRIX", "ARRAY", "LOOP", "STACK", "QUEUE",
    "GRAPH", "TREE", "SEARCH", "SORT", "MERGE", "BINARY", "HEAP",
    "HASH", "STRING", "VECTOR", "LIST", "NODE", "EDGE", "DEPTH",
    "WIDTH", "QUEUEING", "RECURSION", "FUNCTION", "OBJECT", "CLASS",
    "MODULE", "PACKAGE", "IMPORT", "BOOLEAN", "INTEGER", "FLOAT",
    "COMPILE", "DEBUG", "MEMORY", "POINTER", "BUFFER", "THREAD",
    "PROCESS", "NETWORK", "SERVER", "CLIENT", "SOCKET", "KERNEL",
    "LINUX", "WINDOWS", "SCRIPT", "VARIABLE", "CONSTANT"
]

jumble1 = [
    ['P','Y','T','H','O','N','A','Q','W','E','R','T','Y','U','I','O','P','L','K','J'],
    ['Z','C','A','S','D','F','G','H','J','K','L','M','N','B','V','C','X','Z','Q','W'],
    ['S','X','O','P','L','A','N','E','T','R','E','E','Q','M','H','A','S','H','T','Y'],
    ['T','Q','R','D','C','A','T','B','V','N','M','R','E','C','U','R','S','I','O','N'],
    ['A','W','E','R','E','C','N','M','L','K','J','H','G','F','D','S','A','Q','P','O'],
    ['C','T','Y','U','I','X','X','V','B','N','M','L','K','J','H','G','F','D','S','A'],
    ['K','A','S','D','F','G','H','J','K','L','P','O','I','U','Y','T','R','E','W','Q'],
    ['Q','W','E','R','T','Y','U','I','O','A','S','D','F','G','H','J','K','L','Z','X'],
    ['E','R','T','Y','U','I','O','P','T','D','F','G','H','J','K','L','Z','X','C','V'],
    ['R','T','Y','U','I','A','P','M','G','H','J','K','L','Z','X','C','V','B','N','M'],
    ['T','Y','U','Q','R','X','A','V','B','N','M','L','I','S','T','Q','W','E','R','T'],
    ['Y','U','I','O','M','X','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F'],
    ['B','I','N','A','R','Y','L','O','O','P','G','R','A','P','H','N','O','D','E','S'],
    ['L','I','N','U','X','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G'],
    ['M','E','M','O','R','Y','H','J','K','L','Z','X','C','V','B','N','M','Q','W','E'],
    ['S','E','A','R','C','H','P','R','O','C','E','S','S','T','H','R','E','A','D','S'],
    ['C','L','A','S','S','F','U','N','C','T','I','O','N','M','O','D','U','L','E','Q'],
    ['S','O','C','K','E','T','W','I','N','D','O','W','S','I','M','P','O','R','T','Z'],
    ['D','E','B','U','G','B','U','F','F','E','R','S','E','R','V','E','R','C','L','I'],
    ['C','L','I','E','N','T','K','E','R','N','E','L','V','A','R','I','A','B','L','E']
]




def find_word(jumble, word, start_i, start_j, reverse=False):
    word_len = len(word)
    if reverse:
        word = word[::-1]

    # rows
    if (len(jumble[start_i]) - start_j) >= word_len:
        found = True
        for k in range(start_j, start_j + word_len):
            if word[k-start_j] != jumble[start_i][k]:
                found = False
                break
        if found:
            return True
        
    # columns
    if (len(jumble) - start_i) >= word_len:
        found = True
        for k in range(start_i, start_i + word_len):
            if word[k-start_i] != jumble[k][start_j]:
                found = False
                break
        if found:
            return True
        
    # diagonals
    if (len(jumble) - start_i) >= word_len and (len(jumble[start_i]) - start_j) >= word_len:
        j = start_j
        found = True
        for k in range(start_i, start_i + word_len):
            if word[k-start_i] != jumble[k][j]:
                found = False
                break
            j += 1
        if found:
            return True
        
    if (len(jumble) - start_i) >= word_len and (start_j + 1) >= word_len:
        j = start_j
        found = True
        for k in range(start_i, start_i + word_len):
            if word[k-start_i] != jumble[k][j]:
                found = False
                break
            j -= 1
        if found:
            return True
        
    return False


def check_jumble(jumble, words):
    found = []
    for word in words:
        in_jumble = False

        for i in range(len(jumble)):
            for j in range(len(jumble[i])):
                if jumble[i][j] == word[0]:
                    if find_word(jumble, word, i, j):
                        in_jumble = True
                        found.append(word)
                        break

                if jumble[i][j] == word[-1]:
                    if find_word(jumble, word, i, j, reverse=True):
                        in_jumble = True
                        found.append(word)
                        break
            if in_jumble:
                break

    return found

print(check_jumble(jumble1, words1))



def check_direction(jumble, word, i, j, di, dj):
    for k in range(2, len(word)):
        i, j = i + di, j + dj
        if not (0 <= i < len(jumble)) or not (0 <= j < len(jumble[i])):
            return False
        if word[k] != jumble[i][j]:
            return False
    return True

def check_word(jumble, word, i, j):
    if len(word) < 2:
        return False
    for di in range(-1, 2):
        for dj in range(-1, 2):
            if di == 0 and dj == 0:
                continue 
            second_i, second_j = i + di, j + dj
            if not (0 <= second_i < len(jumble)) or not (0 <= second_j < len(jumble[second_i])):
                continue
            if jumble[second_i][second_j] == word[1]:
                if check_direction(jumble, word, second_i, second_j, di, dj):
                    return True
    return False


def check_jumble_2(jumble, words):
    f = []
    for word in words:
        for i in range(len(jumble)):
            found = False
            for j in range(len(jumble[i])):
                if jumble[i][j] == word[0]:
                    found = check_word(jumble, word, i, j)
                    if found:
                        f.append(word)
                        break
            if found:
                break
    return f


# print(check_jumble_2(jumble1, words1))



def check_layer_number(mat, layer_number):
    mat_len = len(mat) if len(mat) > len(mat[0]) else len(mat[0])
    inner_layer = mat_len//2 if mat_len % 2 == 0 else (mat_len + 1)//2
    if (0 <= layer_number < inner_layer) and layer_number != inner_layer:
        return True
    return False

def extract_layer(mat, layer_number):
    n = layer_number
    l = len(mat)
    k = len(mat[0])
    layer = []
    for i in range(n, k - n):
        layer.append(mat[n][i])

    for i in range(n + 1, l - n):
        layer.append(mat[i][k - n - 1])
    
    for i in range(k - n - 2, n, -1):
        layer.append(mat[l - n - 1][i])
    
    for i in range(l - n - 1, n, -1):
        layer.append(mat[i][n])
    
    return layer


def move(lst, steps):
    return lst[-steps:] + lst[:-steps]

def replace_layer(mat, layer_number, lst):
    n = layer_number
    l = len(mat)
    k = len(mat[0])
    ind = 0
    for i in range(n, k - n):
        mat[n][i] = lst[ind]
        ind += 1
    for i in range(n + 1, l - n):
        mat[i][k - n - 1] = lst[ind]
        ind += 1
    for i in range(k - n - 2, n, -1):
        mat[l - n - 1][i] = lst[ind]
        ind += 1
    for i in range(l - n - 1, n, -1):
        mat[i][n] = lst[ind]
        ind += 1
    
    return mat


def change_matrix(mat, layer_number, steps):
    if not check_layer_number(mat, layer_number):
        return False
    layer = extract_layer(mat, layer_number)
    new_layer = move(layer, steps)
    return replace_layer(mat, layer_number, new_layer)


mat = [
    [1, 2, 3, 4, 5, 6],
    [3, 4, 5, 6, 7, 8],
    [4, 5, 6, 7, 7, 8],
    [5, 4, 3, 2, 5, 9]
]

# res = change_matrix(mat, 1, 3)
# if res:
#     for row in res:
#         for elm in row:
#             print(f'{elm:2}', end=' ')
#         print()
# else:
#     print('Invalid layer number')

