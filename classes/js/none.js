for (let i = 1; i <= 10; i++)
    if (i % 3 === 0){
        console.log(i)
    } else {
        console.log(i + ' the number is odd')
    }
function ConvertCelsiusToFahrenheit(celsius) {
    let fahrenheit = celsius * 1.8 + 32;
    return fahrenheit;
}
console.log(ConvertCelsiusToFahrenheit(0))
console.log(ConvertCelsiusToFahrenheit(30))
console.log(ConvertCelsiusToFahrenheit(100))
function IsHot(fahrenheit) {
  let celsius = (fahrenheit - 32) / 1.8;
  return celsius;
}
for (let i = Math.floor(Math.random() * 101); i <= 100; i += 13) {
  let celsius = IsHot(i);
  let fixedcelsius = celsius.toFixed(2);
  if (celsius >= 28) {
    console.log("temperture: " + fixedcelsius + '\n' + "it is hot");
  } else if (celsius < 28 && celsius >= 10) {
    console.log("temperture: " + fixedcelsius + '\n' + "it is comfortable");
  } else {
    console.log("temperture: " + fixedcelsius + '\n' + "it is cold");
  }
}
