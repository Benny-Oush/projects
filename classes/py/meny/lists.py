months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

mini = [float('inf')]
maxi = [float('-inf')]

total = 0
all_precipitations = []

for month in months:
    precipitations = int(input(f'Enter the amount of precipitation for {month}: '))
    total += precipitations
    all_precipitations.append(precipitations)

    if precipitations == maxi[-1]:
        maxi.insert(-2, month)
    elif precipitations > maxi[-1]:
        maxi = [month, precipitations]
        
    if precipitations == mini[-1]:
        mini.insert(-2, month)
    elif precipitations < mini[-1]:
        mini = [month, precipitations]


print(all_precipitations)
print()
print(f'The maximum is: {maxi}\n')
print(f'The minimum is: {mini}\n')
print(f'The average precipitation is {total/12}')