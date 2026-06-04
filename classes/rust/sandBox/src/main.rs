use std::{io::stdin, result};
use rand::Rng;
mod person;
use person::Person;
mod product;
use product::Product;
mod bank_account;
use bank_account::BankAccount;

fn input(value_type: &str) -> String {
    let mut input = String::new();
    println!("Please enter a {value_type}:");
    stdin().read_line(&mut input).expect("Failed to read");
    return input;
}

fn get_number() -> i32 {
    let mut input = String::new();
    println!("Please enter a number:");
    stdin().read_line(&mut input).expect("Failed to read");
    let number = input.trim().parse().expect("Failed to convert");
    return number;
}

fn get_average(arr:&[i32]) -> f32 {
    let mut sum = 0;
    for num in arr {
        sum += num;
    }
    let average = sum as f32 / arr.len() as f32;
    return average;
}

fn get_lowest(arr:&[i32]) -> i32  {
    let mut lowest = 99999999;
    
    for &num in arr {
        if num < lowest {
            lowest = num;
        }
    }
    return lowest;
}

fn get_smiley(num: i32) {
    if num == 1{
        println!("(-:")
    } else if num == 2 {
        println!(")-:")
    } else if num == 3 {
        println!("/-:")
    } else if num == 4 {
        println!("(-;")
    } else {
        println!(")-;")
    }
}

fn main() {

    // let mut rang = rand::thread_rng();
    // let num = rang.gen_range(1..=5);
    
    //    let mut numbers: Vec<i32> = Vec::new();
    //     for i in 0..5 {
    //         numbers.push(get_number());
    //     }

    //     let result = get_lowest(&numbers);
    //     println!("The lowest number you entered is {result}");
    // let new_person = Person {
    //     name: String::from("John"), 
    //     age: 20, 
    //     email: String::from("john@example.com")};
    
    // let mut product1 = Product {
    //     name: String::from("papers"),
    //     price: 20.60,
    //     quantity: 6
    // };

    // let mut product2 = Product {
    //     name: String::from("pencils"),
    //     price: 30.80,
    //     quantity: 9
    // };

    // product1.change_quantity(9);
    // println!("{}", product1.quantity);
    
    // println!("{}", product2.name);

    // println!("{}", product1.total_value());

    // let mut new_account = BankAccount {
    //     owner: String::from("Benny"),
    //     balance: 25000.0
    // };

    // println!("{}", new_account.can_withdraw(30000));
    // new_account.withdraw(30000);

    // new_account.print_details();

    // let mut new_account2 = BankAccount {
    //     owner: String::from("Bunam"),
    //     balance: 15000.0
    // };    

    // new_account.transfer(&mut new_account2, 60000);

}