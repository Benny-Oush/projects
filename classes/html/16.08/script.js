const paragraph = document.getElementById("myParagraph");
const divs = document.getElementsByClassName("myDivs");
const buttonBigger = document.querySelector("#bigger");
const buttonSmaller = document.querySelector("#smaller");
document
  .getElementById("colorPicker")
  .addEventListener("input", function (event) {
    for (const div of divs) {
      div.style.backgroundColor = event.target.value;
    }
  });

let currentScale = 1;

buttonBigger.addEventListener("click", function (event) {
  if (currentScale <= 1.25) {
    currentScale += 0.05;
    for (const div of divs) {
      div.style.transform = `scale(${currentScale})`;
    }
  }
  const red = Math.floor(Math.random() * 256);
  const green = Math.floor(Math.random() * 256);
  const blue = Math.floor(Math.random() * 256);
  const color = `rgb(${red}, ${green}, ${blue})`;
  for (const div of divs) {
    div.style.backgroundColor = `${color}`;
  }

  console.log(currentScale);
});

buttonSmaller.addEventListener("click", function () {
  if (currentScale >= 0.45) {
    currentScale -= 0.05;
    for (const div of divs) {
      div.style.transform = `scale(${currentScale})`;
    }
  }
  const red = Math.floor(Math.random() * 256);
  const green = Math.floor(Math.random() * 256);
  const blue = Math.floor(Math.random() * 256);
  const color = `rgb(${red}, ${green}, ${blue})`;
  for (const div of divs) {
    div.style.backgroundColor = `${color}`;
  }

  console.log(currentScale);
});
