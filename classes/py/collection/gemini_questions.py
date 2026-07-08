def string_stat(string):
    noise = ' !#$%^&*()+=?/".,`'
    current = ''
    words = []
    for char in string:
        if char not in noise:
            current += char
            continue
        elif current:
            words.append(current)
            current = ''
    if current:
        words.append(current)

    appear_most = ''
    most_count = 0
    total_len = 0

    for word in words:
        total_len += len(word)

        tmp_most = 0

        for word_2 in words:
            if word == word_2:
                tmp_most += 1

        if tmp_most > most_count:
            appear_most = word
            most_count = tmp_most

        elif tmp_most == most_count:
            if word not in appear_most:
                appear_most += f', {word}'
    return f'Total words: {len(words)}.\nMost common words: \'{appear_most}\'.\nAverage word length: {total_len/len(words)}'

# print(string_stat('My name is Israel, I sit next to Benny, and I write functions')) 

def equation_integrity_check(equation):
    opening = '([{'
    closing = ')]}'

    def check(ind, expected):
        j = ind 
        while j < len(equation):
            if equation[j] == expected:
                return True, j
            if equation[j] in closing:
                return False, j
            if equation[j] in opening:
                result, current = check(j+1, closing[opening.index(equation[j])])
                if not result:
                    return False, current
                j = current
            j += 1
        return False, j

    i = 0
    
    while i < len(equation):
        if equation[i] in opening:
            result, current = check(i+1, closing[opening.index(equation[i])])
            if not result:
                return False, current
            else:
                i = current

        elif equation[i] in closing:
                    return False, i
        i += 1

    return True

# print(equation_integrity_check('((2+3)*5) / (7-2) + [4*{3+2}])'))


def analyze_grades(grades=['']):
    if not grades:
        return

    stats = {
        'name': '',
        'average': 0,
        'highest': 0,
        'lowest': float('inf'),
        'passed': 0,
        'failed': 0
    }

    stats['name'] += grades[0]
    
    for grade in grades[1:]:
        stats['average'] += grade
        if grade > stats['highest']:
            stats['highest'] = grade
        if grade < stats['lowest']:
            stats['lowest'] = grade
        if grade >= 55:
            stats['passed'] += 1
        else:
            stats['failed'] += 1
    stats['average'] /= len(grades)
    return stats

res = analyze_grades(['Benny', 71, 90, 85])
# print(res)

def analyze_numbers(numbers):
    stats = {
        'highest': float('-inf'),
        'lowest': float('inf'),
        'even_count': 0,
        'odd_count': 0, 
        'average': 0
    }

    for num in numbers:
        if num > stats['highest']:
            stats['highest'] = num
        if num < stats['lowest']:
            stats['lowest'] = num
        if num % 2 == 0:
            stats['even_count'] += 1
        else:
            stats['odd_count'] += 1
        stats['average'] += num
        
    stats['average'] /= len(numbers)
    return stats

with open("input.txt", "r") as file:
    contant = file.read().lower()

words = []

current = ''
noise = '!@#$%^&*()_+?~{[]}|.,:;=></\\\n\t- '

for char in contant:
    if char in noise:
        if current:
            words.append(current)
        current = ''
    else:
        current += char

words_dic = {}

for word in words:
    words_dic[word] = words_dic.get(word, 0) + 1


sorted_items = sorted(words_dic.items(), key=lambda x: x[1], reverse=True)
top_five = sorted_items[:5]
# print(top_five)

# print('--- Stasistics ---')
# print(f'The total count of words is {len(words)}')
# print(f'The amount of distinct words is {len(words_dic)}')
# print(f'The most common words:')
# for word in top_five:
#     print(f'"{word[0]}": {word[1]}')
