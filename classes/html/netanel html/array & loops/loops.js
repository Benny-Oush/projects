// // --- תרגיל 1 ---
// for (let i = 1; i < 11; i++){
//     if (i % 2 == 0){
//         console.log(`The number '${i}' is even`);  
//     } else {
//         console.log(`The number '${i}' is odd`);
//     }
// }

// // --- תרגיל 2 --- 
// for (let i = 20; i > 0; i--){
//     if (i % 3 > 0){
//         console.log(i);  
//     }
// }

// // --- תרגיל 3 ---
// for (let i = 1; i < 51; i++){
//     if (i % 4 == 0 && i % 6 == 0){
//         console.log(i);
//         break 
// }

// // --- תרגיל 4 ---
// let count = 0;
// for (let i = 1; i < 101; i++){
//     if (i % 7 == 0){
//         count++
//     }
// }
// console.log(`Between 1-100, ${count} numbers are divisible by 7`);

// // --- תרגיל 5 ---
// let numbers_sum = 0;
// for (let i = 1; i < 101; i++){
//     if (i % 5 == 0){
//         numbers_sum -= i
//     } else {
//         numbers_sum += i
//     }
// }
// console.log(numbers_sum);

// // --- תרגיל 6 ---
// let count = "";
// for (let i = 1; i < 6; i++){
//     count += "* "
//     console.log(count);
// }

// // --- תרגיל 7 ---
// for (let i = 1; i < 51; i++){
//     if (i % 4 > 0){
//         console.log(i);  
//     }
//     if (i % 17 == 0){
//         break
//     }
// }

// // --- תרגיל 8 ---
// let last = 0;
// for (let i = 1; i < 101; i++){
//     if (i % 9 == 0){
//         last = i
//     }
// }
// console.log(`The last number between 1-100 that is is divisible by 9 is ${last}`);

// // --- תרגיל 9 --- 
// let result = 1;
// while (result <= 1000){
//     console.log(result);
//     result *= 3  
// }

// // --- תרגיל 10 ---
// let counter = 0;
// for (let i = 1; i < 201; i++){
//     if ((i % 3 == 0) && (i % 5 != 0)){
//         counter++  
//     }
// }
// console.log(counter);

// // --- תרגיל 11 ---
// let sum = 0;
// let count = 0;

// while (sum <= 100){
//     count++
//     sum += count  
// }
// console.log(sum - count);
// console.log(count - 1);

// // --- תרגיל 12 ---
// let current = 100;
// while (current > 0){
//     current -= 7
// }
// console.log(current + 7);



// // --- תרגיל 13 ---

// const num = Math.floor(Math.random() * 100) 
// let counter = 0;
// for (let i = 1; i <= num; i++){
//     if (num % i == 0){
//         counter++
//     }
// }
// console.log(num);
// console.log(counter);

// // --- תרגיל 14 ---
// const num = Math.floor(Math.random() * 100) 
// let is_prim = num > 1;
// for (let i = 2; i < num; i++){
//     if (num % i == 0){
//         is_prim = false
//         break
//     }
// }
// if (is_prim) {
//     console.log(`${num} is a prime number`);
// } else {
//     console.log(`${num} is not a prime number`);
// }

// // --- תרגיל 15 ---
// let count = 0;
// for (i = 2; i <= 1000; i++){
//     const num = i 
//     let is_prim = num > 1;
//     for (let j = 2; j < num; j++){
//         if (num % j == 0){
//             is_prim = false
//             break
//         }
//     }
//     if (is_prim) {
//         count++
//     }
// }
// console.log(`There are ${count} prime numbers between 1-1000`);

// // --- תרגיל 16 ---
// let counter = 0;
// let current_longest = 0;
// for (let i = 1; i < 101; i++){
//     if (i % 3 == 0){
//         counter++
//     } else {
//         counter = 0
//     }
//     if (counter > current_longest){
//         current_longest = counter
//     }
// }
// console.log(current_longest);

// // --- תרגיל 17 ---
// let row = '';
// for (let i = 1; i < 6; i++){
//     if (i != 3){
//         row += i
//         console.log(row);       
//     }
// }

