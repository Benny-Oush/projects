const height = document.getElementById("height");
const width = document.getElementById("width");
const borderWidth = document.getElementById("border-width");
const text = document.getElementById("text");
const color = document.getElementById("color");
const divsNum = document.getElementById("divs-num");
const container = document.getElementById("container");

const targetContainer = document.getElementById("container");

const button = document
  .getElementById("create-divs")
  .addEventListener("click", () => {
    for (let i = 0; i < divsNum.value; i++) {
      container.style.display = "flex";
      const box = document.createElement("div");
      box.style.width = width.value + "px";
      box.style.height = height.value + "px";
      box.style.border = borderWidth.value + "px" + " black solid";
      box.style.borderRadius = "20px";
      box.textContent = text.value;
      box.style.display = "flex";
      box.style.alignItems = "center";
      box.style.justifyContent = "center";
      box.style.backgroundColor = color.value;

      container.appendChild(box);
    }
    targetContainer.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  });
