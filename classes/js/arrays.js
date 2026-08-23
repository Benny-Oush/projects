// ------------------
// Cluster 1: Numbers, basic map/filter/some
// ------------------
const nums1 = [3, 6, 9, 12, 15];

// Exercise 1.1
console.log(nums1.map((n) => n * 2));
// 6, 12, 18, 24, 30
// Exercise 1.2
console.log(nums1.filter((n) => n > 10));
// 12, 15
// Exercise 1.3
console.log(nums1.some((n) => n % 4 === 0));
// true
// Exercise 1.4
console.log(nums1.every((n) => n > 0));
// true
// Exercise 1.5
console.log(nums1.find((n) => n % 5 === 0));
// 15
// ------------------
// Cluster 2: Strings, includes/sort/reverse/slice
// ------------------
const fruits = ["banana", "apple", "cherry", "mango", "blueberry"];

// Exercise 2.1
console.log(fruits.includes("apple"));
// true
// Exercise 2.2
console.log(fruits.sort());
// [ apple, banana, blueberry, cherry, mango ]
// Exercise 2.3
console.log(fruits.slice(1, 4));
// [ apple, cherry, mango ]
// Exercise 2.4
console.log(fruits.reverse());
// [ 'blueberry', 'mango', 'cherry', 'apple', 'banana' ]
// Exercise 2.5
console.log(fruits.filter((fruit) => fruit.length > 5));
// [ banana, cherry, blueberry ]
// ------------------
// Cluster 3: Objects in array, map/filter/find
// ------------------
const users = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 18 },
  { name: "Charlie", age: 30 },
  { name: "Dana", age: 22 },
];

// Exercise 3.1
console.log(users.map((user) => user.name));
// Every name in users

// Exercise 3.2
console.log(users.filter((user) => user.age >= 21));
// All ages above 20

// Exercise 3.3
console.log(users.find((user) => user.name.startsWith("C")));
// First name that starts with the letter 'C'
// Exercise 3.4
console.log(users.some((user) => user.age <= 18));
// true if at least one user is under 18
// Exercise 3.5
console.log(users.every((user) => typeof user.name === "string"));
// true if all of the user names are strings
// ------------------
// Cluster 4: Combining map/filter/sort
// ------------------
const nums2 = [5, 1, 12, 8, 3, 7];

// Exercise 4.1
console.log(nums2.filter((n) => n > 5).map((n) => n * 2));
// n * 2 for all elements if bigger than 5
// Exercise 4.2
console.log(nums2.sort((a, b) => b - a).slice(0, 3));
// First 3 elements of the reverse sorted array
// Exercise 4.3
console.log(nums2.map((n) => n % 2 === 0).every((b) => b === true));
// true if all numbres are even
// Exercise 4.4
console.log(nums2.find((n) => n % 3 === 0));
// 12
// Exercise 4.5
console.log(nums2.some((n) => n < 0));
// false
// ------------------
// Cluster 5: Nested arrays (2D), flat, reduce
// ------------------
const matrix1 = [
  [1, 2],
  [3, 4],
  [5, 6],
];

// Exercise 5.1
console.log(matrix1.flat());
// Turns the matrix into an array

// Exercise 5.2
console.log(matrix1.map((row) => row.reduce((a, b) => a + b)));
// Sums every row
// Exercise 5.3
console.log(matrix1.flat().filter((n) => n % 2 === 0));
// returns an array containing only the even numbers
// Exercise 5.4
console.log(matrix1.flat().reduce((sum, n) => sum + n, 0));
// Sums the matrix
// Exercise 5.5
console.log(matrix1.some((row) => row.includes(4)));
// true if at least one row contains the number 4

// ------------------
// Cluster 6: Complex objects with filter/sort/map
// ------------------
const products = [
  { name: "Pen", price: 3 },
  { name: "Notebook", price: 8 },
  { name: "Backpack", price: 25 },
  { name: "Pencil", price: 1 },
];

// Exercise 6.1
console.log(products.filter((p) => p.price < 10));
// [
//   { name: 'Pen', price: 3 },
//   { name: 'Notebook', price: 8 },
//   { name: 'Pencil', price: 1 }
// ];

