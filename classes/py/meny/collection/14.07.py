def is_balanced():
    for _ in range(80):
        inp = int(input('Enter a number: '))
        if inp < 0:
            num = -num
        num = inp
        low = 0
        high = 0
        while num > 0:
            digit = num % 10
            num //= 10
            if digit <= 4:
                low += digit
            else:
                high += digit
        if low == high:
            print(inp)

is_balanced()