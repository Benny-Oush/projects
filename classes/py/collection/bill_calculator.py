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



while True:      
    try:             
        again = input("Would you like to calculate a bill? y/n\n").lower()  
        if again == "n":
            print("\nHave a great day!")
            break
        if again != "y" and again != "n":
            raise ValueError()
        if again == "y":
            calculate_bill()
            
    except ValueError:
        print('Please enter y or n')
