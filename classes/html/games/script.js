document.getElementById("cont").addEventListener("click", (event) => {
  switch (event.target.id) {
    case "minesweeper":
      location.href = "./minesweeper/index.html";
      break
    case "missing-number":
      location.href = "./missing number/index.html";
      break
    case "rps":
      location.href = "./rps/index.html";
      break
    case "cards":
      location.href = "./cards/index.html"
      break
    case "snake":
      location.href = './snake/index.html'
  }
});
