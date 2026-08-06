// const inputSisterAge = +prompt("Enter your sister's age: ")
// const inputAge = +prompt("Enter your age: ")
// const inputBrotherAge = +prompt("Enter your brother's age: ")

// console.log(inputAge, inputBrotherAge, inputSisterAge);

// for (let i = 0; i < 10; i++){
//     console.log("I'm so tired! ", i);
// }
// let limit = +prompt("Enter loop's limit: ");
// let i = 0;
// while (i < limit){
//     console.log("Hi!", i+1);
//     i++
// }

// let limit = +prompt("Enter loop's limit: ");

// while (limit-- >= 0){
//     console.log("Hi!", limit+1);
// }

// let start = +prompt("Enter loop's start: ");
// let end = +prompt("Enter loop's end: ");

// while (start <= end){
//     console.log(start);
//     start++
// }

// const isHungry = +prompt("Are you hungry? (1 = yes/0 = no)");

// if (isHungry) {
//     console.log("Go eat something ");
// } else {
//     console.log("Great. More for me ");
// }

// let xCount = 0;

// for (let i = 0; i < 15; i++){
//     const character = prompt(`Please enter character ${i+1}:`);
//     if (character == "x"){
//         xCount++
//     }
// }

// console.log(`You entered ${xCount} times the letter X`);

// let loopStart = +prompt("Enter loop's start: ");
// let loopEnd = +prompt("Enter loop's end: ");

// let sum = 0;

// if (loopStart > loopEnd){
//     console.log("Assuming you had a mistake and you entered the numbers in the wrong order, ");
//     [loopStart, loopEnd] = [loopEnd, loopStart]
// }

// for (let i = loopStart; i <= loopEnd; i++){
//     sum += i;
// }
// console.log(`the sum of all of the numbers in the given range (${loopStart}, ${loopEnd}) is ${sum}`);



// const numOfStudents = +prompt("How many students are in your class? ");

// let youngest = Infinity;
// let oldest = -Infinity;

// for (let i = 0; i < numOfStudents; i++) {
//   const studentAge = +prompt(`Enter the age of student ${i + 1}`);
//   if (studentAge < youngest) {
//     youngest = studentAge;
//   }
//   if (studentAge > oldest) {
//     oldest = studentAge;
//   }
// }

// let classType;

// if (oldest - youngest > 3) {
//   classType = "heterogeneous";
// } else {
//   classType = "homogeneous";
// }

// console.log(`youngest's age - ${youngest}, oldest's age - ${oldest}`);
// console.log(`Your class is ${classType}`);




// let candidate1 = 0;
// let candidate2 = 0;

// for (let i = 0; i < 41; i++){
//     const vote = +prompt(`Student ${i+1}, to which of the two candidates do you want to vote for? (enter 1/2)`);
//     if (vote === 1){
//         candidate1++
//     } else if (vote === 2){
//         candidate2++
//     }
// }

// let winner = "candidate";

// if (candidate1 > candidate2){
//     winner += " 1"
// } else {
//     winner += " 2"
// }

// console.log(`The winner is ${winner}`);


// const limit = +prompt("How big do you want the multiplication table to be? (enter 5 for a 5x5 table)");

// for (let i = 1; i <= limit; i++){
//     let row = [];

//     for (let j = 1; j <= limit; j++){
//         row.push(i * j);
//     }
//     console.log(...row);
// }


// const sum = (a, b) => a + b;

// const sum2 = function (a, b) {
//     return a + b;
// }

// function sum3(a, b) {
//     a + b    
// }\


// let car = {
//     model: prompt('What model is your car? '),
//     price: prompt('how much did your car cost? ')
// };



