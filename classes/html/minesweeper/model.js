let GRID = [];
let VISIBILITY = [];
let NUMBER_OF_MINES = [];
let FLAGS = [];

let GAME_ON = false;
let HAS_LOST = false;

let IS_FIRST_CLICK = true;
let CURRENT_SIZE = 0;
let CURRENT_MINES = 0;


function handleCellClick(r, c) {
  if (!GAME_ON || HAS_LOST || VISIBILITY[r][c] === 1) {
    return;
  }

  if (FLAGS[r][c] === 1) {
    return;
  }

  if (IS_FIRST_CLICK) {
    placeMinesAndNumbers(r, c);
    IS_FIRST_CLICK = false;
  }

  if (GRID[r][c] === 1) {
    HAS_LOST = true;
    GAME_ON = false;
    VISIBILITY[r][c] = 1;
    revealMines();
    updateStatusMessage("Game Over! ☹️");
    return;
  }

  const idx = r * CURRENT_SIZE + c;
  checkSurroundings(idx);

  if (checkForWin(GRID, VISIBILITY)) {
    GAME_ON = false;
    updateStatusMessage("You Win! 🎉");
  }
  render()
}

function toggleFlag(r, c) {
  if (!GAME_ON || HAS_LOST) {
    return;
  }

  if (VISIBILITY[r][c] === 0) {
    FLAGS[r][c] = FLAGS[r][c] === 0 ? 1 : 0;
  }
  render()
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function revealMines() {
  for (let i = 0; i < GRID.length; i++) {
    for (let j = 0; j < GRID.length; j++) {
      if ((GRID[i][j] === 1 && FLAGS[i][j] === 0) || (GRID[i][j] === 0 && FLAGS[i][j] === 1)) {
        VISIBILITY[i][j] = 1;
        render();
        await sleep(100); 
      }
    }
  }
}


function create_grid(size, numOfMines) {
  GRID = [];
  FLAGS = [];
  VISIBILITY = [];
  NUMBER_OF_MINES = [];

  GAME_ON = true;
  HAS_LOST = false;
  IS_FIRST_CLICK = true;

  CURRENT_SIZE = size;
  CURRENT_MINES = numOfMines;

  for (let i = 0; i < size; i++) {
    GRID.push([]);
    VISIBILITY.push([]);
    NUMBER_OF_MINES.push([]);
    FLAGS.push([]);

    for (let j = 0; j < size; j++) {
      GRID[i].push(0);
      VISIBILITY[i].push(0);
      NUMBER_OF_MINES[i].push(0);
      FLAGS[i].push(0);
    }
  }
}

function placeMinesAndNumbers(firstR, firstC) {
  let minesPlaced = 0;

  while (minesPlaced < CURRENT_MINES) {
    const r = Math.floor(Math.random() * CURRENT_SIZE);
    const c = Math.floor(Math.random() * CURRENT_SIZE);

    if (Math.abs(r - firstR) <= 1 && Math.abs(c - firstC) <= 1) {
      continue;
    }

    if (GRID[r][c] === 1) {
      continue;
    }

    GRID[r][c] = 1;
    minesPlaced++;
  }

  const len = CURRENT_SIZE;
  for (let i = 0; i < len; i++) {
    for (let j = 0; j < len; j++) {
      let sum = 0;
      for (let di = -1; di <= 1; di++) {
        for (let dj = -1; dj <= 1; dj++) {
          if (di === 0 && dj === 0) continue;

          const newI = i + di;
          const newJ = j + dj;

          if (newI >= 0 && newI < len && newJ >= 0 && newJ < len) {
            if (GRID[newI][newJ] === 1) {
              sum++;
            }
          }
        }
      }
      NUMBER_OF_MINES[i][j] = sum;
    }
  }
}

function write_numbers() {
  const len = GRID.length;
  for (let i = 0; i < len; i++) {
    NUMBER_OF_MINES.push([]);
    for (let j = 0; j < len; j++) {
      let sum = 0;
      for (let di = -1; di <= 1; di++) {
        for (let dj = -1; dj <= 1; dj++) {
          if (di === 0 && dj === 0) {
            continue;
          }
          const newI = i + di;
          const newJ = j + dj;
          if (newI < 0 || newI >= len || newJ < 0 || newJ >= len) {
            continue;
          }
          if (GRID[newI][newJ] === 1) {
            sum++;
          }
        }
      }
      NUMBER_OF_MINES[i].push(sum);
    }
  }
}

async function checkSurroundings(idx) {
  const len = GRID[0].length;
  const startR = Math.floor(idx / len);
  const startC = idx % len;

  VISIBILITY[startR][startC] = 1;

  if (GRID[startR][startC] === 1 || NUMBER_OF_MINES[startR][startC] > 0) {
    return;
  }
  let empties = [idx];
  let visited = [];
  visited.push(idx);

  while (empties.length > 0) {
    const currentIdx = empties.pop();
    const r = Math.floor(currentIdx / len);
    const c = currentIdx % len;

    for (let di = -1; di <= 1; di++) {
      for (let dj = -1; dj <= 1; dj++) {
        if (di === 0 && dj === 0) {
          continue;
        }
        const newI = r + di;
        const newJ = c + dj;
        const newIdx = newI * len + newJ;
        if (newI < 0 || newI >= len || newJ < 0 || newJ >= len) {
          continue;
        }
        if (VISIBILITY[newI][newJ] == 0) {
          visited.push(newIdx);
          VISIBILITY[newI][newJ] = 1;
          render()
          await sleep(2)
          if (GRID[newI][newJ] === 0 && NUMBER_OF_MINES[newI][newJ] === 0) {
            empties.push(newIdx);
          }
        }
      }
    }
  }
}

function checkForWin(GRID, VISIBILITY) {
  for (let i = 0; i < GRID.length; i++) {
    for (let j = 0; j < GRID.length; j++) {
      if (GRID[i][j] === 0 && VISIBILITY[i][j] === 0) {
        return false;
      }
    }
  }
  return true;
}
