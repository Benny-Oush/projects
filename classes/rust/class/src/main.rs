use std::io;

fn main() {
    // println!("Enter your name: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input);
    // println!("yout name is {input}");

    // println!("Enter the first number: ");
    // let mut input1 = String::new();
    // io::stdin().read_line(&mut input1)
    // .expect("Failed to read");

    // println!("Enter the second number: ");
    // let mut input2 = String::new();
    // io::stdin().read_line(&mut input2)
    // .expect("Failed to read");

    // println!("Enter the third number: ");
    // let mut input3 = String::new();
    // io::stdin().read_line(&mut input3)
    // .expect("Failed to read");

    // let num1:i32 = input1.trim().parse()
    // .expect("Failed to read");
    // let num2:i32 = input2.trim().parse()
    // .expect("Failed to read");
    // let num3:i32 = input3.trim().parse()
    // .expect("Failed to read");

    // let sum = num1 * num2 * num3;
    // println!("The result is {}", sum);
    

    //     println!("Enter number:");

//     let mut input = String::new();

//     io::stdin().read_line(&mut input).unwrap();

//     let number: i32 = input.trim().parse().unwrap();

//     println!("Number is {}", number);


    // תרגיל 1: 

    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input)
    // .expect("Failed to read");

    // let num:i32 = input.trim().parse()
    // .expect("Failed to read");

    // let sum = num * 2;
    // println!("{} * 2 is: {}", num, sum);

    // // תרגיל 2: 

    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input)
    // .expect("Failed to read");

    // let num:i32 = input.trim().parse()
    // .expect("Failed to read");

    // let sum = num + 10;
    // println!("{} + 10 is: {}", num, sum);

    // // תרגיל 3:
    
    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input)
    // .expect("Failed to read");

    // let num:i32 = input.trim().parse()
    // .expect("Failed to read");

    // let sum = num / 2;
    // println!("{} / 2 is: {}", num, sum);

    // let score = 99;

    // match score {
    //     90..=100 => println!("score: {}. grade: Excellent!", score),
        
    //     80..=89 => println!("score: {}. grade: Great.", score),
        
    //     70..=79 =>  println!("score: {}. grade: Good.", score),
       
    //     60..=69 => println!("score: {}. grade: Needs improvement.", score),
        
    //     _ => println!("score: {}. You did not pass the exam!", score),


        // let age = 21;
    // let is_old = if age > 60{
    //     true
    // } else {
    //     false
    // };

    // println!("age = {age}. \nis old = {is_old}");


    // // "loop" loop

    // let mut count = 0;
    // loop{
    //     count+=1;

    //     if count == 5{
    //         break;
    //     }

    //     println!("{count}");
    // }

    // let mut counter = 0;

    // let result1 = loop{
    //     counter += 1;
    //     if counter == 10 {
    //         break counter * 2;
    //     }
    // };
    // println!("{result1}");
// // תרגיל 1

    // let mut number = 1;
    // while number <= 100 {
    //     println!("{number}");
    //     number += 1;
    // }

// // תרגיל 2

//     let mut number = 100;
//     while number >= 1 {
//         println!("{number}");
//         number -= 1;
//     }

    // // תרגיל 3

    //     let mut number = 1;
    // while number <= 100 {
    //     println!("{number}");
    //     number += 2;
    // }

    // // תרגיל 4
    // let mut number = 2;
    // while number <= 100 {
    //     println!("{number}");
    //     number += 2;
    // }

    // // תרגיל 5
    // let mut number = 3;
    // while number <= 100 {
    //     println!("{number}");
    //     number += 3;
    // }

    // // תרגיל 6
    // let mut number = 6;
    // while number <= 100 {
    //     println!("{number}");
    //     number += 6;
    // }

    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input)
    // .expect("Failed to read");

    // let num:i32 = input.trim().parse()
    // .expect("Failed to read");

    // let mut number3 = num - 1; 
    // while number3 > 0{
    //     println!("{number3}");
    //     number3 -= 1;
    // };

    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input)
    // .expect("Failed to read");

    // let num:i32 = input.trim().parse()
    // .expect("Failed to read");

    // if num % 2 == 0{
    //     let mut number3 = num - 2; 
    //     while number3 > 0 {
    //     println!("{number3}");
    //     number3 -= 2;
    //     }

    // } else {
    //     let mut number3 = num - 1; 
    //     while number3 > 0 {
    //     println!("{number3}");
    //     number3 -= 2;
    //     }
    // };
    
    // println!("Enter a number: ");
    // let mut input = String::new();
    // io::stdin().read_line(&mut input)
    // .expect("Failed to read");

    // let num:i32 = input.trim().parse()
    // .expect("Failed to read");

    // if num % 2 == 1{
    //     let mut number3 = num - 2; 
    //     while number3 > 0 {
    //     println!("{number3}");
    //     number3 -= 2;
    //     }

    // } else {
    //     let mut number3 = num - 1; 
    //     while number3 > 0 {
    //     println!("{number3}");
    //     number3 -= 2;
    //     }
    // };

        // let mut rep = 0;

        // while rep < 10 {
        //         println!("Enter a number: ");
        //         let mut input = String::new();
        //         io::stdin().read_line(&mut input)
        //         .expect("Failed to read");

        //         let num:i32 = input.trim().parse()
        //         .expect("Failed to read");

        //         if num >= 50 {
        //             println!("the number {num} is greater than 50!");
        //         }
        //         rep += 1;
        //     }



        // let mut rep = 0;

        // while rep < 10 {
        //     println!("Enter a number: ");
        //     let mut input = String::new();
        //     io::stdin().read_line(&mut input)
        //     .expect("Failed to read");

        //     let num:i32 = input.trim().parse()
        //     .expect("Failed to read");

        //     if num >= 50 && num < 100 && num % 2 == 0{
        //         println!("the number {num} is over 50, smaller than 100 and even!");
        //     }
        //     rep += 1;
        // }



    











}










