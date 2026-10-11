string = input('Enter a string: ')
string = 'YFD UG HG  GYI HB U U  UJH JH HUJHJKH H'
count = 0

for i in range(1, len(string)):
    if string[i] == ' ' and string[i-1] != ' ':
        count += 1

if len(string) > 0 and string[-1] != ' ':
    count += 1 
print(f'You entered {count} words')


# # sol 1

# string = input('Enter a string: ')
# count = 0

# for i in range(256):
#     for j in range(len(string)):
#         if chr(i) == string[j]:
#             count += 1
#             break
    

# print(f'There are {count} distinct characters in the string you entered')



# # sol 2

# string = input('Enter a String: ')
# count = 0

# for i in range(len(string)):
#     is_distinct = True
#     for j in range(i + 1, len(string)):
#         if string[i] == string[j]:
#             is_distinct = False
#             break
#     if is_distinct:
#         count +=1

# print(f'There are {count} distinct characters in the string you entered')



