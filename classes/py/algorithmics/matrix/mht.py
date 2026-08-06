def is_perm(num1, num2):
    num1_counters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    num2_counters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if num1 == num2:
        return False
    if num1 > num2:
        num1, num2 = num2, num1
    while num1:
        num1_counters[(num1 % 10)] += 1
        num2_counters[(num2 % 10)] += 1
        num1 //= 10
        num2 //= 10

    return False if num2 else num1_counters == num2_counters


def is_super_perm(arr):
    for lst in arr:
        is_super = False
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                if is_perm(lst[i], lst[j]):
                    is_super = True
                    break
            if is_super:
                break
                
        if not is_super:
            return False
    return True

arr1 = [
    [12, 55, 21],         
    [123, 321, 999, 10],  
    [7, 89, 98]
]

arr2 = [
    [14, 41],            
    [11, 22, 33], 
    [105, 501, 20]    
]

arr3 = [
    [123, 123, 45],        
    [56, 65]               
]






            
