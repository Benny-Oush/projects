use std::{io, result, vec};
fn input(value_type: &str) -> String {
    let mut input= String::new();
    println!("Enter a {value_type}: ");
    io::stdin().read_line(&mut input).expect("Failed to read");
    input
}

fn to_number(value: &str) -> i32 {
    value.trim().parse().expect("Invalid number")    
}

// fn main() {
//     let num = rand::random_range(1..=10);
//     println!("Random number: {num}");
// }















// fn average(num1: i32, num2: i32, num3: i32) -> f32{
//     let sum: f32 = (num1+num2+num3) as f32;
//     sum/3.0
// }

// fn max(num1: i32, num2: i32, num3: i32) -> i32 {
//     let mut max_num: i32 = num1;
//     if num2 > max_num {
//         max_num = num2;
//     }
//     if num3 > max_num {
//         max_num = num3;
//     }
//     max_num
// }

// fn main() {

//     let mut input = String::new();

//     println!("Enter a number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num1: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter second number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num2: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter third number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num3: i32 = input.trim().parse().expect("Invalid number");


//     let result = max(num1, num2, num3);
//     println!("The biggest number is {result}")
// }


// fn max(num1: i32, num2: i32, num3: i32){
//     let mut max_num: i32 = num1;
//     if num2 > max_num {
//         max_num = num2;
//     }
//     if num3 > max_num {
//         max_num = num3;
//     }
//     println!("The biggest number is {max_num}");

// }

// fn main() {

//     let mut input = String::new();

//     println!("Enter a number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num1: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter second number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num2: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter third number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num3: i32 = input.trim().parse().expect("Invalid number");


//     max(num1, num2, num3);
// }


// fn max(num1: i32, num2: i32, num3: i32){
//     let mut sum: i32 = num1 + num2 + num3;

//     println!("The sum is {sum}");

// }

// fn main() {

//     let mut input = String::new();

//     println!("Enter a number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num1: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter second number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num2: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter third number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num3: i32 = input.trim().parse().expect("Invalid number");


//     max(num1, num2, num3);
// }


// fn max(num1: f32, num2: f32, num3: f32){
//     let mut sum: f32 = num1 + num2 + num3;
//     let average: f32 = (sum/3.0) as f32; 
//     println!("The average is {average}");

// }

// fn main() {

//     let mut input = String::new();

//     println!("Enter a number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let num1: f32 = input.trim().parse().expect("Invalid number");

    // println!("Enter second number: ");
    // input.clear();
    // io::stdin().read_line(&mut input).expect("Failed to read");
    // let num2: f32 = input.trim().parse().expect("Invalid number");

    // println!("Enter third number: ");
    // input.clear();
    // io::stdin().read_line(&mut input).expect("Failed to read");
    // let num3: f32 = input.trim().parse().expect("Invalid number");


//     max(num1, num2, num3);
// }


// fn range(min: i32, max: i32){
//     for i in min..max+1 {
//         println!("- {i} -");
//     }
// }

// fn main(){

//     let mut input = String::new();

//     println!("Enter min range: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let min: i32 = input.trim().parse().expect("Invalid number");

//     println!("Enter max number: ");
//     input.clear();
//     io::stdin().read_line(&mut input).expect("Failed to read");
//     let max: i32 = input.trim().parse().expect("Invalid number");

//     range(min, max);

// fn main(){
//     let mut arr = [0; 10];

//     for i in 0..10 {
        // println!("Enter number {i} to the array: ");
        // let mut input = String::new();
        // io::stdin().read_line(&mut input).expect("Failed to read");

//         arr[i] = input.trim().parse().expect("Please enter a valied number");
//     }

//     for num in arr {
//         println!("{num}");
//     }
//     if arr[0] == arr[9] {
//         println!("Yes")
//     } else {
//         println!("No")
//     }
// }

