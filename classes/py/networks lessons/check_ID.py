def get_check_digit(ID_number):
    total = 0
    for i in range(8):
        current = int(ID_number[i])
        if i % 2 == 0:
            total += current
        else:
            if (current * 2) > 9:
                tmp = current * 2
                while tmp:
                    total += tmp % 10
                    tmp //= 10
            else:
                total += current * 2 
   
    return (10 - total % 10) % 10

print(get_check_digit('32780398'))