const botDiv = document.getElementById("bot");
const userDiv = document.getElementById("user");
const roundH = document.getElementById("round");
const statusH = document.getElementById("status");
const scoreH = document.getElementById("score");
const paper = document.getElementById("paper");
const rock = document.getElementById("rock");
const scissors = document.getElementById("scissors");
const button = document.getElementById("next-round");

rock.addEventListener("click", () => {
  if (gameIsOn) {
    userChoose(ROCK);
  }
});
paper.addEventListener("click", () => {
  if (gameIsOn) {
    userChoose(PAPER);
  }
});

scissors.addEventListener("click", () => {
  if (gameIsOn) {
    userChoose(SCISSORS);
  }
});

button.addEventListener("click", () => {
  nextRound();
  button.style.display = "none";
});

const ROCK = 0;
const PAPER = 1;
const SCISSORS = 2;

let userChoice, botChoice;
let userScore = 0,
  botScore = 0;
let roundCount = 0;
let gameIsOn = false;
let stat = "";

const names = ["rock", "paper", "scissors"];

function render() {
  roundH.innerText = `Round ${roundCount}`;
  statusH.innerText = stat;
  console.log(
    `User chose: ${names[userChoice]}\nBot chose: ${names[botChoice]}`,
  );

  scoreH.innerText = `${userScore} : ${botScore}`;
}

function userChoose(choice) {
  gameIsOn = false;
  userChoice = choice;
  botChoice = Math.floor(Math.random() * 3);
  if (userChoice === botChoice) {
    stat = "Tie";
  } else if (userChoice === (botChoice + 1) % 3) {
    stat = "User wins";
    userScore++;
  } else {
    stat = "Bot wins";
    botScore++;
  }
  userDiv.style.backgroundImage = `url('./assets/${names[userChoice]}.png')`;
  botDiv.style.backgroundImage = `url('./assets/${names[botChoice]}.png')`;
  button.style.display = "block";
  render();
}

function nextRound() {
  if (gameIsOn) {
    return;
  }
  roundCount++;
  stat = "Make your choice";
  gameIsOn = true;
  userDiv.style.backgroundImage = "url(./assets/user.png)";
  botDiv.style.backgroundImage = "url(./assets/bot.png)";

  render();
}

nextRound();
