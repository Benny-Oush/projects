import sys

def print_board(board):
    sys.stdout.write("\033[2J\033[3J\033[H")
    
    print('\nTerminal Tic-Tac-Toe')
    print('\n    a | b | c ')

    for i in range(len(board)):
        print(f'{i + 1} | ', end='')
        for j in range(len(board[0])):
            if board[i][j]:
                print(f'{board[i][j]} | ', end='')
            else:
                print('  | ', end='') 
        print()

        if i != 2:
            print('  +---+---+---+')
            
def get_move(board):
    while True:
        try:
            move = input('\nEnter your move (e.g., a1): ')
            if not check_move(move, board):
                raise ValueError
            else:
                return move
        except ValueError:
            print('\n⚠️  Illegal move!')

def check_tie(board):
    for row in board:
        for cell in row:
            if not cell:
                return False
    return True

def check_win(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != '':
            return row[0]
            
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
            return board[0][col]
            
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
        return board[0][2]
        
    return False

def divide_move(move):
    row = int(move[1]) - 1
    column = ord(move[0]) - ord('a')
    return row, column

def check_move(move, board):
    if len(move) != 2:
        return False
    
    if move[0] in 'abc':
        if move[1].isdigit():
            if 4 > int(move[1]) > 0:
                row, column = divide_move(move)

                if not board[row][column]:
                    return True
                else:
                    return False
    return False

board = [
    ['', '', ''],
    ['', '', ''],
    ['', '', '']
]

print_board(board)

active_player = 'X'
waiting_player = 'O'

while True:
    print(f'\n{active_player}\'s move now')

    if not check_tie(board):
        move = get_move(board)
    else:
        print('\nBoard is full. Good game!\n')
        break
        
    row, column = divide_move(move)
    board[row][column] = active_player

    
    print_board(board)
    winner = check_win(board)

    if winner:
        print('\nWe have a winner! 🎉')
        print(f'\n{winner} wins!\n')
        break

    active_player, waiting_player = waiting_player, active_player
        
        