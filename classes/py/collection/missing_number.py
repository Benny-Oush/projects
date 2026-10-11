def find_majority_element(arr):
    if not arr:
        return
    candidate = arr[0]
    count = 1
    for i in range(1, len(arr)):
        num = arr[i]
        if num == candidate:
            count += 1
        else:
            count -= 1
        if count == 0:
            candidate = num
            count = 1
    return candidate

arr = [2, 3, 3, 2, 3, 3]
print(find_majority_element(arr))