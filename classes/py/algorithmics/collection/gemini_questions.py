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

# res = analyze_grades(['Benny', 71, 90, 85])
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

# with open("input.txt", "r") as file:
#     contant = file.read().lower()

# words = []

# current = ''
# noise = '!@#$%^&*()_+?~{[]}|.,:;=></\\\n\t- '

# for char in contant:
#     if char in noise:
#         if current:
#             words.append(current)
#         current = ''
#     else:
#         current += char

# words_dic = {}

# for word in words:
#     words_dic[word] = words_dic.get(word, 0) + 1


# sorted_items = sorted(words_dic.items(), key=lambda x: x[1], reverse=True)
# top_five = sorted_items[:5]
# print(top_five)

# print('--- Stasistics ---')
# print(f'The total count of words is {len(words)}')
# print(f'The amount of distinct words is {len(words_dic)}')
# print(f'The most common words:')
# for word in top_five:
#     print(f'"{word[0]}": {word[1]}')

import json
import datetime
import random
def write_log():
    levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
    services = ["auth_service", "payment_gateway", "database_cluster"] 
    info_messages = ["User login successful", "Connection timeout", "Query executed in 45ms"]

    line = {
        'timestep': datetime.datetime.now(),
        'level': random.choice(levels),
        'service': random.choice(services),
        'message': ''
    }

    for _ in range(15):
        line['timestep'] = str(datetime.datetime.now())
        line['level'] = random.choice(levels)
        line['service'] = random.choice(services)
        if line['level'] == 'WARNING':
            line['message'] == 'Missing login info'
        elif line['level'] == 'CRITICAL':
            line['message'] == f'{line['service']} database access dinied'
        elif line['level'] == 'ERROR':
            line['message'] = 'Admin login failed'
        else:
            line['message'] = random.choice(info_messages)

        with open("app.log", "a") as file:
            file.write(f'{json.dumps(line)}\n')

def analyes_log(log_file):
    stats = {
        'services': {
            'auth_service': 0,
            'payment_gateway': 0,
            'database_cluster': 0
        },
        'levels': {
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0,
            'INFO': 0 
        },
        'high_level_messages': []
    }
    
    with open(log_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
                
            try:
                log_data = json.loads(line)
            except json.JSONDecodeError:
                print(f"Warning: Skipped invalid log line -> {line}")
                continue

            service = log_data.get('service')
            if service in stats['services']:
                stats['services'][service] += 1

            level = log_data.get('level')
            if level in stats['levels']:
                stats['levels'][level] += 1
                
                if level in ('ERROR', 'CRITICAL'):
                    stats['high_level_messages'].append({
                        'service': service,
                        'time': log_data.get('timestamp'),
                        'message': log_data.get('message') 
                    })

    most_noisy_service = max(stats['services'], key=stats['services'].get)
    
    return most_noisy_service, stats['levels'], stats['high_level_messages']



class Book:
    def __init__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price
    def apply_discount(self, percentage):
        discount = 1.0 - percentage/100
        self.price *= discount
        print(f'Discount applied! The price of {self.title} is now {self.price:.2f}')


class EBook(Book):
    def __init__(self, title, author, price, file_size):
        super().__init__(title, author, price)
        self.file_size = file_size
    def download(self):
        print(f'Downloading {self.title}\nFile size: {self.file_size}MB')





class SmartDevice:
    def __init__(self, name, is_on=False):
        self.name = name
        self.is_on = is_on

    def status_report(self):
        print(f'The {self.name} is {"on" if self.is_on else "off"}')
    def turn_on(self):
        self.is_on = True
        print(f'The {self.name} is on now')
    def turn_off(self):
        self.is_on = False
        print(f'The {self.name} is off now')


class SmartLight(SmartDevice):
    def __init__(self, name, brightness, is_on=False):
        super().__init__(name, is_on)
        self.brightness = brightness

    def status_report(self):
        super().status_report()
        print(f'Brightness: {self.brightness}')
    
class SmartThermostat(SmartDevice):
    def __init__(self, name, temperature, is_on=False):
        super().__init__(name, is_on)
        self.temperature = temperature
    def status_report(self):
        super().status_report()
        print(f'Temperature: {self.temperature}')

class SmartHome:
    def __init__(self, devices):
        self.devices = devices
    def show_all_statuses(self):
        for device in self.devices:
            device.status_report()
    def active_movie_mode(self):
        for device in self.devices:
            if isinstance(device, SmartThermostat):
                device.turn_on()
                device.temperature = 22
            elif isinstance(device, SmartLight):
                device.turn_on()
                device.brightness = 20


# kitchen_light = SmartLight('kitchen light', 89, True)
# washing_machine = SmartDevice('Washing machine')
# smart_shower = SmartThermostat('Shower', 0)
# home = SmartHome([kitchen_light, washing_machine, smart_shower])


