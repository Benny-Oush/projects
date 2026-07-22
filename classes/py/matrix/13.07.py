def check_for_mixing(matrix_1, matrix_2):
    if len(matrix_1) != len(matrix_2):
        return False
    
    checked_count = 0
    for i in range(len(matrix_1)):
        row = matrix_1[i]
        if len(row) != len(matrix_2[i]):
            return False
        for row2 in matrix_2:
            if row[0] not in row2:
                continue
            for item in row:
                if item not in row2:
                    continue
        checked_count += 1
    if checked_count == len(matrix_1):
        return True
    return False

mat_1 = [
    [1, 2, 3],
    [4, 1, 6]
]

mat_2 = [
    [1, 4, 6],
    [3, 2, 1]
]

# print(check_for_mixing(mat_1, mat_2))

def is_magical_matrix(matrix):
    if matrix:
        for row in matrix:
            if len(row) != len(matrix):
                return 0
    else:
        return 0
    
    n = len(matrix)
    seen = []
    magical_sum = 0

    for num in matrix[0]:
        magical_sum += num

    diagonal1_sum = 0
    diagonal2_sum = 0
    
    for i in range(n):
        row_sum = 0
        column_sum = 0
        diagonal1_sum += matrix[i][i]
        diagonal2_sum += matrix[i][n - 1 - i]
    
        for j in range(n):
            if matrix[i][j] > n**2 or matrix[i][j] < 1:
                return 0
            if matrix[i][j] not in seen:
                row_sum += matrix[i][j]
                seen.append(matrix[i][j])
            else:
                return 0
            column_sum += matrix[j][i]
    
        if row_sum != magical_sum or column_sum != magical_sum:
            return 0
    
    if diagonal1_sum != magical_sum or diagonal2_sum != magical_sum:
        return 0
    
    return magical_sum

matrix = [
    [2, 9, 4],
    [7, 5, 3],
    [6, 1, 8]
]

matrix_2 = [
    [47, 58, 69, 80,  1, 12, 23, 34, 45],
    [57, 68, 79,  9, 11, 22, 33, 44, 46],
    [67, 78,  8, 10, 21, 32, 43, 54, 56],
    [77,  7, 18, 20, 31, 42, 53, 55, 66],
    [ 6, 17, 19, 30, 41, 52, 63, 65, 76],
    [16, 27, 29, 40, 51, 62, 64, 75,  5],
    [26, 28, 39, 50, 61, 72, 74,  4, 15],
    [36, 38, 49, 60, 71, 73,  3, 14, 25],
    [37, 48, 59, 70, 81,  2, 13, 24, 35]
]

# print(is_magical_matrix(matrix))

def find_prefix(lst):
    if len(lst) < 2:
        return 0, ''
    
    end = len(lst[0])

    for word in lst[1:]:
        while lst[0][:end] != word[:end]:
            if end == 0:
                return 0, ''
            end -= 1
    return end, lst[0][:end] 

# print(find_prefix(["flower", "flow", "flight"]))

def print_calendar(first_day, month, year):
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 100 != 0 and year % 4 == 0) or year % 400 == 0:
        month_days[1] = 29

    calendar = []
    calendar.append([])

    for i in range(month_days[month-2] - (first_day-1), month_days[month-2]):
        calendar[0].append(i+1)
    ind = 0

    for i in range(month_days[month-1]):
        if len(calendar[ind]) < 7:
            calendar[ind].append(i+1)
        else:
            calendar.append([])
            ind += 1
            calendar[ind].append(i+1)
    for i in range(7 - len(calendar[-1])):
        calendar[-1].append(i+1)

    print('+-----+-----+-----+-----+-----+-----+-----+')
    print('| SUN | MON | TUE | WED | THU | FRI | SAT |')
    for week in calendar:
        print('+-----+-----+-----+-----+-----+-----+-----+')
        print('|', end='')
        for day in week:
            print(f'{day:4} ', end='|')
        print()
    print('+-----+-----+-----+-----+-----+-----+-----+')
    
print_calendar(2, 4, 1933)

