def get_largest_idx_under_idx_n(arr: list[int], n: int) -> int:
    if not arr:
        return
    largest_idx = 0
    arr_len = len(arr)
    for i in range(1, n):
        if i == arr_len:
            break
        if arr[i] > arr[largest_idx]:
            largest_idx = i
    return largest_idx

def swap(idx_1: int, idx_2: int, arr: list[int]):
    if not 0 <= idx_1 < len(arr) or not 0 <= idx_2 < len(arr) or idx_1 == idx_2:
        return False
    arr[idx_1], arr[idx_2] = arr[idx_2], arr[idx_1]
    print(arr) 
    return True

def selection_sorting(arr):
    for i in range(len(arr), 1, -1):
        swap(get_largest_idx_under_idx_n(arr, i), i - 1, arr)

def expressive_selection_sorting(arr):
    length = len(arr)
    for i in range(len(arr) - 1):
        max_ind = 0
        for j in range(1, length - i):
            if arr[j] > arr[max_ind]:
                max_ind = j
        arr[length - 1 - i], arr[max_ind] = arr[max_ind], arr[length - 1 -i]
    print(arr)

def bubble_sorting(arr):
    length = len(arr)
    for i in range(1, length):
        swapped = False
        for j in range(1, length - i):
            if arr[j - 1] > arr[j]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                swapped = True
        if not swapped:
            break
    print(arr)

def search(arr, val):
    for i in range(len(arr)):
        if arr[i] == val:
            return i
    return

def bin_search(arr: list[int], val: int) -> int:
    if not arr:
        return
    left = 0
    right = len(arr) - 1
    mid = 0
    while left <= right:
        mid = (right + left) // 2
        if arr[mid] > val:
            right = mid - 1
        elif arr[mid] < val:
            left = mid + 1
        else:
            return mid
    return -1

def merge_lists(arr_1, arr_2, arr_3):
    arr_3.clear()
    arr_1_idx = arr_2_idx = 0

    while arr_1_idx < len(arr_1) and arr_2_idx < len(arr_2):
        if arr_1[arr_1_idx] < arr_2[arr_2_idx]:
            arr_3.append(arr_1[arr_1_idx])
            arr_1_idx += 1
        else:
            arr_3.append(arr_2[arr_2_idx])
            arr_2_idx += 1
    
    if arr_1_idx < len(arr_1):
        arr_3 += arr_1[arr_1_idx:]
    else:
        arr_3 += arr_2[arr_2_idx:]
