const SPEED = 170; // Milliseconds
const WIDTH = 16;
const HEIGHT = 12;
const highScoreDisplay = document.getElementById("top-score")
const cont = document.getElementById("cont");
const scoreText = document.getElementById("score");
const statusText = document.getElementById("status");
document.getElementById('reset-top-score-button').addEventListener('click', () => {
    localStorage.removeItem('topScore');
    topScore = 0;
    highScoreDisplay.textContent = `Top: ${topScore}`;
});

let score = 0;
let topScore = localStorage.getItem('topScore') || 0;

let prevTopScore = topScore;

let lossAnimationClock;

let clock;
let nextDir = [];
let snake,
  apple,
  dir,
  on = false;

let ateApple = false;

const sameCor = (c1, c2) => c1[0] === c2[0] && c1[1] === c2[1];

function dropApple() {
  let inSnake = true;
  while (inSnake) {
    apple = [
      Math.floor(Math.random() * HEIGHT),
      Math.floor(Math.random() * WIDTH),
    ];
    inSnake = false;
    for (let k = 0; k < snake.length; k++) {
      if (sameCor(apple, snake[k])) {
        inSnake = true;
        break;
      }
    }
  }
}

function render() {
  const boardSquares = document.getElementsByClassName("board");
  for (let k = 0; k < boardSquares.length; k++) {
    boardSquares[k].classList.remove("head");
    boardSquares[k].classList.remove("body");
    boardSquares[k].classList.remove("apple");
  }
  const [appleI, appleJ] = apple;
  const appleSquare = document.getElementById(`s_${appleI}_${appleJ}`);
  appleSquare.classList.add("apple");
  const [headI, headJ] = snake[0];
  const headSquare = document.getElementById(`s_${headI}_${headJ}`);
  headSquare.classList.add("head");
  for (let k = 1; k < snake.length; k++) {
    const [bodyI, bodyJ] = snake[k];
    const bodySquare = document.getElementById(`s_${bodyI}_${bodyJ}`);
    bodySquare.classList.add("body");
  }
  scoreText.innerText = `Score: ${score}`;
  highScoreDisplay.textContent = `Top: ${topScore}`;
}

function renderloss() {
  statusText.style.color = "red";
  statusText.innerText = "GAME OVER ☹️";
  
  if (prevTopScore < topScore) {
    highScoreDisplay.innerText = `NEW TOP SCORE!\n${topScore}`
  }

  let k = 0;
  let lossAnimationClock = setInterval(() => {
    if (k >= snake.length) {
      clearInterval(lossAnimationClock);
      lossAnimationClock = undefined;
      return;
    }

    const [headI, headJ] = snake[k];
    const headSquare = document.getElementById(`s_${headI}_${headJ}`);
    headSquare.classList.add("hit");
    headSquare.classList.remove("body", "head");
    k++;
  }, SPEED / 2);
}

function renderWin() {
  console.log("You win");
}

function startClock() {
  if (clock === undefined) {
    clock = setInterval(snakeMove, SPEED);
  }
}

function stopClock() {
  if (clock !== undefined) {
    clearInterval(clock);
    clock = undefined;
  }
}

function startGame() {
  if (lossAnimationClock !== undefined) {
    clearInterval(lossAnimationClock);
    lossAnimationClock = undefined;
  }
  const headStartX = Math.floor(WIDTH / 2) - 1;
  const headStartY = Math.floor(HEIGHT / 2) - 1;
  snake = [[headStartY, headStartX]];
  for (let k = 0; k < 2; k++) {
    const [prevY, prevX] = snake[k];
    const nextY = prevY;
    const nextX = prevX - 1;

    if (nextX < 0) {
      break;
    }
    snake.push([nextY, nextX]);
  }
  prevTopScore = topScore;
  dropApple();
  dir = [0, 1];
  score = 0;
  on = true;
  createBoard();
  statusText.style.color = "rgb(2, 2, 192)";
  statusText.innerText = "GOOD LUCK!";
  render();
  startClock();
}

function changeDir(dirName) {
  let newDir;
  switch (dirName) {
    case "RIGHT":
      newDir = [0, 1];
      break;
    case "LEFT":
      newDir = [0, -1];
      break;
    case "UP":
      newDir = [-1, 0];
      break;
    case "DOWN":
      newDir = [1, 0];
      break;
    default:
      return;
  }
  let currentDir = dir;
  if (nextDir.length) {
    currentDir = nextDir[nextDir.length - 1];
  }
  if (currentDir[0] + newDir[0] !== 0 || currentDir[1] + newDir[1] !== 0) {
    nextDir.push(newDir);
  }
}

function checkLoss() {
  let loss = false;
  for (let k = 4; k < snake.length; k++) {
    if (sameCor(snake[0], snake[k])) {
      loss = true;
      break;
    }
  }
  let [headY, headX] = snake[0];
  if (headY === -1 || headY === HEIGHT || headX === -1 || headX === WIDTH) {
    loss = true;
  }
  if (!loss) {
    return;
  }
  stopClock();
  on = false;
  renderloss();
  return true;
}

function checkWin() {
  if (snake.length === WIDTH * HEIGHT - 1) {
    renderWin();
    stopClock();
    on = false;
    return true;
  }
  return false;
}

function snakeMove() {
  if (!on) {
    return;
  }

  if (nextDir.length) {
    dir = nextDir.shift();
  }

  let [headY, headX] = snake[0];
  const [dirY, dirX] = dir;
  headY += dirY;
  headX += dirX;
  snake.unshift([headY, headX]);
  if (!ateApple) {
    snake.pop();
  } else {
    ateApple = false;
  }
  if (sameCor(snake[0], apple)) {
    ateApple = true;
    score += 25;
    statusText.innerText = "YUMMY! 🤤";
    dropApple();
    updateHighScore()
  }

  render();
  
  const hasLost = checkLoss();
  const hasWon = checkWin();
  if (hasLost || hasWon) {
    return;
  }
}

function createBoard() {
  cont.innerHTML = "";
  for (let i = -1; i <= HEIGHT; i++) {
    const row = document.createElement("div");
    row.classList.add("row");
    for (let j = -1; j <= WIDTH; j++) {
      const square = document.createElement("div");
      if (i === -1 || i === HEIGHT || j === -1 || j === WIDTH) {
        square.classList.add("border");
      } else {
        square.classList.add("board");
      }
      square.id = `s_${i}_${j}`;
      row.appendChild(square);
    }
    cont.appendChild(row);
  }
}

function updateHighScore() {
    if (score > topScore) {
        topScore = score;
        localStorage.setItem('topScore', topScore);
        highScoreDisplay.textContent = `Top: ${topScore}`;
    }
}

document.addEventListener("keydown", (event) => {
  if (!on && event.key == "Enter") {
    startGame();
  } else if (on && event.key.startsWith("Arrow")) {
    event.preventDefault();
    const newDirName = event.key.substring(5).toUpperCase();
    changeDir(newDirName);
  }
});

createBoard();
