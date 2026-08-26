const difficultySettings = {
  easy: { rows: 10, cols: 10, mines: 12 },
  medium: { rows: 12, cols: 12, mines: 25 },
  hard: { rows: 15, cols: 15, mines: 40 },
};

const boardUI = document.getElementById("board");
const difficultySelect = document.getElementById("difficulty");
const resetButton = document.getElementById("reset");
const statusUI = document.getElementById("status");

function setupBoardUI(config) {
  boardUI.innerHTML = "";
  boardUI.style.display = "grid";
  boardUI.style.gridTemplateColumns = `repeat(${config.cols}, 1fr)`;
  boardUI.style.gridTemplateRows = `repeat(${config.rows}, 1fr)`;

  for (let r = 0; r < config.rows; r++) {
    for (let c = 0; c < config.cols; c++) {
      const cellDiv = document.createElement("div");
      cellDiv.className = "cell";

      cellDiv.dataset.index = r * config.cols + c;

      cellDiv.addEventListener("click", () => {
        handleCellClick(r, c);
      });

      cellDiv.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        toggleFlag(r, c);
      });

      boardUI.appendChild(cellDiv);
    }
  }
}

function render() {
  const cells = boardUI.children;
  const len = CURRENT_SIZE;

  for (let r = 0; r < len; r++) {
    for (let c = 0; c < len; c++) {
      const index = r * len + c;
      const cellDiv = cells[index];

      cellDiv.className = "cell";
      cellDiv.innerHTML = "";

      const isRevealed = VISIBILITY[r][c] === 1;
      const isMine = GRID[r][c] === 1;
      const isFlagged = FLAGS[r][c] === 1;
      const neighborMines = NUMBER_OF_MINES[r][c];

      if (isRevealed) {
        cellDiv.classList.add("revealed");

        if (isMine) {
          cellDiv.classList.add("mine");
          cellDiv.innerHTML = "💣";
        } else if (isFlagged) {
          cellDiv.innerHTML = "❌";
        } else if (neighborMines > 0) {
          cellDiv.innerHTML = neighborMines;
          cellDiv.dataset.num = neighborMines;
        }
      } else if (isFlagged) {
        cellDiv.innerHTML = "🚩";
      }
    }
  }
}

function updateStatusMessage(message) {
  if (statusUI) {
    statusUI.innerText = message;
  }
}

difficultySelect.addEventListener("change", startNewGame);
resetButton.addEventListener("click", startNewGame);

function startNewGame() {
  const config = difficultySettings[difficultySelect.value];
  create_grid(config.rows, config.mines);
  setupBoardUI(config);
  updateStatusMessage("Good Luck!");
  render();
}

startNewGame();
