// let m = Math.floor(Math.random()*15);

// let sum = 1;
// for (let k = 1; k <= m; k++){
//     sum *= k;
// }
// console.log(m, sum);

// let n = Math.floor(Math.random()*10);

// for (let i = 0; i < n; i++){
//     let row = '';
//     for (let j = 0; j < n; j++){
//         row += '  *';
//     }
//     console.log(row)
// }

// let n = Math.floor(Math.random() * 10) + 1;
// console.log("n =", n);

// for (let i = 1; i <= n; i++) {
//   let row = "";
//   for (let j = 0; j < i; j++) {
//     row += "*  ";
//   }
//   console.log(row);
// }

// for (let i = n - 1; i >= 1; i--) {
//   let row = "";
//   for (let j = 0; j < i; j++) {
//     row += "*  ";
//   }
//   console.log(row);
// }

// let week_days = [
//   "Sunday",
//   "Monday",
//   "Tuesday",
//   "Wednesday",
//   "Thursday",
//   "Friday",
//   "Saturday",
// ];
// for (i of week_days) {
//   console.log(i);
// }

const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});

readline.question('What is your name? ', name => {
  console.log(`Hi, ${name}!`);
  readline.close();
});