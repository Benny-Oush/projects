def calculate_bill():
    while True:
        while True:
            try:
                bill = float(input("what is the total bill?\n "))
                if bill <= 0:
                    raise ValueError()
                break                
            except ValueError as e:               
                print('error, please enter a valid number\n')
                
        while True:
            try:
                people = int(input("how many people are you?\n "))               
                if people <= 0:
                    print("Error, number of people must be greater than 0\n")                   
                    continue                  
                break
            except ValueError:               
                print('error, please enter a number\n')
                
        while True:
            try:      
                tip = int(input("how many percentage would you like to add (8-12%)?\n"))           
                if tip < 8 or tip > 12:
                    print("please enter a number between 8-12\n")                   
                    continue                   
                total_tip = (tip * bill)/100
                break
            except ValueError:               
                print('error, please enter a number\n')
                
        if bill >= 1500:
            discounted_bill = bill * 0.95
            rounded_bill = round(discounted_bill, 2)
            print("congratulations! you received a 5 percent discount!\n\n"
            f"the amount after discount: {rounded_bill}\n")                    

        total_bill = total_tip + discounted_bill
        total_bill_per_person = total_bill/people
        final = round(total_bill_per_person, 2)                         
                
        print(f"the amount each person should pay is:\n {final}\n")       
        again = input("would you like to calculate another bill? y/n\n ").lower()        
        if again != "y":
            print("have a great day!\n ")
            break
        
calculate_bill()
