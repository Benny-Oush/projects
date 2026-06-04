// Lesson 7 Lab: Objects (Basics)

// Task 1: Basic Object
// 1. Create an empty object 'user'.
// 2. Add the property 'name' with the value 'John'.
// 3. Add the property 'surname' with the value 'Smith'.
// 4. Change the value of the 'name' to 'Pete'.
// 5. Delete the property 'name' from the object.
// Write your code below:

// const user = {};

// user.name = 'John';
// user.surname = 'Smith';
// user.age = 35;

// user.name = 'Pete';

// delete user.name;

// console.log(user);



// Task 2: Check for Emptiness
// Write a function 'isEmpty(obj)' that returns true if the object has no properties, 
// and false otherwise.
// Write your code below:

// function isEmpty(object) {
//     let result = true;
//     for (let parameter in object){
//         result = false
//         break
//     }
//     return result
// }

// console.log(isEmpty(user));



// Task 3: Sum Object Properties
// 1. Create an object 'salaries' with values: John: 100, Ann: 160, Pete: 130.
// 2. Write code to sum all salaries and print the result.
// Write your code below:

// const salaries = {
//     John: 100,
//     Ann: 160,
//     Pete: 130
// }

// let sumOfSalaries = 0;

// for (let key in salaries) {
//     sumOfSalaries += salaries[key]
// } 
// console.log(sumOfSalaries);

// Task 4: Multiply Numeric Property Values by 2
// 1. Create a function 'multiplyNumeric(obj)'.
// 2. It should multiply all numeric property values of 'obj' by 2.
// (Hint: use 'typeof' to check if a value is a number).
// Write your code below:

// const user = {};

// user.name = 'John';
// user.surname = 60;
// user.age = 35;

// function multiplyNumeric(object) {
//     let numArr = [];
//     for (let key in object){
//         if (typeof object[key] === 'number'){
//             numArr.push(object[key]);
//         }
//     }
//     return numArr
// }

// console.log(multiplyNumeric(user));

// for (let num of multiplyNumeric(user)) {
//     console.log(num * 2);
// }
