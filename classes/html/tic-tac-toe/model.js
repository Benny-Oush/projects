const readline = require('readline/promises');
const { stdin: input, stdout: output } = require('process');

const rl = readline.createInterface({ input, output });

function printBoard(board) {
    // מחיקת המסך בדומה לקוד הפייתון המקורי
    process.stdout.write("\x1b[2J\x1b[3J\x1b[H");
    
    console.log('\nTerminal Tic-Tac-Toe');
    console.log('\n    a | b | c ');

    for (let i = 0; i < board.length; i++) {
        let rowOutput = `${i + 1} | `;
        for (let j = 0; j < board[0].length; j++) {
            if (board[i][j]) {
                rowOutput += `${board[i][j]} | `;
            } else {
                rowOutput += '  | ';
            }
        }
        console.log(rowOutput);

        if (i !== 2) {
            console.log('  +---+---+---+');
        }
    }
}

async function getMove(board) {
    while (true) {
        const move = await rl.question('\nEnter your move (e.g., a1): ');
        if (!checkMove(move, board)) {
            console.log('\n⚠️  Illegal move!');
        } else {
            return move;
        }
    }
}

function checkTie(board) {
    for (const row of board) {
        for (const cell of row) {
            if (!cell) {
                return false;
            }
        }
    }
    return true;
}

function checkWin(board) {
    for (const row of board) {
        if (row[0] === row[1] && row[1] === row[2] && row[0] !== '') {
            return row[0];
        }
    }
        
    for (let col = 0; col < 3; col++) {
        if (board[0][col] === board[1][col] && board[1][col] === board[2][col] && board[0][col] !== '') {
            return board[0][col];
        }
    }
        
    if (board[0][0] === board[1][1] && board[1][1] === board[2][2] && board[0][0] !== '') {
        return board[0][0];
    }
    if (board[0][2] === board[1][1] && board[1][1] === board[2][0] && board[0][2] !== '') {
        return board[0][2];
    }
        
    return false;
}

function divideMove(move) {
    const row = parseInt(move[1]) - 1;
    const column = move.charCodeAt(0) - 'a'.charCodeAt(0);
    return [row, column];
}

function checkMove(move, board) {
    if (move.length !== 2) {
        return false;
    }
    
    if ('abc'.includes(move[0])) {
        if (!isNaN(move[1])) {
            const rowNum = parseInt(move[1]);
            if (rowNum > 0 && rowNum < 4) {
                const [row, column] = divideMove(move);

                if (!board[row][column]) {
                    return true;
                } else {
                    return false;
                }
            }
        }
    }
    return false;
}

async function playGame() {
    const board = [
        ['', '', ''],
        ['', '', ''],
        ['', '', '']
    ];

    printBoard(board);

    let activePlayer = 'X';
    let waitingPlayer = 'O';

    while (true) {
        console.log(`\n${activePlayer}'s move now`);
        let move;

        if (!checkTie(board)) {
            move = await getMove(board);
        } else {
            console.log('\nBoard is full. Good game!\n');
            break;
        }
        
        const [row, column] = divideMove(move);
        board[row][column] = activePlayer;

        printBoard(board);
        const winner = checkWin(board);

        if (winner) {
            console.log(`\nWe have a winner! 🎉\n\n${winner} wins!\n`);
            break;
        }

        // החלפת תורות
        [activePlayer, waitingPlayer] = [waitingPlayer, activePlayer];
    }
    
    rl.close(); // סגירת ממשק הקלט בסיום
}

// הפעלת המשחק
playGame();