// fn main() {
    // for i in 1..101 {
    //     println!("{i}")
    // }
    // let mut i = 1;
    // while i < 101 {
    //     println!("{i}");
    //     i += 1;
    // }
    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input).expect("Failed to read");

    // let mut input = String::new();
    // println!("Enter a number: ");
    // io::stdin().read_line(&mut input).expect("Failed to read");
    // let number: i32 = input.trim().parse().expect("Invalid number");

    // if number > 20 {
    //     println!("We love Shmuel!");
    // } else {
    //     println!("Number is smaller than 20");
    // }

    // let mut input = String::new();
    // println!("Enter a starting point: ");
    // io::stdin().read_line(&mut input).expect("Failed to read");
    // let start: i32 = input.trim().parse().expect("Invalid number");
    // input.clear();
    // println!("Enter a ending point: ");
    // io::stdin().read_line(&mut input).expect("Failed to read");
    // let end: i32 = input.trim().parse().expect("Invalid number");

    // for i in start..end + 1 {
    //     println!("{i}");
    // }



    // fn display_full_name(first_name: &str, last_name: &str) {
    //     println!("Hello, {first_name} {last_name}");
    // }
    // display_full_name("Benny", "Oush");

    // fn sum_of_numbers(first_number: i32, last_number: i32) -> i32 {
    //     return first_number + last_number
    // }
    // let result = sum_of_numbers(3, 6);
    // println!("{result}");

    // fn greeting(name: &str, times: i32){
    //     for i in 0..times {
    //         println!("Hello, {name}!");
    //     }
    // }

    // greeting("Shmuel", 6);




    // fn average(num1: i32, num2: i32, num3: i32) -> f64 {
    //     (num1 + num2 + num3) as f64 / 3.0
    // }
    
    // let average = average(
    //     to_number(&input("number")),
    //     to_number(&input("number")),
    //     to_number(&input("number"))
    // );

    // println!("The average is {average}");




// }





fn main() {

    // fn is_positive(num: i32) -> bool {
    //     if num > 0 {
    //         return true;
    //     } else {
    //         return false;
    //     }
    // }

    // let result = is_positive(to_number(&input("number")));
    // println!("Is positive: {result}");



    // let mut numbers: Vec<i32> = Vec::new();

    // while numbers.len() < 10 {
    //     numbers.push(rand::random_range(1..=100));
    // }

    // fn arr_editor(numbers: Vec<i32>) {
    //     for (i, num) in numbers.iter().enumerate() {
    //     if i == 9 { 
    //         continue;
    //     }
    //         print!("{num} | ");
    //     }
    //     print!("{}", numbers[9]);
    // }
    // arr_editor(numbers);


    // let numbers = vec![12, 34, 56, 43, 76, 89, 45, 37, 84, 2];
    // let mut numbers: Vec<i32> = Vec::new();

    // while numbers.len() < 10 {
    //     numbers.push(rand::random_range(1..=100));
    // }
    
    // fn get_average(vector: &Vec<i32>) -> f64{
    //     let mut count = 0;
    //     let mut sum = 0;
    //     for n in vector {
    //         count += 1;
    //         sum += n;
    //     }
    //     sum as f64 / count as f64
    // }

    // let result = get_average(&numbers);
    // for n in numbers {
    //     print!("{n} ");
    // }
    // println!("\nthe average is {result}");

    // fn get_random_in_range(start: i32, end: i32) -> i32 {
    //     let random_num = rand::random_range(start..=end);
    //     random_num
    // }

    // let result = get_random_in_range(to_number(&input("number")), to_number(&input("number")));
    // println!("Number generated from given range: {result}")
    // let mut count = 0;
    // while count <= 100 {
    //     let result = get_random_in_range(rand::random_range(1..=10), rand::random_range(10..=20));
    //     println!("{result}");
    //     count += 1;
    // }

    // let names = ["Benny", "Yossi", "Shmuel", "Netanel", "David"];

    // fn get_longest<'a>(names: &'a [&'a str]) -> (&'a str, usize) {
    //     let mut longest = names[0];
    //     let mut len = names[0].len();

    //     for n in names {
    //         if n.len() > longest.len() {
    //             longest = n;
    //             len = n.len();
    //         }
    //     }
    //     (longest, len)
    // }

    // let result = get_longest(&names);
    // println!("The longest name is {} ({})", result.0, result.1);

    // let mut numbers: Vec<i32> = Vec::new();

    // while numbers.len() < 10 {
    //     numbers.push(rand::random_range(1..=100));
    // }
    
    // fn get_average(vector: &Vec<i32>) -> i32{
    //     let mut count = 0;
    //     let mut sum = 0;
    //     for n in vector {
    //         count += 1;
    //         sum += n;
    //     }
    //     let average = sum / count;
    //     count = 0;
    //     for n in vector {
    //         if n >= &average {
    //             count += 1;
    //         } 
    //     }

    //     count
    // }

    // let result = get_average(&numbers);
    // for n in &numbers {
    //     print!("{n} ");
    // }
    // println!("\n{result} numbers are equal to or greater than the vector's average");


    let mut numbers: Vec<i32> = Vec::new();

    while numbers.len() < 10 {
        numbers.push(rand::random_range(1..=100));
    }
    
    fn get_lowest(vector: &Vec<i32>) -> usize{
        let mut loewst = &vector[0];
        let mut lowest_index: usize = 0;
        for (i, num) in vector.iter().enumerate() {
            if num < loewst {
                loewst = num;
                lowest_index = i;
            }
        }
        lowest_index
    }

    let result = get_lowest(&numbers);

    print!("\nthe loewst number's Index in \n");
    for n in &numbers {
        print!("{n} ");
    }
    print!("\nis {result}");




}