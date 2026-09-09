const scoretext = document.getElementById("score");
let topScore = localStorage.getItem("topScore") || 0;
const topScoreText = document.getElementById("top-score");
const statusText = document.getElementById("status");
const startButton = document.getElementById("start");
const countDownText = document.getElementById("count-down");
document.getElementById("reset").addEventListener("click", () => {
  localStorage.removeItem("topScore");
  topScore = 0;
  topScoreText.innerText = "Top score: 0";
});
let score = 0;
let hasLostLastRound = false;
let pressed;
let pressedIdx = [];
const numberDivs = document.getElementsByClassName("num");
const cells = document.getElementsByClassName("cell");
let time;
let timeLeft;

topScoreText.innerText = `Top score: ${topScore}`;

let on = false;
startButton.addEventListener("click", () => {
  statusText.innerText = "Find the missing number";
  scoretext.innerText = "Score: 0";
  countdownTime();
});

function renderWin() {
  statusText.innerText = "YOU WON 🎉";
  scoretext.innerText = `Score: ${score}`;
  topScoreText.innerText = `Top score: ${topScore}`;
}

function renderLoss(timeUp = false) {
  if (timeUp) {
    statusText.innerText = "TIME IS UP ☹️";
  } else {
    statusText.innerText = "YOU LOST ☹️";
  }
  scoretext.innerText = `Score: ${score}`;
  topScoreText.innerText = `Top score: ${topScore}`;
  for (let i = 0; i < cells.length; i++) {
    if (cells[i].innerText == pressed) {
      cells[i].classList.add("pressed");
      pressedIdx.push(i);
    }
  }
}

let missingNumber;

function addListeners() {
  for (let i = 0; i < numberDivs.length; i++) {
    numberDivs[i].id = `_${i + 1}`;
    numberDivs[i].addEventListener("click", (event) => {
      if (!on) {
        return;
      }
      stopClock();
      on = false;
      pressed = parseInt(event.currentTarget.id.slice(1), 10);
      const hasWon = pressed === missingNumber;
      if (hasWon) {
        hasLostLastRound = false;
        score = time / 10;
        if (topScore < score) {
          topScore = score;
          localStorage.setItem("topScore", topScore);
        }
        renderWin();
      } else {
        hasLostLastRound = true;
        renderLoss();
      }
      score = 0;
      pressed = "";
    });
  }
}

function countdownTime() {
  if (on) {
    return;
  }
  timeLeft = 3;
  const countdownTimer = setInterval(
    (function tick() {
      if (timeLeft > 0) {
        countDownText.innerText = timeLeft;
        timeLeft--;
      } else {
        clearInterval(countdownTimer);
        countDownText.innerText = "10.00";
        startRound();
      }
      return tick;
    })(),
    1000,
  );
}

function startRound() {
  if (on) {
    return;
  }
  if (hasLostLastRound) {
    for (let i = 0; i < pressedIdx.length; i++) {
      cells[pressedIdx[i]].classList.remove("pressed");
    }
  }
  startClock();
  on = true;
  const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9];
  missingNumber = nums.splice(Math.floor(Math.random() * 9), 1)[0];
  const duplicated = [...nums, ...nums];
  for (let i = 0; i < cells.length; i++) {
    let randomCellIdx = Math.floor(Math.random() * duplicated.length);
    cells[i].innerText = duplicated.splice(randomCellIdx, 1)[0];
  }
  pressedIdx = [];
}

function countDown() {
  if (time <= 0) {
    stopClock();
    on = false;
    renderLoss((timeUp = true));
    return;
  }
  time -= 10;
  countDownText.innerText = (time / 1000).toFixed(2);
}

function startClock() {
  if (on) {
    return;
  }
  time = 5000;
  clock = setInterval(countDown, 10);
}

function stopClock() {
  clearInterval(clock);
}

addListeners();
