def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    '''both 1st and 2nd numbers are 1'''
    if n == 1:
        return 1
    if n == 0:
        return 0
    return fibonacci(n - 1) + fibonacci(n - 2)

def pascal_row(n):
    if n == 1: 
        return [1]
    row = pascal_row(n - 1)
    new_row = [1]
    for i in range(1, len(row)):
        new_row.append(row[i] + row[i-1])
    new_row.append(1)
    return new_row

def deep_list_sum(lst):
    total = 0
    for item in lst:
        if type(item) == list:
            total += deep_list_sum(item)
        else:
            total += item
    return total
    