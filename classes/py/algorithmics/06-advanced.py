# 1
def get_sums(arr):
    e_sum = 0
    o_sum = 0
    for i in range(len(arr)):
        if i % 2 == 0:
            e_sum += arr[i]
        else:  
            o_sum += arr[i]

    result = e_sum - o_sum

    return result if result > 0 else -result


# 2
def gcd(arr):
    arr = sorted(arr)
    for i in range(arr[0], 0, -1):
        is_div = True
        div = i
        for num in arr:
            if num % i != 0:
                is_div = False
                break
        if is_div:
            return div
    return 1


# 2
def gcd2(arr):
    div = arr[0]
    for num in arr[1:]:
        while num:
            div, num = num, div % num
        if div == 1:
            return 1
    return div


# 3
def get_prime_sum(arr):
    total = 0

    for num in arr:
        if num < 2:
            continue

        is_prime = True

        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break

        if is_prime:
            total += num

    return total


# 4
def get_largest_digit_sum(arr):
    largest = 0
    count = 0
    for num in arr:
        current = num
        tmp = 0
        while num > 0:
            tmp += 1
            num //= 10
        if tmp > count:
            count = tmp
            largest = current
            
    return largest


# 5
def every_has_7(arr):
    for num in arr:
        has_7 = False
        while num > 0:
            if num % 10 == 7:
                has_7 = True
            num //= 10
        if not has_7:
            return False
    return True

6
def has_most_divisors(arr):
    count = 0
    has_most = 0
    for num in arr:
        tmp = 0
        for i in range(1, int(num**0.5) + 1):
            if num % i == 0:
                tmp += 1
                if i != num // i:
                    tmp += 1
        if tmp > count:
            count = tmp
            has_most = num
    return has_most, count


7
def longest_sequence(arr):
    sequence = []
    tmp = [arr[0]]
    for i in range(1, len(arr)):
        if arr[i]-1 == arr[i-1]:
            tmp.append(arr[i])
        else:
            if len(tmp) > len(sequence):
                sequence = tmp[:]
            tmp = [arr[i]]
    if len(tmp) > len(sequence):
        sequence = tmp[:]
    return sequence

8
def sum_of_even(arr):
    sum = 0
    for i in range(0, len(arr), 2):
        if arr[i] % 2 == 0:
            sum += arr[i]
    return sum

9
def get_divisible_by_3_average(arr):
    sum = 0
    count = 0 
    for num in arr:
        if num % 3 == 0:
            sum += num
            count += 1
    return sum / count

10
def find_largest_difference(arr):
    difference = 0
    num1 = 0
    num2 = 0
    for i in range(1, len(arr)):
        if arr[i] - arr[i-1] > difference:
            difference = arr[i] - arr[i-1]
            num1 = arr[i-1]
            num2 = arr[i]
    return (f"[{num1}, {num2}] - difference: {difference}")


11
def is_symmetric(arr):
    return arr == arr[::-1]

12
def find_even_digit_sum(arr):
    for num in arr:
        sum = 0
        current = num
        while num > 0:
            sum += num % 10
            num //= 10
        if sum % 2 == 0:
            return current

13
def count_divisible_by_digit_sum(arr):
    count = 0
    divable = []
    for num in arr:
        sum = 0
        current = num
        while num > 0:
            sum += num % 10
            num //= 10
        if current % sum == 0:
            count += 1
            divable.append(current)
    return (f"{count} -> {divable}")



# 15
def get_sum_of_coprime(arr):
    sum = 0
    for i in range(1, len(arr)):
        is_foreign = True
        for j in range(2, arr[i]+1):
            if arr[0] % j == 0 and arr[i] % j == 0:
                is_foreign = False
                break
        if is_foreign:
            sum += arr[i]
    return sum


# 16
def find_largest_product(arr):
    largest_ind = 0
    tmp_sum = 1
    largest_sum = float('-inf')
    for i in range(len(arr)):
        num = arr[i] if arr[i] > 0 else -arr[i]
        digit = 0
        while num:
            digit = num % 10
            num //= 10
            tmp_sum *= digit
        if tmp_sum > largest_sum:
            largest_sum = tmp_sum
            largest_ind = i
        tmp_sum = 1
    return largest_ind



# 17
def longest_sequence(arr):
    count = 1
    max_num = arr[0] % 10

    for num in arr:
        prev = num % 10
        tmp_max = prev
        tmp_count = 1

        num //= 10
        while num:
            digit = num % 10
            if digit == prev:
                tmp_count += 1
                tmp_max = digit
            else:
                if tmp_count > count:
                    count = tmp_count
                    max_num = tmp_max
                tmp_count = 1
            prev = digit
            num //= 10

        if tmp_count > count:
            count = tmp_count
            max_num = tmp_max
            
    return f'The number {max_num} appears {count} times'


