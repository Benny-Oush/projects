const startButton = document.getElementById("start");
startButton.addEventListener("click", () => {
  if (on) {
    resetGame();
    return;
  }
  startButton.innerText = "RESET";
  startGame();
});
const drawButton = document.getElementById("draw");
drawButton.addEventListener("click", () => {
  draw();
});
drawButton.disabled = true;

const humanContainer = document.getElementById("human-img");
const botContainer = document.getElementById("bot-img");
const humanScoreText = document.getElementById("human-score");
const botScoreText = document.getElementById("bot-score");
const statusText = document.getElementById("status");

async function getDeck() {
  if (!on || cardsRemaining > 0) {
    return;
  }
  const response = await fetch(
    "https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1",
  );
  const result = await response.json();
  console.log(result);
  return result;
}

let deckID, cardsRemaining, humanScore, botScore, currentCards;
let on = false;
let cardsToDraw = 6; // Tie
let tieCount = 0;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function startGame() {
  if (on) {
    return;
  }
  humanScore = 0;
  botScore = 0;
  tieCount = 0;
  on = true;
  const deck = await getDeck();
  deckID = deck["deck_id"];
  cardsRemaining = deck["remaining"];
  statusText.innerText = "War launched. Draw your first card";
  startButton.innerText = "RESET";
  humanScoreText.innerText = "0";
  botScoreText.innerText = "0";
  drawButton.disabled = false;
}

async function draw() {
  drawButton.disabled = true;
  if (cardsRemaining <= 0 || !on) {
    return;
  }
  let roundWinner;
  await newCards();
  const [humanValue, botValue] = getValues();
  console.log("Human:", humanValue, "Bot:", botValue);

  if (humanValue === botValue) {
    tieCount++;
    if (cardsRemaining <= 0) {
      statusText.innerText = "Not enough cards!";
      await sleep(1000);
      resetGame();
      renderWin();
      return;
    }
    cardsToDraw = cardsRemaining >= 6 ? 6 : cardsRemaining;
    const response = await fetch(
      `https://deckofcardsapi.com/api/deck/${deckID}/draw/?count=${cardsToDraw}`,
    );
    const result = await response.json();
    cardsRemaining = result.remaining;
    if (cardsRemaining <= 0) {
      statusText.innerText = "Not enough cards!";
      await sleep(1000);
      resetGame();
      renderWin();
      return;
    }
    await sleep(1000)
    statusText.innerText = "TIE!";
    drawButton.disabled = false;
    humanContainer.innerHTML = `<img src="./assets/images.jpg">`
    botContainer.innerHTML = `<img src="./assets/images.jpg">`
    return;
  }
  if (humanValue > botValue) {
    roundWinner = "human";
  } else {
    roundWinner = "bot";
  }

  for (let i = 0; i < tieCount; i++) {
    if (roundWinner === "human") {
      humanScore += cardsToDraw;
    } else if (roundWinner === "bot") {
      botScore += cardsToDraw;
    }
  }
  tieCount = 0;
  cardsToDraw = 6;

  if (roundWinner === "human") {
    humanScore++;
  } else if (roundWinner === "bot") {
    botScore++;
  }
  displayScores();
  statusText.innerText = `${roundWinner.toUpperCase()} WINS!
  Remaining cards: ${cardsRemaining}`;
  if (cardsRemaining === 0) {
    resetGame();
    renderWin();
    drawButton.disabled = true;
    return;
  }
  drawButton.disabled = false;
}

async function getCards() {
  const response = await fetch(
    `https://deckofcardsapi.com/api/deck/${deckID}/draw/?count=2`,
  );
  const result = await response.json();
  cardsRemaining = result.remaining;
  return result;
}

async function displayCards() {
  const humanImg = document.createElement("img");
  humanImg.src = currentCards.cards[0].image;
  humanContainer.innerHTML = "";
  humanContainer.appendChild(humanImg);
  const botImg = document.createElement("img");
  botImg.src = currentCards.cards[1].image;
  botContainer.innerHTML = "";
  botContainer.appendChild(botImg);
}

async function newCards() {
  currentCards = await getCards();
  displayCards();
}

async function displayScores() {
  await sleep(500);
  humanScoreText.innerText = humanScore;
  botScoreText.innerText = botScore;
}

function getValues() {
  let humanValue = currentCards.cards[0].value;
  let botValue = currentCards.cards[1].value;
  return [convertValue(humanValue), convertValue(botValue)];
}

function convertValue(value) {
  switch (value) {
    case "JACK":
      return +11;
    case "QUEEN":
      return +12;
    case "KING":
      return +13;
    case "ACE":
      return +14;
    default:
      return +value;
  }
}

function resetGame() {
  startButton.innerText = "Start War";
  humanContainer.innerHTML = "";
  statusText.innerText = " ";
  botContainer.innerHTML = "";
  deckID = 0;
  humanScoreText.innerText = "0";
  botScoreText.innerText = "0";
  on = false;
  cardsToDraw = 6;
  currentCards = [];
  tieCount = 0;
  humanValue = 0;
  botValue = 0;
  cardsRemaining = 0;
  drawButton.disabled = true;
}

async function renderWin() {
  if (humanScore === botScore) {
    await sleep(1000);
    statusText.innerText = "THE WAR ENDED IN A TIE!";
    return;
  }
  const winner = humanScore > botScore ? "HUMAN" : "BOT";
  statusText.innerText = `${winner} WON THE WAR!`;
}
