// for (let l = 0; l < 8; l++) {
//   console.log(l + 1, "hello world");
// }
// for (let d = 1; d < 501; d++) {
//   console.log(d, d**2);
// }
// let counter = 1
// for (let k = 0; k < 900; k++) {
//     if (k % 3 === 0 && k % 2 === 1){
//         console.log(counter + ': ' + k);
//         counter++;
//     }
// }
// let j = Math.floor(Math.random() * 10);
// console.log(j)
// for (let y = 0; y < j; y++){
//     console.log('abc');
// }
// let i = Math.floor(Math.random() * 10);
// console.log(i);
// while (i > 0){
//     console.log('abc')
//     i--
// }
let h = Math.floor(Math.random() * 10);
let text = 'abc\n ';
let result = '';
for (let n = 0; n < h; n++){
    result += text;
}
console.log(result);

let final = 0;
for (let j = 0; j < 200; j++) {
  if ((j % 3 === 0 || j % 7 === 0) && j % 5 !== 0) {
    final += j;
    // console.log(j)
  }
}
console.log(final);