// Exercise 6.2
console.log(products.map((p) => p.name.toUpperCase()));
// [ "PEN", "NOTEBOOK", "BACKPACK", "PENCIL" ]
// Exercise 6.3
console.log(products.sort((a, b) => a.price - b.price));
// [
//   { name: 'Pencil', price: 1 }
//   { name: 'Pen', price: 3 },
//   { name: 'Notebook', price: 8 },
//   { name: 'Backpack', price: 25 },
// ];
// Exercise 6.4
console.log(products.find((p) => p.name === "Backpack"));
//   { name: 'Backpack', price: 25 },

// Exercise 6.5
console.log(products.every((p) => typeof p.name === "string"));
// true
// ------------------
// Cluster 7: Combined methods and chaining
// ------------------
const grades = [65, 75, 85, 95, 55];

// Exercise 7.1
console.log(grades.filter((g) => g >= 70).map((g) => g + 5));
// [ 80, 90, 100 ]
// Exercise 7.2
console.log(grades.map((g) => (g >= 60 ? "Pass" : "Fail")));
// [ Pass, Pass, Pass, Pass, Fail]
// Exercise 7.3
console.log(grades.reduce((a, b) => a + b, 0) / grades.length);
// 75 (sum of the array divided by the array's length)
// Exercise 7.4
console.log(grades.sort((a, b) => a - b).slice(-2));
// Last two elements of the sorted array
// Exercise 7.5
console.log(grades.every((g) => g >= 50));
// true if all numbers are bigger than 49
// ------------------
// Cluster 8: 2D arrays with advanced manipulation
// ------------------
const board = [
  ["X", "", "O"],
  ["O", "X", ""],
  ["", "", "X"],
];

// Exercise 8.1
console.log(board[0][2]);
// O
// Exercise 8.2
console.log(board.map((row) => row.includes("X")));
// [ true, true, true ]
// Exercise 8.3
console.log(board.flat().filter((cell) => cell === "X").length);
// 3
// Exercise 8.4
console.log(board[1].map((cell) => cell || "-").join(","));
// O,X,-
// Exercise 8.5
console.log(
  board.flat().every((cell) => cell === "X" || cell === "O" || cell === ""),
);
// true
// ------------------
// Cluster 9: Nested objects and complex filtering
// ------------------
const library = [
  { title: "1984", author: "Orwell", year: 1949 },
  { title: "Brave New World", author: "Huxley", year: 1932 },
  { title: "Fahrenheit 451", author: "Bradbury", year: 1953 },
];

// Exercise 9.1
console.log(library.filter((book) => book.year < 1950));
// [
//   { title: "1984", author: "Orwell", year: 1949 },
//   { title: "Brave New World", author: "Huxley", year: 1932 }
// ]
// Exercise 9.2
console.log(library.map((book) => `${book.title} by ${book.author}`));
// [
//     "1984 by Orwell",
//     "Brave New World by Huxley",
//     "Fahrenheit 451 by Bradbury"
// ]
// Exercise 9.3
console.log(library.find((book) => book.title.includes("451")));
// { title: "Fahrenheit 451", author: "Bradbury", year: 1953 }
// Exercise 9.4
console.log(library.some((book) => book.author === "Orwell"));
// true
// Exercise 9.5
console.log(library.sort((a, b) => a.year - b.year).map((b) => b.title));
// [
// "Brave New World",
// "1984",
// "Fahrenheit 451"
// ]
// ------------------
// Cluster 10: Complex combinations with chaining and conditionals
// ------------------
const data = [
  { name: "Max", scores: [90, 80, 100] },
  { name: "Zoe", scores: [70, 60, 50] },
  { name: "Leo", scores: [100, 100, 100] },
];

// Exercise 10.1
console.log(
  data.map((d) => d.scores.reduce((a, b) => a + b) / d.scores.length),
);
// [ 90, 60, 100 ] (Averages)

// Exercise 10.2
console.log(
  data.filter((d) => d.scores.every((s) => s >= 60)).map((d) => d.name),
);
// [ 'Max', 'Leo' ]

// Exercise 10.3
console.log(data.find((d) => d.name === "Zoe").scores.includes(50));
// true
// Exercise 10.4
console.log(data.some((d) => d.scores.some((s) => s < 60)));
// true
// Exercise 10.5
console.log(data.map((d) => ({ ...d, maxScore: Math.max(...d.scores) })));
// [
//   { name: 'Max', scores: [ 90, 80, 100 ], maxScore: 100 },
//   { name: 'Zoe', scores: [ 70, 60, 50 ], maxScore: 70 },
//   { name: 'Leo', scores: [ 100, 100, 100 ], maxScore: 100 }
// ]
// ------------------
// Cluster 11: Advanced objects and chaining
// ------------------
const people = [
  { name: "Alice", age: 32, city: "New York" },
  { name: "Bob", age: 25, city: "Los Angeles" },
  { name: "Charlie", age: 40, city: "Chicago" },
  { name: "Dana", age: 28, city: "New York" },
  { name: "Eli", age: 35, city: "Los Angeles" },
];

