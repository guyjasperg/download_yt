import os
import time

def clear_screen():
    """
    Clears the console screen.
    Works for Windows, macOS, and Linux.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    
def print_board(board):
    """
    Clears the screen and prints the current state of the board.
    """
    clear_screen()
    print("Tic Tac Toe")
    print()
    for row in range(len(board)):
        print(" | ".join(board[row]))
        if row < len(board) - 1:
            print("-" * 5)

def check_winner(board):
    """
    Checks if there is a winner or if the game is a draw.
    Returns 'X', 'O', 'Draw', or None.
    """
    # Check rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != " ":
            return board[0][i]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != " ":
        return board[0][2]

    # Check for draw
    if all(cell != " " for row in board for cell in row):
        return "Draw"

    return None

def tic_tac_toe():
    """
    Main function to play the game.
    """
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"

    print("Welcome to Tic Tac Toe!")
    print_board(board)

    while True:
        # Get player input
        print(f"Player {current_player}'s turn.")
        try:
            row, col = map(int, input("Enter row and column (0-2, space-separated): ").split())
        except ValueError:
            print("Invalid input. Please enter two numbers separated by a space.")
            continue

        # Validate input
        if not (0 <= row < 3 and 0 <= col < 3):
            print("Invalid position. Choose a number between 0 and 2.")
            continue
        if board[row][col] != " ":
            print("Position already taken. Choose another.")
            continue

        # Make the move
        board[row][col] = current_player
        print_board(board)

        # Check for a winner
        winner = check_winner(board)
        if winner:
            if winner == "Draw":
                print("The game is a draw!")
            else:
                print(f"Player {winner} wins!")
            break

        # Switch player
        current_player = "O" if current_player == "X" else "X"

# Run the game
if __name__ == "__main__":
    tic_tac_toe()
