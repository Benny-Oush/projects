use std::io;
fn main() {

    let mut name = "benny";
    println!("before: {}" , name);
    name = "Benny";
    println!("after: {}" , name);

    let x = 5;
    let x = x + 10;
    let x = x * 2;
    println!("x = {}", x);
    
    let person = (21, 178.5, true);
    println!("age: {}", person.0);
    println!("height: {}", person.1);
    println!("is student: {}", person.2);

    let grades = [100, 98, 89, 97];
    println!("the first grade is: {}", grades[0]);
    println!("the last grade is: {}", grades[3]);

    let new = grades[2] as f64;
    println!("{new}");
    
    let number = 8;
    let result = if number % 2 == 0{
        format!("the number {}  is even", number)
    } else {
        format!("the number {} is odd", number)
    };
    println!("{result}");

    let age = 20;
    if age >= 18 && age <= 65 {
    println!("Working age");
    }

    let score = 59;
    if score >= 90 {
        println!("score: {}. grade: Excellent", score);
    } else if score >= 80 {
        println!("score: {}. grade: Great", score);
    } else if score >= 70 {
        println!("score: {}. grade: Good", score);
    } else if score >= 60 {
        println!("score: {}. grade: Needs improvement", score)
    } else {
        println!("score: {}. You did not pass the exam!", score)
    }
    let get_num = 14;
    if get_num > 0{
        "Positive"
    } else if get_num > 0{
        "Negative"
    } else {
        "Zero"
    };

    let get_age = 21;
    if get_age < 18{
        "Minor"
    } else {
        "Adult"
    };

    println!("Hi! what is your name? ");
    let mut name_input = String::new();
    io::stdin()
        .read_line(&mut name_input)
        .expect("Failed to read");
    println!("\nHello, {}!", name_input.trim());

    println!("\nhow old are you? ");
    let mut age_input = String::new();
    io::stdin()
        .read_line(&mut age_input)
        .expect("Failed to read");
    println!("\nyou are {} years older than me! i'm barely a few minutes old...", age_input.trim());

    println!("\nwhere do you live? ");
    let mut city_input = String::new();
    io::stdin()
        .read_line(&mut city_input)
        .expect("Failed to read");
    println!("\nnice,! {} is a beautiful place!", city_input.trim());
    println!("\nso, in conclusion: \nyour name is {}, \nyou are {} years old and you live in {}. \nit was a pleasure talking to you!", name_input.trim(), age_input.trim(), city_input.trim());

    let price = 549;
    println!("the product costs {} dollars", price);

    let first_name = "Benny";
    let last_name = "Oush";
    let country = "Israel";
    println!("hi, my name is {} {} and I live in {}", first_name, last_name, country);

    let year = "2026";
    println!("the current year is {}", year);

    let width = 12;
    let height = 6;
    println!("rectangle width: {}. \nrectangle height: {}", width, height);
    println!("the area of the rectangle is {}", width * height);

    let language = "rust";
    println!("today, I am learning to code in {}", language);

    let temperature = 19;
    if temperature >= 30{
        println!("the temperature today is: {}. \nit is a hot day!", temperature);
    } else {
        println!("the temperature today is: {}. \nthere is a nice weather today!", temperature);
    }

    let score1 = 78;
    if score1 > 60{
        println!("score: {}. you passed", score1)
    } else {
       println!("score: {}. you failed", score1)
    }

    let num2 = 67;
    if num2 > 0{
        println!("the number is positive")
    } else {
        println!("the number is negative or zero")
    }

    let coins = 12;
    if coins > 10{
        println!("you are rich!")
    } else {
        println!("you are poor...")
    }

    let day = 7;
    if day == 7{
        println!("it is weekend")
    } else {
        println!("it is weekday")
    }

    let speed = 107;
    if speed > 100{
        println!("speed: {}. you are driving too fast", speed)
    } else {
        println!("speed: {}. you are driving at safe speed", speed)
    }

    let battery = 23;
    if battery > 60{
        println!("battery percentage: {}. you don't need to charge.", battery)
    } else if  battery > 40 && battery < 60{
        println!("battery percentage: {}. it is recommended to charge.", battery)
    } else {
        println!("battery percentage: {}. you need to charge!", battery)
    }

    let password = "56789343";
    if password.len() >= 8{
        println!("strong password")
    } else {
        println!("weak password")
    }

    use std::io;

let mut input = String::new();

io::stdin()
    .read_line(&mut input)
    .expect("Failed to read");


    
}
