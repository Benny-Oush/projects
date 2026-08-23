let currentDiv = 0;
const divs = document.querySelectorAll(".box");
const totalBoxes = divs.length;

function activateBox(newIndex, previousIndex) {
  divs[previousIndex].classList.remove("active");
  divs[newIndex].classList.add("active");
}

const right = document.getElementById("right").addEventListener("click", () => {
  const prev = currentDiv;
  currentDiv = (currentDiv + 1) % totalBoxes;
  activateBox(currentDiv, prev);
});

const left = document.getElementById("left").addEventListener("click", () => {
  const prev = currentDiv;
  currentDiv = (currentDiv - 1 + totalBoxes) % totalBoxes;
  activateBox(currentDiv, prev);
});
