use std::{io::stdin, result};

fn get_number() -> i32 {
    let mut input = String::new();
    println!("Please enter a number:");
    stdin().read_line(&mut input).expect("Failed to read");
    let number = input.trim().parse().expect("Failed to convert");
    return number;
}
pub struct Product {
    pub name: String, 
    pub price: f64,
    pub quantity: i32
}

impl Product {
    pub fn new(name: String, price: f64, quantity: i32) -> Self {
        Self { name, price, quantity}
    }
    pub fn change_quantity(&mut self, new_quantity: i32) {
        if new_quantity <= 0 {
            println!("Quantity must be larger than 0");
            self.quantity = get_number();
        } else {
            self.quantity = new_quantity;
        }
    }
    pub fn total_value(&self) -> f64 {
        return self.price * self.quantity as f64;
    }
}