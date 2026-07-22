def calculate_bill():
    while True:
        try:
            bill = float(input("\nEnter the total bill: "))
            if bill <= 0:
                raise ValueError()
            break                
        except ValueError as e:               
            print('Error, please enter a valid number\n')
            
    while True:
        try:
            people = int(input("\nEnter the number of people: "))               
            if people <= 0:
                print("Error, number of people must be greater than 0\n")                   
                continue                  
            break
        except ValueError:               
            print('Error, please enter a number\n')
            
    while True:
        try:      
            tip = int(input("\n🤑 How many percentage would you like to add (8-12%)?\n"))           
            if tip < 8 or tip > 12:
                print("Please enter a number between 8-12\n")                   
                continue                   
            total_tip = (tip * bill)/100
            break
        except ValueError:               
            print('Error, please enter a number\n')
            
    if bill >= 1500:
        discounted_bill = bill * 0.95
        rounded_bill = round(discounted_bill, 2)
        print("🎉 Congratulations! you received a 5 percent discount! 🎉\n\n"
        f"The amount after discount: -- {rounded_bill} -- ")  
    else:
        discounted_bill = bill                  

    total_bill = total_tip + discounted_bill
    total_bill_per_person = total_bill/people
    final = round(total_bill_per_person, 2)                         
            
    print(f"\nThe amount each person should pay is:\n\n--{final}--\n")



# while True:      
#     try:             
#         again = input("Would you like to calculate a bill? y/n\n").lower()  
#         if again == "n":
#             print("\nHave a great day!")
#             break
#         if again != "y" and again != "n":
#             raise ValueError()
#         if again == "y":
#             calculate_bill()
            
#     except ValueError:
#         print('Please enter y or n')

def get_valid_input(prompt, expected_type):
    while True:
        if expected_type == 'number':
            try:
                user_input = float(input(prompt))
                return user_input
            except ValueError:
                print('Please enter a number')
        else:
            try:
                user_input = input(prompt)
                if user_input.lower().strip() not in ('y', 'n'):
                    raise ValueError
                return user_input
            except ValueError:
                print('Please enter y or n')
    
def calculate_profits():
    total = 0
    deposit_total = 0
    monthly_deposit = 0

    is_initial_capital = get_valid_input('\nIs there an initial capital (y/n)? ', 'y/n').lower().strip()

    is_monthly_deposit = get_valid_input('\nWill there be monthly deposits (y/n)? ', 'y/n').lower().strip()


    if is_initial_capital == 'y':
        initial_capital = get_valid_input('\nHow much is the initial capital estimated to be? ', 'number')
        total += initial_capital
        deposit_total += initial_capital

    if is_monthly_deposit == 'y':
        monthly_deposit = get_valid_input('\nHow much is a monthly deposit estimated to be? ', 'number')
    else:
        if is_initial_capital == 'n':
            return 'No money to work with'
        
    years_num = int(get_valid_input('\nHow many years is the investment plan planned for (Enter a number of years)? ', 'number'))

    profit_percentage = (get_valid_input('\nWhat is the estimated monthly profit percentage (enter a number)? ', 'number') / 100) + 1
    
    month_num = years_num * 12
    for _ in range(month_num):
        total *= profit_percentage
        total += monthly_deposit
        deposit_total += monthly_deposit

    return f'\nThe total after {years_num} years will be {total:.2f}\n\nThe total deposits are {deposit_total}'

print(calculate_profits())