def bubble_sorting(lst):
    for i in range(len(lst)):
        swapped = False
        for j in range(len(lst) - 1 - i):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
                swapped = True
        if not swapped:
            return lst
    return lst

def insertion_sorting(lst):
    for i in range(1, len(lst)):
        if lst[i] < lst[i-1]:
            lst[i], lst[i-1] = lst[i-1], lst[i]
            for j in range(i - 1, 0, -1):
                if lst[j] < lst[j-1]:
                    lst[j], lst[j-1] = lst[j-1], lst[j]
                else:
                    break
    return lst

