/**
 * Lab: DOM Basics Exercises
 * Refer to index.html for the structure.
 */

// MISSION 0: Instant Updates (No Events) 🚀
// 1. Select the element with ID 'message' and change its text to "DOM is loaded!".
// 2. Select the element with ID 'status' and change its text to "Ready".
// 3. Select the element with ID 'style-me' and change its color to 'blue'.
// TODO: your code here
document.getElementById("message").innerText = "DOM is loaded!";

document.getElementById("status").innerText = "Ready";

document.getElementById("style-me").style.color = "blue";



// MISSION 1: The Dark Mode Toggle 🌓
// 1. Select the button with ID 'theme-toggle'.
// 2. Add a click event listener.
// 3. Inside the listener, toggle the class 'dark-mode' on the document.body.
// TODO: your code here
const themeToggle = document.getElementById('theme-toggle');

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});


// MISSION 2: The Counter 🔢
// 1. Select the counter span (#counter-value) and the two buttons (#increment-btn, #decrement-btn).
// 2. Create a variable 'count' initialized to 0.
// 3. When the increment button is clicked, increase 'count' and update the span's text.
// 4. When the decrement button is clicked, decrease 'count' and update the span's text.
// TODO: your code here
const counter = document.getElementById('counter-value');
const increment = document.getElementById('increment-btn');
const decrement = document.getElementById('decrement-btn');
let count = 0;
increment.addEventListener('click', () => {
    count++
    counter.innerText = count;
})
decrement.addEventListener('click', () => {
    count--
    counter.innerText = count;
})


// MISSION 3: Price Highlighting 🏷️
// 1. Select the highlight button (#highlight-btn) and ALL elements with class 'price-tag'.
// 2. When the button is clicked, loop through the price tags.
// 3. If the 'data-price' attribute is greater than 100:
//    - Change the text color to 'red'.
//    - Change the font weight to 'bold'.
// TODO: your code here
const highlight = document.getElementById('highlight-btn');
const priceTags = document.querySelectorAll('.price-tag');
highlight.addEventListener('click', () => {
    priceTags.forEach(tag =>  {
        const price = Number(tag.dataset.price);
        if (price > 100) {
            tag.style.color = 'red';
            tag.style.fontWeight = 'bold';
            }
    });
})
