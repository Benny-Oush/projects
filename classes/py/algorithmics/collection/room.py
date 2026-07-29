def calculate_profits(income, expenses):
    differences = []
    all_sum = 0
    
    for i in range(len(income)):
        all_sum += income[i] - expenses[i]

    average = all_sum/len(income)

    for i in range(len(income)):
        net = income[i] - expenses[i]
        differences.append(net - average)

    return differences

# 2 for loops

def get_balance_ind(arr):
    if len(arr) < 3:
        return -1

    left_side = arr[0]
    right_side = 0

    for num in arr[2:]:
        right_side += num
    
    for i in range(1, len(arr)-1):
        if right_side == left_side:
            return i
        else:
            right_side -= arr[i+1]
            left_side += arr[i]

    return -1

# 2 for loops

def is_prime(num):
    if num < 2:
        return False
    
    i = 2
    while i*i <= num:
        if num % i == 0:
            return False
        
    return True

def sum_super_prime(arr):
    total = 0

    for num in arr:
        if num % 2 == 0 and num != 2:
            continue

        if is_prime(num):
            digit_count = 0
            digit_sum = 0 
            current = num

            while current:
                digit_count += 1
                digit_sum += current % 10
                current //= 10

            if is_prime(digit_sum) and is_prime(digit_count):
                total += num

    return total

# 2 for loops, 1 while and 1 nested

def seconds_difference(arr):
    greatest = float('-inf')
    second_greatest = float('-inf')

    smallest = float('inf')
    second_smallest = float('inf')

    for num in arr:
        if num > greatest:
            greatest, second_greatest = num, greatest
        elif num > second_greatest and num != greatest:
            second_greatest = num

        if num < smallest:
            smallest, second_smallest = num, smallest
        elif num < second_smallest and num != smallest:
            second_smallest = num

    return second_greatest - second_smallest

# 1 for loop

