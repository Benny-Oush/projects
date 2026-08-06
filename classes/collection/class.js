let x1 = Math.floor(Math.random() * 10);
let y1 = Math.floor(Math.random() * 10);
console.log("x = " + x1);
console.log("y = " + y1);
if (Math.abs(x1 - y1) === 3){
 console.log('the difference is 3');
}

if (x1 & 2 === 0){
 console.log('x is even');
} else {
 console.log('x is not even');
}

let grade1 = Math.floor(Math.random() * 101);
if (grade1 >= 60) {
  console.log("Your grade is " + grade1 + "\nCongratulations, you passed! ");
} else {
  console.log("Your grade is " + grade1 + "\nYou did not pass ");
}
let x2 = Math.floor(Math.random() * 10);
let y2 = Math.floor(Math.random() * 20);
if (y2/2 >= x2){
  console.log('congratulations, you won!');
} else {
  console.log('you lost, good luck next time!');
}
let text = 'Hello Yoav 9'
console.log('the text is: ' + text);
let num = Math.floor(Math.random() * 15);
console.log('the number is: ' + num);
if (text.length == num){
  console.log('the text is as long as the number');
} else if (text.length < num) {
  console.log('the text is shorter than the number');
} else {
  console.log('the text is longer than the number');
}
let grade = Math.floor(Math.random() * 101);
if (grade >= 90 && grade <= 100){
  console.log('your grade is A');
} else if (grade >= 80 && grade <= 89){
  console.log('your grade is B');
} else if (grade >= 70 && grade <= 79){
  console.log('your grade is C');
} else if (grade >= 60 && grade <= 69){
  console.log('your grade is D');
} else if (grade >= 0 && grade <= 50){
  console.log('your grade is F');
}
console.log(grade);
let num1 = Math.floor(Math.random() * 11);
let num2 = Math.floor(Math.random() * 11);
console.log(num1 + "\n" + num2);
if (num1 % 2 === 0 && num2 % 2 === 0){
  console.log('both');
} else if ((num1 % 2 === 0 && num2 % 2 === 1) || (num1 % 2 === 1 && num2 % 2 === 0)){
  console.log('one');
} else {
  console.log('none');
}
console.log('the end');
