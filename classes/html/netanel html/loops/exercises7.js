// Lesson 6 Lab: Functions

// Task 1: Basic Function Declaration
// 1. Create a function named 'welcome'.
// 2. It should take one parameter 'name'.
// 3. It should print "Welcome to JS, [name]!".
// Write your code below:

// const welcome = (name) => console.log(`Welcome to JS, ${name}!`);
// welcome(prompt('enter your name: '))

// Task 2: Function with Return
// 1. Write a function 'multiply' that takes two numbers.
// 2. It should RETURN the product of the two numbers using addition only.
// 3. Call the function and store the result in a variable 'res'.
// 4. Print 'res'.
// Write your code below:

// function multiply(num1, num2) {
//     let result = 0;
//     for (let i = 0; i < num1; i++) {
//         result += num2
//     }
//     return result;
// }

// let res = multiply(+prompt('enter a number: '), +prompt('enter a second number: '));
// console.log(res);

// Task 3: Circle Area
// 1. write a function that gets a raduis and returns its area:.
// 2. call the funtion save the return value in a veriable calles area
// 3. print the result in a nice message
// Write your function below:

// function circle_erea(raduis){
//     let raduisPow = 0;
//     for (let i = 0; i < raduis; i++){
//         raduisPow += raduis
//     }
//     let circleErea = 0;
//     for (let i = 0; i < raduisPow; i++){
//         circleErea += Math.PI
//     }
//     return circleErea;
// }

// let erea = circle_erea(+prompt("enter the raduis: "));
// console.log(erea);

// Task 4: Power function with multiplication only
// 1. Write a function 'pow(x, n)' that returns x in power n.
// 2. (Assume n is a positive integer).
// Example: pow(3, 2) = 3 * 3 = 9.
// Write your code below:

// function pow(x, n = 2) {
//     let result = 1;
//     for (let i = 0; i < n; i++){
//         result *= x
//     }
//     return result
// }

        

// arr = ["a", "b", "c", "d"];
// arr.splice(2, 1, "f", "k", "l")
// arr2 = ["e", "f", "g"]
// console.log(`${arr},${arr2}`);


// arr = [
//     { id: 4, name: "Tesla", price: 20000},
//     { id: 5, name: "BMW", price: 10000},
//     { id: 3, name: "Audi", price: 30000},
//     { id: 1, name: "Mercedes", price: 40000},
//     { id: 2, name: "Toyota", price: 50000}
// ]

// arr.myFilter = function(fn) {
//     const newArr = [];
//     for (let item of this) if (fn(item)) newArr.push(item)
//     return newArr
// }

// const result = arr.myFilter(car => car.price > 25000 && car.price < 45000);
// console.log(result);


// let user = {
//     name: "John",
//     sayHi() {
//         console.log(this.name);
        
//     }
// }

// user.sayHi()