# 18
def all_has_gcd(arr):
    for i in range(len(arr)-1):
        has_gcd = False
        for j in range(arr[i+1], 1, -1):
            if arr[i] % j == 0 and arr[i+1] % j == 0:
                has_gcd = True
                break
        if not has_gcd:
            return f'Pair: [{arr[i]}, {arr[i+1]}] has no gcd greater than 1'
    return 'All pairs have a gcd greater than 1'


# 19
def appears_most(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    max_num = arr[0]
    max_count = 1
    tmp_count = 1

    for i in range(1, len(arr)):
        if arr[i] == arr[i-1]:
            tmp_count += 1
            if tmp_count > max_count:
                max_count = tmp_count
                max_num = arr[i]
        else:
            tmp_count = 1
    return max_num


# 20
def largest_prime(arr):
    largest = float('-inf')
    for num in arr:
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime and num > largest:
            largest = num
    return largest


# 21
def most_vowels(arr):
    vowels = 'aeiou'
    count = 0
    most_vowels = []

    for word in arr:
        tmp_count = 0

        for word_letter in word:
            if word_letter in vowels:
                tmp_count += 1

        if tmp_count > count:
            count = tmp_count
            most_vowels = [word]

        elif tmp_count == count:
            most_vowels.append(word)


    if len(most_vowels) == 1:
        return most_vowels[0]
    else:
        return ', '.join(f'{w} ({count})' for w in most_vowels)



# 22
def all_uppercased(txt):
    upp_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    all_are_upper = True if txt[0] in upp_alphabet else False

    for i in range(len(txt)):
        if txt[i] == ' ':
            if txt[i+1] not in upp_alphabet:
                all_are_upper = False

    return True if all_are_upper else False


# 23
def longest_word2(txt):
    longest = ''
    current_word = ''
    nums = '1234567890'
    
    for letter in txt:
        if letter == ' ':
            has_no_num = True

            for num in nums:
                if num in current_word:
                    has_no_num = False

            if has_no_num:
                if len(current_word) > len(longest):
                    longest = current_word
                current_word = ''
        else:
            current_word += letter

    has_no_num = True
    
    for num in nums:
        if num in current_word:
            has_no_num = False

    if has_no_num and len(current_word) > len(longest):
        longest = current_word
            
    return longest


# 24
def prime_length(txt):
    current_word = ''
    prime_words_count = 0

    for letter in txt:
        if letter == ' ':
            n = len(current_word)

            if n < 2:
                continue

            is_prime = True

            for i in range(2, n):
                if n % i == 0:
                    is_prime = False

            if is_prime:
                prime_words_count += 1

            current_word = ''

        else:
            current_word += letter

    n = len(current_word)
    is_prime = True

    for i in range(2, n):
        if n % i == 0:
            is_prime = False

    if is_prime:
        prime_words_count += 1

    return prime_words_count



# 25
def most_distinct_letters(txt):
    current_word = ''
    most_distint = ''
    distinct_count = 0

    for letter in txt:
        if letter == ' ':
            distinct = ''

            for char in current_word:
                char = char.lower()

                if char not in distinct:
                    distinct += char

            if len(distinct) > distinct_count:
                distinct_count = len(distinct)
                most_distint = current_word

            current_word = ''

        else:
            current_word += letter

    distinct = ''

    for char in current_word:
        char = char.lower()

        if char not in distinct:
            distinct += char

    if len(distinct) > distinct_count:
        distinct_count = len(distinct)
        most_distint = current_word  

    return most_distint



# 26
def shortest_word(txt):
    words = []
    
    current_word = ''
    for letter in txt:
        if letter == ' ':
            words.append(current_word.lower())
            current_word = ''

        else:
            current_word += letter

    words.append(current_word.lower())

    shortest = ''
    shortest_length = float('inf')

    for word in words:
        word_count = 0

        if len(word) < shortest_length:
            for word2 in words:
                if word2 == word:
                    word_count += 1

                if word_count > 1:
                    shortest = word
                    shortest_length = len(shortest)
                    break
    return shortest


# 27
def has_vowel(txt):
    current_word = ''
    vowels = 'aeiouy'

    for letter in txt:
        letter = letter.lower()

        if letter == ' ':
            word_has_vowel = False

            for char in vowels:
                if char in current_word:
                    word_has_vowel = True
                    break

            if not word_has_vowel:
                return False
            
            current_word = ''

        else:
            current_word += letter

    for char in vowels:
        if char in current_word:
            return True
        
    return False
                

# 28
def longest_palindrome(txt):
    current_word = ''
    longest = ''
    longest_count = float('-inf')

    for letter in txt:
        letter = letter.lower()

        if letter == ' ':
            if current_word == current_word[::-1]:
                if len(current_word) > longest_count:
                    longest_count = len(current_word)
                    longest = current_word

            current_word = ''

        else:
            current_word += letter
    
    if current_word == current_word[::-1]:
        if len(current_word) > longest_count:
            longest = current_word

    return longest


# 29
def count_pairs(txt):
    count = 0
    gap = 1
    txt = txt.lower()

    for i in range(1, len(txt)):
        if txt[i] == ' ':
            gap = 2
            continue

        if txt[i] == txt[i-gap]:
            count += 1

        gap = 1

    return count



# 30
def letter_appears_most(txt):
    txt_list = []

    for letter in txt:
        if letter != ' ':
            txt_list.append(letter.lower())

    for i in range(len(txt_list)):
        swapped = False

        for j in range(len(txt_list) - i -1):
            if txt_list[j] > txt_list[j + 1]:
                txt_list[j], txt_list[j + 1] = txt_list[j + 1], txt_list[j]
                swapped = True

        if not swapped:
            break
    
    most = txt_list[0]
    count = 1
    tmp_count = 1

    for i in range(1, len(txt_list)):
        if txt_list[i] == txt_list[i-1]:
            tmp_count += 1

            if tmp_count > count:
                count = tmp_count
                most = txt_list[i]

        else:
            tmp_count = 1

    return most



# 31
def longest_even(arr):
    longest = ''
    longest_count = float('-inf')

    for string in arr:
        if len(string) > longest_count and len(string) % 2 == 0:
            longest = string
            longest_count = len(string)

    return longest


# 32
def count_lowercased(arr):
    count = 0

    for string in arr:
        is_upper = False

        for letter in string:
            if not letter.islower():
                is_upper = True
                break
        if not is_upper:
            count += 1
    
    return count
        


# 33
def has_most_digits(arr):
    has_most = ''
    most_count = 0
    nums = '1234567890' 

    for string in arr:
        tmp_count = 0

        for letter in string:
            if letter in nums:
                tmp_count += 1
        if tmp_count > most_count:
            has_most = string
            most_count = tmp_count

    return has_most



# 34
def all_have_uppercased(arr):
    for string in arr:
        has_upper = False

        for letter in string:
            if letter.isupper():
                has_upper = True
        
        if not has_upper:
            return False
        
    return has_upper



# 35
def count_vowels(arr):
    count = 0
    vowels = 'aeiouy'

    for string in arr:
        string = string.lower()

        for letter in string:
            if letter in vowels:
                count += 1

    return count



def most_common_first_letter(arr):
    prefix = []
    for string in arr:
        prefix.append(string[0].lower())

    for i in range(len(prefix)):
        for j in range(len(prefix) - i - 1):
            if prefix[j] > prefix[j+1]:
                prefix[j], prefix[j+1] = prefix[j+1], prefix[j]

    longest_sequence = 1
    tmp_longest = 1
    most_common = prefix[0]

    for i in range(1, len(prefix)):
        if prefix[i] == prefix[i-1]:
            tmp_longest += 1

            if tmp_longest > longest_sequence:
                longest_sequence = tmp_longest
                most_common = prefix[i]
    
        else:
            tmp_longest = 1

    return most_common



# 36

def most_common_prefix(arr):
    count = 0
    most_common = ''
    
    for word in arr:
        for word2 in arr:
            end = len(word) 

            for i in range(len(word)):
                if i >= len(word2) or word[i] != word2[i]:
                    end = i
                    break

            if end == 0:
                continue

            tmp_count = 0
            for word3 in arr:
                if word[:end] == word3[:end]:
                    tmp_count += 1

            if tmp_count > count:
                count = tmp_count
                most_common = word[:end]
                
    return most_common
                    

# 37
def greatest_difference(arr):
    shortest = arr[0]
    longest = arr[0]

    for string in arr:
        length = len(string)

        if length > len(longest):
            longest = string

        if length < len(shortest):
            shortest = string
    return f'[{shortest}, {longest}]'



# 38
def count_palindromes(arr):
    count = 0
    for string in arr:
        if string.lower() == string[::-1].lower():
            count += 1

    return count



# 39
def less_distinct(arr):
    has_fewest = arr[0]
    fewest_distinct = float('inf')

    for string in arr:
        string = string.lower()
        distinct = ''

        for letter in string:
            if letter not in distinct:
                distinct += letter

        if len(distinct) < fewest_distinct:
            has_fewest = string
            fewest_distinct = len(distinct)

    return has_fewest



# 40
def all_have_different_length(arr):
    lengths = []

    for string in arr:
        lengths.append(len(string))
    
    for length in lengths:
        count = 0

        for length2 in lengths:
            if length == length2:
                count += 1

        if count > 1:
            return False
        
    return True