// // --- תרגיל 18 ---
// let row = '';
// for (let i = 1; i < 6; i++){
//     for (let j = 1; j < 6; j++){
//         row += `${(j * i).toString().padStart(2, ' ')} `;
//     }
//     console.log(row);
//     row = '';
// }

// // --- תרגיל 19 ---
// let row = '';
// for (let i = 1; i < 6; i++){
//     for (let j = 1; j < 6; j++){
//         if (j == i){
//             row += "x "
//         } else {
//             row += "0 "
//         }
//     } 
//     console.log(row)
//     row = '';
// }

// // --- תרגיל 20 ---
// let row = '';
// for (let i = 1; i < 5; i++){
//     for (let j = 0; j < i; j++){
//         row += i
//     } 
//     console.log(row)
//     row = '';
// }

// --- תרגיל 21 ---
// sol 1

// let row = '*****';
// for (let i = 5; i > 0; i--){
//     console.log(row)
//     row = row.slice(1)
// }

// // sol 2
// let row = '';
// for (let i = 5; i > 0; i--){
//     for (let j = i; j > 0; j--){
//         row += '*'
//     }
//     console.log(row);
//     row = ''  
// }

// // --- תרגיל 22 ---
// let prime_row = [];
// for (i = 2; i <= 50; i++){
//     const num = i 
//     let is_prim = num > 1;
//     for (let j = 2; j < num; j++){
//         if (num % j == 0){
//             is_prim = false
//             break
//         }
//     }
//     if (is_prim) {
//         prime_row.push(num)
//         if (prime_row.length === 5){
//             console.log(prime_row);
//             prime_row = []
//         }
//     }
// }

// // --- תרגיל 23 ---
// let num_of_divisors = 0;
// for (let i = 1; i < 11; i++){
//     for (let j = 1; j <= i; j++){
//         if (i % j === 0){
//             num_of_divisors++
//         }
//     }
//     console.log(`number ${i} has ${num_of_divisors} divisors `);
//     num_of_divisors = 0;
// }

// // --- תרגיל 24 ---
// for (let i = 1; i < 201; i++){
//     if (i % 12 === 0){
//         console.log(`number ${i} is divisible by both 4 and 6 `);
//     }
// }

// // --- תרגיל 25 ---
// let height = 4;
// for (let i = 1; i <= height; i++){
//     let row = ''
//     for (let j = 1; j <= height - i; j++){
//         row += ' '
//     } 
//     for (let k = 1; k <= (i * 2 -1); k++){
//             row += '*'
//         }
//     console.log(row);
// }

// // --- תרגיל 26 ---
// let max_div_by_7 = 0;
// let row = [];
// for (let i = 1; i < 101; i++){
//     if (i % 7 === 0){
//         max_div_by_7 = i
//     }
//     row.push(i);
//     if (row.length === 10){
//         // console.log(row.join("\t"));
//         console.log(...row);
//         row = [];
//     }
// }

// console.log(`The largest number between 1-100 divisible by 7 is ${max_div_by_7}`);

// --- תרגיל 27 ---
// for (let i = 1; i < 21; i++){
//     for (let j = 1; j < 21; j++){
//         if (j + i === 15){
//             console.log(`${i} + ${j} = 15`);
//             break
//         }
//     }
// }

// // --- תרגיל 28 ---
// // sol 1
// for (let i = 1; i < 101; i++){
//     if ((i % 3 === 0) && (i % 5 === 0)){
//         console.log("FizzBuzz");
//     } else if (i % 5 === 0){
//         console.log("Buzz");
//     } else if (i % 3 === 0) {
//         console.log("Fizz");
//     } else {
//         console.log(i);
//     }
// }

// // sol 2
// for (let i = 1; i < 101; i++){
//     let output = "";
//     if (i % 3 === 0) output += "Fizz"
//     if (i % 5 === 0) output += "Buzz"

//     console.log(output || i);
// }

// // --- תרגיל 29 ---
// let row = [];
// for (let i = 1; i < 17; i++){
//     row.push(i)
//     if (row.length === 4){
//         console.log(row.join("\t"));
//         row = [];
//     }
// }

// // --- תרגיל 30 ---
// let row = [];
// for (let i = 1; i < 6; i++){
//     if (i % 2 == 0){
//         row.unshift(0)
//     } else {
//         row.unshift(1)
//     }
//     console.log(...row);
// }
