def get_sums(arr):
    e_sum = 0
    o_sum = 0
    for i in range(0, len(arr)):
        if i % 2 == 0:
            e_sum += arr[i]
        else:  
            o_sum += arr[i]
    return e_sum, o_sum


# def gcd(arr):
#     arr = sorted(arr)
#     for i in range(arr[0], 0, -1):
#         is_div = True
#         div = i
#         for num in arr:
#             if num % i != 0:
#                 is_div = False
#                 break
#         if is_div:
#             return div
#     return 1


# def gcd2(arr):
#     div = arr[0]
#     for num in arr[1:]:
#         while num:
#             div, num = num, div % num
#         if div == 1:
#             return 1
#     return div


# def get_prime_sum(arr):
#     sum = 0
#     for num in arr:
#         is_prime = True
#         for i in range(2, num-1):
#             if num % i == 0:
#                 is_prime = False
#                 break
#         if is_prime:
#             sum += num
#     return sum

# def get_largest_digit_sum(arr):
#     largest = 0
#     count = 0
#     for num in arr:
#         current = num
#         tmp = 0
#         while num > 0:
#             tmp += 1
#             num //= 10
#         if tmp > count:
#             count = tmp
#             largest = current
            
#     return largest


# def every_has_7(arr):
#     for num in arr:
#         has_7 = False
#         while num > 0:
#             if num % 10 == 7:
#                 has_7 = True
#             num //= 10
#         if not has_7:
#             return False
#     return True

# def has_most_divisors(arr):
#     count = 0
#     has_most = 0
#     for num in arr:
#         tmp = 0
#         for i in range(1, int(num**0.5) + 1):
#             if num % i == 0:
#                 tmp += 1
#                 if i != num // i:
#                     tmp += 1
#         if tmp > count:
#             count = tmp
#             has_most = num
#     return has_most, count


# def longest_sequence(arr):
#     sequence = []
#     tmp = [arr[0]]
#     for i in range(1, len(arr)):
#         if arr[i]-1 == arr[i-1]:
#             tmp.append(arr[i])
#         else:
#             if len(tmp) > len(sequence):
#                 sequence = tmp[:]
#             tmp = [arr[i]]
#     if len(tmp) > len(sequence):
#         sequence = tmp[:]
#     return sequence

# def sum_of_even(arr):
#     sum = 0
#     for i in range(0, len(arr), 2):
#         if arr[i] % 2 == 0:
#             sum += arr[i]
#     return sum

# def get_divisible_by_3_average(arr):
#     sum = 0
#     count = 0 
#     for num in arr:
#         if num % 3 == 0:
#             sum += num
#             count += 1
#     return sum / count

# def find_largest_difference(arr):
#     difference = 0
#     num1 = 0
#     num2 = 0
#     for i in range(1, len(arr)):
#         if arr[i] - arr[i-1] > difference:
#             difference = arr[i] - arr[i-1]
#             num1 = arr[i-1]
#             num2 = arr[i]
#     return (f"[{num1}, {num2}] - difference: {difference}")


# def is_symmetric(arr):
#     return arr == arr[::-1]

# def find_even_digit_sum(arr):
#     for num in arr:
#         sum = 0
#         current = num
#         while num > 0:
#             sum += num % 10
#             num //= 10
#         if sum % 2 == 0:
#             return current

# def count_divisible_by_digit_sum(arr):
#     count = 0
#     divable = []
#     for num in arr:
#         sum = 0
#         current = num
#         while num > 0:
#             sum += num % 10
#             num //= 10
#         if current % sum == 0:
#             count += 1
#             divable.append(current)
#     return (f"{count} -> {divable}")


def are(num1, num2):
    are_for = True
    for i in range(num1):
        if num1 % i == 0 and num2 % i == 0:
            are_for = False
    return are_for

def get_sum_of_coprime(arr):
    sum = 0
    for i in range(1, len(arr)):
        is_foreign = True
        for j in range(2, arr[i]):
            if arr[0] % j == 0 and arr[i] % j == 0:
                is_foreign = False
                break
        if is_foreign:
            sum += arr[i]
    return sum


def find_largest_product(arr):
    largest_ind = 0
    tmp_sum = 1
    largest_sum = float('-inf')
    for i in range(len(arr)):
        num = arr[i] if arr[i] > 0 else -arr[i]
        digit = 0
        while num:
            digit = num % 10
            num //= 10
            tmp_sum *= digit
        if tmp_sum > largest_sum:
            largest_sum = tmp_sum
            largest_ind = i
        tmp_sum = 1
    return largest_ind



def longest_sequence(arr):
    count = 1
    max_num = arr[0] % 10

    for num in arr:
        prev = num % 10
        tmp_max = prev
        tmp_count = 1

        num //= 10
        while num:
            digit = num % 10
            if digit == prev:
                tmp_count += 1
                tmp_max = digit
            else:
                if tmp_count > count:
                    count = tmp_count
                    max_num = tmp_max
                tmp_count = 1
            prev = digit
            num //= 10

        if tmp_count > count:
            count = tmp_count
            max_num = tmp_max
            
    return f'The number {max_num} appears {count} times'


def all_has_gcd(arr):
    for i in range(len(arr)-1):
        has_gcd = False
        for j in range(arr[i+1], 1, -1):
            if arr[i] % j == 0 and arr[i+1] % j == 0:
                has_gcd = True
                break
        if not has_gcd:
            return f'Pair: [{arr[i]}, {arr[i+1]}] has no gcd greater than 1'
    return 'All pairs have a gcd greater than 1'


def appears_most(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    max_num = arr[0]
    max_count = 1
    tmp_count = 1

    for i in range(1, len(arr)):
        if arr[i] == arr[i-1]:
            tmp_count += 1
            if tmp_count > max_count:
                max_count = tmp_count
                max_num = arr[i]
        else:
            tmp_count = 1
    return max_num


def largest_prime(arr):
    largest = float('-inf')
    for num in arr:
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime and num > largest:
            largest = num
    return largest



# arr = [234, 12, 77, 833, 14988889, 959, 75, 77, 79, 80, 81, 60]
arr = [1, 2, 3, 4, 5]
# arr = [6, 12, 18, 35, 70]
# arr = [1, 2, 3, 3, 4, 3, 2, 6, 5, 4, 7, 9]

# print(longest_sequence(arr))


