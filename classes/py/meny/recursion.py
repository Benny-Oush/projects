from time import sleep

def star(n):
    if n > 0:
        star(n - 1)
        sleep(0.015)
        print(n, end=" ", flush=True)
        star(n - 1)

def revarse(n):
    if n:
        print(n % 10, end="")
        revarse(n // 10)

def count_down(n):
    if n:
        print(n, flush=True)
        sleep(1)
        count_down(n - 1)
    else:
        print("Done!")

def sum_digits(n, total=0):
    if n:
        return sum_digits(n // 10, total + n % 10)
    return total

def sum_list(arr, total=0):
    if not arr:
        return total
    return sum_list(arr[:-1], total + arr[-1])


def fibonacci(n):
    if n <= 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)