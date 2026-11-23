# 1.1
def is_unique(string: str) -> bool:
    for i in range(len(string)):
        for j in range(i + 1, len(string)):
            if string[i] == string[j]:
                return False
    return True

# 1.2
# count = 0
# current_string = input("Enter a string: ")
# while current_string == "" or current_string[0].lower() != "r":
#     # מתייחס למחרוזת ריקה כייחודית
#     if is_unique(current_string):
#         count += 1
#     current_string = input("Enter a string: ")
# print(f"You entered {count} unique strings")

# 2.1
def get_leading_digit(number: int) -> int:
    while number // 10 != 0:
        number //= 10
    return number

# 2.2
def check_for_triple(arr: list[int], init_i: int) -> bool:
    return arr[init_i] == arr[init_i - 1] == arr[init_i - 2]

def count_triples(arr: list[int]) -> int:
    if len(arr) < 3:
        return 0
    leading_digits = []
    for num in arr:
        leading_digits.append(get_leading_digit(num))
    count = 0
    for i in range(2, len(leading_digits)):
        if check_for_triple(leading_digits, i):
            count += 1
    return count

# 3.1
# 3.1.1
# Separate tracking table.
# The function will return False when given [1, -5, 2, -8, 4, 10, -3].

# 3.1.2
# Yes.
# When switching the last two numbers, the function will return True.
# This is going to be the result, since the function is checking whether all of the pairs in the given list have opposite signs or not.

# 3.3
# The claim is true.
# If the list contains the number 0, there must be a pair in the list that does'nt have opposite signs.

# 4
class Flight:
    def __init__(self, flight_num: int, destination: str, passengers: int, capacity: int) -> None:
        self.flight_num = flight_num
        self.destination = destination
        self.passengers = passengers
        self.capacity = capacity

a = [Flight(1, 'TAV', 2, 10), Flight(2, 'TAV', 3, 5), Flight(3, 'TAV', 15, 30), Flight(4, 'NY', 2, 15)]

# 4.1
def count_same_destination(flight_arr: list[Flight], dest: str) -> int:
    count = 0
    for flight in flight_arr:
        if flight.destination == dest:
            count += flight.passengers
    return count

# 4.2
def find_proper_flight(flight_arr: list[Flight], dest: str, num_of_passengers: int):
    for flight in flight_arr:
        if flight.destination == dest and num_of_passengers + flight.passengers <= flight.capacity:
            print(flight.flight_num)

# 5.1
def is_breakthrough(arr: list[int], k: int) -> bool:
    for i in range(k - 1, -1, -1):
        if arr[i] >= arr[k]:
            return False
    return True

# 5.2
def all_breakthroughs(arr: list[int]) -> list[int]:
    all = []
    for i in range(len(arr)):
        if is_breakthrough(arr, i):
            all.append(arr[i])
    return all

# 5.3.1
# Minimal length for n=4 is 1, for example [4, 3, 2, 1]

# 5.3.2
# Maximal length for n=4 is 4, for example [1, 2, 3, 4]

# 6.1
class Donation:
    def __init__(self, donor_name: str, amount: float, donation_type: str) -> None:
        pass

class CharityProject:
    def __init__(self, project_id, location: str, donations: list[Donation]) -> None:
        pass