// Exercise 11.1
// Write code that logs the names of people older than 30, in alphabetical order.
// console.log(people.filter((d) => d.age > 30).map((d) => d.name)).sort();

// Exercise 11.2
// Write code that logs true if *all* people live in either New York or Los Angeles.
// console.log(people.every((d) => d.city === 'New York' || d.city === 'Los Angeles'));
// Exercise 11.3
// Write code that logs the names of people whose name starts with 'A' or 'E'.
// console.log(people.filter((d) => d.name.startsWith('A') || d.name.startsWith('E')).map((d) => d.name));

// Exercise 11.4
// Write code that logs the person object with the highest age.
console.log(people.reduce((oldest, current) => oldest.age < current.age ? current : oldest));

// Exercise 11.5
// Write code that logs an array of all unique cities (no duplicates).
// const cities = people.filter((d, i) => people.findIndex((p) => p.city === d.city) === i).map((d) => d.city);
// Exercise 11.6
// Write code that logs true if *any* person is exactly 40 years old.
// console.log(people.some((p) => p.age === 40));

// Exercise 11.7
// Write code that logs an array of names sorted by descending age.
// console.log(people.sort((a, b) => b.age - a.age).map((p) => p.name));

// Exercise 11.8
// Write code that logs an array of person objects, filtered to only those in New York, sorted by age.
// console.log(people.filter((p) => p.city === 'New York').sort((a, b) => a.age - b.age));

// Exercise 11.9
// Write code that logs an array of booleans indicating whether each person's name includes the letter 'a' (case-insensitive).
// console.log(people.map((d) => d.name.toLowerCase().includes('a')));

// Exercise 11.10
// Write code that logs the name of the first person from Chicago.
// console.log(people.find((d) => d.city === 'Chicago').name);

// ------------------
// Cluster 12: 2D arrays, nested structures, and complex transformations
// ------------------
const classrooms = [
  ["Anna", "Ben", "Charlie"],
  ["Diana", "Ethan"],
  ["Fiona", "George", "Hannah", "Ian"],
];

const scores = [
  [85, 90, 78],
  [88, 92],
  [70, 75, 80, 65],
];

// Exercise 12.1
// Write code that logs the total number of students across all classrooms.
// console.log(classrooms.map((row) => row.length).reduce((a, b) => a + b));

// Exercise 12.2
// Write code that logs the name of the longest-named student (across all classrooms).
// console.log(classrooms.flat().reduce((longest, current) => current.length > longest.length ? current : longest));

// Exercise 12.3
// Write code that logs an array of all student names that start with a vowel.
// const vowels = 'eyuioa'
// console.log(classrooms.flat().filter((name) => vowels.includes(name[0].toLowerCase())));

// Exercise 12.4
// Write code that logs an array of classroom sizes (number of students in each).
// console.log(classrooms.map((row) => row.length));

// Exercise 12.5
// Write code that logs the average score across all classrooms (flatten and calculate).
// console.log(scores.flat().reduce((a, b) => a + b) / scores.flat().length);

// Exercise 12.6
// Write code that logs the maximum score per classroom (array of 3 max values).
// console.log(scores.map((row) => row.reduce((highest, current) => highest < current ? current : highest)));

// Exercise 12.7
// Write code that logs true if *every* classroom has at least one student whose name contains the letter "n" (case-insensitive).
// console.log(classrooms.every((row) => row.some((name) => name.toLowerCase().includes('n'))));

// Exercise 12.8
// Write code that logs all scores above 80, sorted in descending order.
// console.log(scores.flat().filter((score) => score > 80).sort((a, b) => b - a));

// Exercise 12.9
// Write code that logs an array of students from classrooms that contain more than 3 students.
// console.log(classrooms.filter((row) => row.length > 3).flat());

// Exercise 12.10
// Write code that logs an array of `[name, score]` pairs (use same index from `classrooms` and `scores`, flatten them).
// console.log(classrooms.flat().map((name, index) => [name, scores.flat()[index]]));
