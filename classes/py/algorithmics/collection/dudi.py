def matrix_sum(matrix):
    total = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            total += matrix[i][j]
    return total


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


def check_if_symmetrical(matrix):
    for i in range(len(matrix) - 1):
        for j in range(i + 1, len(matrix[i])):
            if matrix[i][j] != matrix[j][i]:
                return False
    return True

# mat2 = [
#     [3, 4, 5, 9],
#     [4, 5, 0, 8],
#     [5, 0, 1, 2],
#     [9, 8, 2, 7]
# ]
# mat = [
#     [5,  4,  1,  0,   0, 3],
#     [1, 10,  7,  1, 123, 3],
#     [6,  1,  7,  0,   0, 2],
#     [1, 10, 21,  5,   5, 2],
#     [1, 10,  1, 10,  10, 1]
# ]

# arr = [5, 12, 4, 15]


def has_digit(num, digit):
    while num:
        if num % 10 == digit:
            return True
        num //= 10
    return False

def is_arranged(mat):
    row_len = len(mat)
    for i in range(len(mat)):
        if len(mat[i]) != row_len:
            return False
        for j in range(row_len):
            if mat[i][j] < 0:
                return False
            if not has_digit(mat[i][j], j):
                return False 
    return True

# mat = [
#     [10, 312, 1220, 31],
#     [605, 1, 1342, 13],
#     [70, 15 ,21, 305],
#     [1003, 601, 200, 203]
# ]


def is_flower(mat, row, column):
    if row == 0 or row == len(mat) - 1: 
        return False
    if column == 0 or column == len(mat[0]) - 1:
        return False
    a = mat[row - 1][column - 1]
    b = mat[row - 1][column + 1]
    c = mat[row + 1][column - 1]
    d = mat[row + 1][column + 1]

    total = a + b + c + d
    return total == mat[row][column] 


def find_all_flowers(mat):
    row_len = len(mat[0])
    flowers = []
    for i in range(1, len(mat) - 1):
        if len(mat[i]) != row_len:
            return []
        for j in range(1, row_len - 1):
            if is_flower(mat, i, j):
                flowers.append(mat[i][j])
    return flowers if flowers else None


mat = [
    [3, 9, 1, 9, 9, 9],
    [9, 6, 9, 9, 9, 9],
    [0, 9, 2, 9, 8, 9],
    [9, 9, 9, 15, 9, 9],
    [9, 9, 7, 9, -2, 9]
]


class Subject:
    def __init__(self, subject: str, assignments_num: int, passing_grade: int, credits_num: int):
        self.subject = subject
        self.assignments_num = assignments_num
        self.passing_grade = passing_grade
        self.credits_num = credits_num

    def get_points(self, submitted: int, grade: int):
        if submitted >= (self.assignments_num/2) and grade >= self.passing_grade:
            return self.credits_num
        return 0
        

def result(subjects_arr):
    total_points = 0
    for subject in subjects_arr:
        total_points += subject.get_points(int(input(f'Enter the number of {subject.subject} submitted assignments: ')), int(input(f'Enter the {subject.subject} grade: ')))
    print(total_points)

class Gift:
    def __init__(self, code: int, price: float, type: str):
        self.code = code
        self.price = price
        self.type = type
    def set_type(self, new_type):
        if new_type.upper() in ['M', 'F', 'U', 'K']:
            self.type = new_type
    def is_for_man(self):
        if self.type in ['M', 'U']:
            return True
        return False

def check_for_3_different_man_gifts(gifts_arr: list, total: float):
    gifts_for_man = [gift for gift in gifts_arr if gift.is_for_man()]
    found_match = False
    n = len(gifts_for_man)

    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if gifts_for_man[i].price + gifts_for_man[j].price + gifts_for_man[k].price == total:
                    found_match = True
                    print(gifts_for_man[i].code, gifts_for_man[j].code, gifts_for_man[k].code)
    if not found_match:
        print('No match')


def exchange(number: int):
    prev = (number % 10) % 2
    number //= 10
    while number:
        if (number % 10) % 2 == prev:
            return False   
        prev = (number % 10) % 2         
        number //= 10
    return True

def lowest_exchanging_number_sum(arr: list):
    lowest_ind = -1
    lowest = float('inf')
    for i in range(len(arr)):
        if exchange(arr[i]):
            num = arr[i]
            total = 0
            while num:
                total += num % 10
                num //= 10
            if total < lowest:
                lowest = total
                lowest_ind = i
    return lowest_ind

def intersect(arr_a, arr_b):
    slicing = []
    a_counter = [0] * 100
    b_counter = [0] * 100
    for i in range(len(arr_a)):
        if 10 <= arr_a[i] < 100: 
            a_counter[arr_a[i]] = 1
    for i in range(len(arr_b)):
        if 10 <= arr_b[i] < 100: 
            b_counter[arr_b[i]] = 1
    for i in range(10, 100):
        if a_counter[i] == b_counter[i] == 1:
            slicing.append(i)
    return slicing

def are_strangers(arr_a, arr_b):
    return intersect(arr_a, arr_b) == []



class Time:
    def __init__(self, hour: int, minute: int):
        pass # ...

    def is_before(self, other: 'Time') -> bool:
        pass # ...

    def add_five_minutes(self) -> 'Time':
        pass # ...

