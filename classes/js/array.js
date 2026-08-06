// let arr = [3, 7, 2, 9, 5];

// for (let i = 0; i < 5; i++){
//     console.log(arr[i]);
// }

// let arr = [1, 2, 3, 4, 5];
// for (let i = 5; i >= 0; i--){
//     console.log(arr[i]);
// }

// let sum = 0;
// let arr = [4, 8, 2, 6];

// for (let i = 0; i < 4; i++){
//     sum += arr[i]
// }
// console.log(sum);

// let count = 0;
// let arr = [1, 10, 3, 12, 5, 20];
// for (let i = 0; i < 6; i++){
//     if (arr[i] > 6){
//         count += 1;
//     }
// }
// console.log(count + " numbers of the list (" + arr + ") are greater than 6");

// let bigest = 0;
// let arr = [3, 17, 9, 2, 25, 4];

// for (let i = 0; i < 6; i++){
//     if (arr[i] > bigest){
//         bigest = arr[i];
//     }
// }
// console.log(bigest);

// let last_odd = 0;
// let arr = [2, 4, 6, 7, 8, 9];

// for (let i = 0; i < 6; i++){
//     if (arr[i] % 2 == 1){
//         last_odd = arr[i];
//     }
// }
// console.log(last_odd);

// let arr = [];

// for (let i = 1; i < 11; i++){
// arr.push(i);
// }
// console.log(arr);

// // sol 1
// let arr = [];

// for (let i = 2; arr.length < 20; i += 2){
//     arr.push(i)

// }

// console.log(arr);

// // sol 2

// let arr = [];
// let i = 2;

// while (arr.length < 20){
//     arr.push(i)
//     i += 2
// }
// console.log(arr);

// let arr = [];

// for (let i = 1; i < 11; i++){
// arr.push(i*i);
// }
// console.log(arr);

// let arr = [1, 2, 3, 4, 5];
// let rev_arr = [];
// for (let i = 4; i >= 0; i--){
//     rev_arr.push(arr[i])
// }
// console.log(arr);
// console.log(rev_arr);

// // sol 1
// let arr = [5, 10, 15];
// let new_arr = [];

// for (i of arr){
//     new_arr.push(i)
// }
// console.log(arr);

// console.log(new_arr);

// // sol 2
// let arr = [5, 10, 15];
// let new_arr = [];

// for (let i = 0; i < 3; i++){
//     new_arr.push(arr[i])
// }
// console.log(arr);
// console.log(new_arr);

// let arr = [3, 12, 7, 20, 5];
// let new_arr = [];

// for (let i = 0; i < arr.length; i++){
//     if (arr[i] > 10){
//         new_arr.push(arr[i])
//     }
// }
// console.log(new_arr);

// let arr = [1, 2, 3, 4, 5];
// arr.pop();
// arr.pop();
// console.log(arr);

// let arr = [3, 6, 9];

// for (let i = 0; i <= arr.length + 1; i++){
//     arr.pop()
// }
// console.log(arr);

// let arr = [1, 2, 3, 4, 5, 6];
// let new_arr = [];

// for (let i = 0; i < 6; i++) {
//   if (arr[i] % 2 == 0) {
//     new_arr.push(arr[i]);
//   }
// }

// console.log(arr);
// console.log(new_arr);


// let arr = [2, 4, 6];
// let new_arr = [];

// for (let i = 0; i < 3; i++){
//     new_arr.push(arr[i]*2)
// }
// console.log(new_arr);


// let arr = [1, 2, 3, 4];
// let new_arr = [];
// let num = 0;

// for (let i = 0; i < arr.length; i++){
//     new_arr.push(num + arr[i])
//     num = new_arr[i]
// }

// console.log(new_arr);


// let arr = [3, 7, 12, 5, 20];
// let num = 0;

// for (let i = 0; i < arr.length; i++){
//     num = arr[i]
//     if (num > 10){
//         break
//     }
// }
// console.log(num);

// let arr = [1, 2, 3, 2, 4, 2];
// let times = 0;

// for (let i = 0; i < arr.length; i++){
//     if (arr[i] == 2){
//         times += 1
//     }
// }
// console.log(times);

// let arr = [];

// for (let i = 1; i < 11; i++){
//     arr.push(i)
//     arr.push(-i)
// }
// console.log(arr);

// // sol 1
// let a = [1, 2, 3];
// let b = [4, 5, 6];

// let new_arr = [];

// for (let i = 0; i < a.length; i++){
//     new_arr.push(a[i])
// }

// for (let i = 0; i < b.length; i++){
//     new_arr.push(b[i])
// }
// console.log(new_arr);

// sol 2
// let a = [1, 2, 3];
// let b = [4, 5, 6];

// let new_arr = [];

// for (let i = 0; i < a.length+b.length; i++){
//     if (i < a.length){
//     new_arr.push(a[i])
//     } else{
//             new_arr.push(b[i - a.length])
//     }
// }

// console.log(new_arr);



// for (let i = 1; i < 6; i++){
//     for (let j = 1; j < 6; j++){
//         console.log("(" + i + ", " + j +")");
//     }
// }


// for (let i = 1; i < 6; i++){
//     for (let j = 1; j < 6; j++){
//         if (i + j == 6){
//             console.log("(" + i + ", " + j +")");
//         }
//     }
// }


// let arr = [1, 2, 3, 2, 4, 1];

// for (let i = 0; i < arr.length; i++){
//     for (let j = i + 1; j < arr.length; j++){
//         if (arr[i] == arr[j]){
//             console.log(arr[i])
            
//         }
//     }
// }


// let arr = [1, 2, 1, 5, 4, 3, 4];
// let unique = [];

// for (let i = 0; i < arr.length; i++){
//     let count = 0;
//     for (let j = 0; j < arr.length; j++){
//         if (arr[i] == arr[j]){
//             count++
//         }
//     }
//     if (count == 1){
//         unique.push(arr[i])    
//     }
// }
// console.log(unique);


// let arr = [1, 2, 3, 1, 2, 3, 4, 1];

// let longest = 1;
// let current = 1;

// for (let i = 1; i < arr.length; i++){
//     if (arr[i] > arr[i-1]){
//         current++
//     } else {
//         current = 1
//     }
//     if (current > longest){
//         longest = current
//     }
// }
// console.log("The longest sequence length is " + longest);

// let arr = [5, 2, 8, 1];

// for (let i = 0; i < arr.length; i++){
//     for (let j = 0; j < arr.length-1; j++){
//         if (arr[j] > arr[j+1]){
//         [arr[j],  arr[j+1]] = [arr[j+1], arr[j]]
//         }
//     }
// }
// console.log(arr);


// let arr = [10, 5, 20, 8];
// let largest = -Infinity;
// let second_largest = -Infinity;

// for (let i = 0; i < arr.length; i++){    
//     if (arr[i] > largest){
//         second_largest = largest
//         largest = arr[i]
//     } else if (second_largest < arr[i] && largest > arr[i]) {
//         second_largest = arr[i]
//     }
// }

// console.log(second_largest);

// let arr = [1,2,3,4,5,6];

// let evens = [];
// let odds = [];

// for (let i = 0; i < arr.length; i++){
//     if (arr[i] % 2 == 0){
//         evens.push(arr[i])
//     } else {
//         odds.push(arr[i])
//     }
// }

// console.log("evens: " + evens);
// console.log("odds: " + odds);













