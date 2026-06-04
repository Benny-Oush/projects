use std::{io::stdin, result};

fn get_number() -> i32 {
    let mut input = String::new();
    println!("Please enter a number:");
    stdin().read_line(&mut input).expect("Failed to read");
    let number = input.trim().parse().expect("Failed to convert");
    return number;
}

pub struct BankAccount {
    pub owner: String,
    pub balance: f64
}

impl BankAccount {
    pub fn new(owner: String, balance: f64) -> Self {
        Self {owner, balance}
    }

    pub fn deposit(&mut self, amount: i32) {
        let amount = amount as f64;
        if amount <= 0.0 {
            println!("Amount must be larger than 0");
            self.balance += get_number() as f64;
        } else {
            self.balance += amount;
        }
        println!("The deposit was successful! The current balance in your account is {}", self.balance);
    }

    pub fn withdraw(&mut self, amount: i32) {
        let amount = amount as f64;
        if self.balance - amount >= 0.0 {
            self.balance -= amount;
        } else {
            println!("There is not enough money left in your balance.\n
    Please enter a smaller amount");
            let mut new_amount = get_number() as f64;
            while self.balance - new_amount < 0.0 {
                println!("There is not enough money left in your balance.\n
    Please enter a smaller amount");
                new_amount = get_number() as f64;
            }
            self.balance = self.balance - new_amount;
        }
        println!("The withdraw was successful! \n
    The current balance in your account is {}", self.balance);
    }

    pub fn can_withdraw(&self, amount: i32) -> bool {
        if self.balance - amount as f64 >= 0.0 {
            return true
        } else {
            return false
        }        
    }

    pub fn print_details(&self) {
        println!("{}", self.owner);
        println!("{}", self.balance);
    }

    pub fn  transfer(&mut self, other: &mut BankAccount, amount: i32) {
        let amount = amount as f64;
        if self.balance - amount >= 0.0 {
            self.balance -= amount;
            other.balance += amount;
        } else {
            println!("There is not enough money left in your balance.\n
    Please enter a smaller amount");
            let mut new_amount = get_number() as f64;
            while self.balance - new_amount < 0.0 {
                println!("There is not enough money left in your balance.\n
    Please enter a smaller amount");
                new_amount = get_number() as f64;
            }
            self.balance -= new_amount;
            other.balance += new_amount;        
        }
        println!("The withdraw was successful! \n
    The current balance in your account is {}", self.balance);
        }
}