class Message:
    def __init__(self, sender: str, subject: int, content: str, receiving_time: Time, has_attachment: bool):
        pass
    def get_sender(self):
        pass # ...
    def get_subject(self):
        pass # ...
    def get_content(self):
        pass # ...
    def get_receiving_time(self):
        pass # ...
    def get_has_attachment(self):
        pass # ...

    def reply(self, text: str) -> 'Message':
        return Message('support@uni.ac.il', -1 * self.get_subject(), self.get_content() + ' ' + text, self.get_receiving_time().add_five_minutes(), False)

class Mailbox:
    def __init__(self, num: int):
        self.max_capacity = num
        self.inbox = []
        self.no_of_mes = 0
    def how_many_between_times(self, first: Time, second: Time) -> int:
        count = 0
        for message in self.inbox:
            time = message.get_receiving_time()
            if first.is_before(time) and time.is_before(second):
                count += 1
        return count
    
    def most_popular_subject(self) -> int:
        subject_counter = [0] * 12
        for message in self.inbox:
            subject = message.get_subject()
            if subject > 0:
                subject_counter[subject - 1] += 1
        most_popular = 0
        most_popular_count = 0
        for i in range(len(subject_counter)):
            if subject_counter[i] > most_popular_count:
                most_popular_count = subject_counter[i]
                most_popular = i + 1
        return most_popular


def digits_sum(num) -> int:
    if num < 0:
        num = -num
    total = 0
    while num:
        total += num % 10
        num //= 10
    return total

def has_most_brothers_in_other_arr(arr1, arr2) -> int:
    has_most = 0
    most_brothers_count = 0
    for i in range(len(arr1)):
        tmp_count = 0
        total = digits_sum(arr1[i])
        for other_num in arr2:
            if total == digits_sum(other_num):
                tmp_count += 1
        if tmp_count > most_brothers_count:
            most_brothers_count = tmp_count
            has_most = i
    return has_most

a = [89, 552, 9]
b = [-156, 39, 78, 9]

# print(has_most_brothers_in_other_arr(a, b))


def get_peak(arr):
    '''Returns the peak - if there is only one peak'''
    peak = arr[0]
    ind = 1
    for i in range(1, len(arr)):
        if arr[i] > arr[i-1]:
            peak = arr[i]
            ind += 1
        else:
            break
    for i in range(ind, len(arr)):
        if arr[i] > arr[i-1]:
            return False
    return peak

# print(get_peak([3, 2, 1]))


def is_valid(string):
    upper_count = 0
    lower_count = 0
    for char in string:
        if ord('a') <= ord(char) <= ord('z'):
            lower_count += 1
        elif ord('A') <= ord(char) <= ord('Z'):
            upper_count += 1
        else:
            return False
    return upper_count > lower_count

# has_an_A_edge = 0
# string = input('Enter a string: ')
# while not is_valid(string):
#     if string[0] == 'A' or string[-1] == 'A':
#         has_an_A_edge += 1
#     string = input('Enter another string: ')

# print(has_an_A_edge)

class Truck:
    def __init__(self, truck_id: str, driver_name: str, max_weight=4000, is_refrigeration=False, is_free=True):
        self.truck_id = truck_id
        self.driver_name = driver_name
        self.max_weight = max_weight
        self.is_refrigeration = is_refrigeration
        self.is_free = is_free
    def get_truck_id(self):
        return self.truck_id
    def get_driver_name(self):
        return self.driver_name
    def get_max_weight(self):
        return self.max_weight
    def get_is_refrigeration(self):
        return self.is_refrigeration
    def get_is_free(self):
        return self.is_free


def print_refrigeration_heavy_trucks(trucks_arr: list[Truck]):
    for truck in trucks_arr:
        if truck.get_is_refrigeration() and truck.get_max_weight() >= 10000:
            print(truck.get_truck_id())
def find_free_heavy_refrigeration_truck(trucks_arr: list[Truck]):
    heaviest = trucks_arr[0]
    for truck in trucks_arr:
        if truck.get_is_free() and truck.get_is_refrigeration():
            if truck.get_max_weight() > heaviest.get_max_weight():
                heaviest = truck
    return heaviest.get_driver_name() if heaviest.is_refrigeration and heaviest.get_is_free() else 'No name'

# trucks = [
#     Truck('1', 'Dudi', is_refrigeration=True),
#     Truck('2', 'Benny', 10000, is_refrigeration=True),
#     Truck('3', 'Mendi'),
#     Truck('4', 'Moshe', 7000),
#     Truck('5', 'Bunam', 12000, is_refrigeration=True),
#     Truck('6', 'Dor'),
#     Truck('7', 'yossi', 11000, is_refrigeration=True)
# ]

# print_refrigeration_heavy_trucks(trucks)
# print(find_free_heavy_refrigeration_truck(trucks))

def sum_of_divisors(num):
    total = 0
    for i in range(1, num):
        if num % i == 0:
            total += i
    return total

def check_number_type(num):
    total = sum_of_divisors(num)
    if total == num:
        return 'P'
    if total < num:
        return 'D'
    if total > num:
        return 'A'

def all_numbers_by_type(limit: int, num_type: str):
    found = []
    for i in range(2, limit):
        found_type = check_number_type(i)
        if found_type == num_type:
            found.append(i)
    return found

def is_k_rolling(str1: str, str2: str, k: int) -> bool:
    return str1[k:] + str1[:k] == str2

def find_rolling_k(str1: str, str2: str) -> int:
    if len(str1) != len(str2):
        return -1
    for i in range(len(str1)):
        if is_k_rolling(str1, str2, i): return i
    return -1

def are_all_rotating(arr: list[str], s: str) -> bool:
    for string in arr:
        if find_rolling_k(string, s) == -1:
            return False
    return True