import tkinter as tk
import chess
from chess_engine import find_best_move  # Import the chess engine's best move function

# Set up initial chess board
board = chess.Board()

# Create main window for the Tkinter UI
root = tk.Tk()
root.title("Chess - One Player Game (vs AI)")

# Function to update the board on the interface
def update_board():
    try:
        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)  # Corrected mapping
                piece = board.piece_at(square)
                label = labels[i][j]

                # Set the background of all squares to grey
                label.config(bg='grey')

                # Display piece symbol with appropriate color (white/black)
                if piece:
                    piece_color = 'black' if piece.color == chess.WHITE else 'white'
                    label.config(text=piece.symbol(), fg=piece_color, font=("Arial", font_size, "bold"))
                else:
                    label.config(text="", bg=label.cget("bg"))
    except Exception as e:
        print(f"Error updating board: {e}")

# Function to handle player's move
def player_move(i, j):
    global selected_square, turn

    try:
        square = chess.square(j, 7 - i)
        current_square = chess.SQUARE_NAMES[square]

        # Debugging statement to see the move being made
        print(f"Player move: {selected_square} to {current_square}")

        if selected_square is None:
            piece = board.piece_at(square)

            # Check if a valid piece is selected for the human's turn
            if piece and piece.color == board.turn:  # Ensure it's the correct turn
                selected_square = current_square
                print(f"Selected piece: {selected_square}")
        else:
            # Check if the move is the same square
            if selected_square == current_square:
                print(f"Invalid move: {selected_square} to {current_square} (same square)")
                selected_square = None  # Deselect piece after invalid move
                update_board()  # Update board to reflect deselection
                return

            move = chess.Move.from_uci(f'{selected_square}{current_square}')

            if move in board.legal_moves:
                board.push(move)
                update_board()
                selected_square = None  # Reset selected square after valid move
                turn = 'ai'  # Switch turn to AI after human move
                ai_move()  # Let AI make its move
            else:
                print(f"Invalid move: {selected_square} to {current_square}")
                print("Legal moves:", [m.uci() for m in board.legal_moves])
                selected_square = None  # Reset selected square after invalid move
                update_board()  # Update board to reflect deselection

    except Exception as e:
        print(f"Error handling player move: {e}")

# AI's move: Uses the chess engine to calculate and make the best move
def ai_move():
    global turn
    try:
        print("AI is thinking...")
        # Ensure the FEN string is passed, not the board object
        fen = board.fen()  # Get the FEN string from the current board state
        print(f"AI thinking with FEN: {fen}")
        
        depth = 3  # You can adjust the depth based on performance

        # Pass the FEN string (not the board object) to find_best_move
        best_move_uci = find_best_move(fen, depth)
        print(f"Best move from AI: {best_move_uci}")

        if best_move_uci:
            move = chess.Move.from_uci(best_move_uci)
            board.push(move)
            print(f"AI moves: {move.uci()}")
            update_board()
            turn = 'human'  # Switch turn to human after AI move
    except Exception as e:
        print(f"Error during AI move: {e}")

# Deselect the current piece
def deselect_piece():
    global selected_square
    try:
        selected_square = None
        print("Deselected piece")
        update_board()  # Update the board after deselecting
    except Exception as e:
        print(f"Error deselecting piece: {e}")

# Create the chessboard grid (8x8) in the UI
selected_square = None
labels = []
turn = 'human'  # The game starts with the human player's turn

# Decrease the size of each square and font size
square_size = 4
font_size = 14

# Create 8x8 grid with Tkinter labels
for i in range(8):
    row = []
    for j in range(8):
        label = tk.Label(root, width=square_size, height=square_size, relief="solid", font=("Arial", font_size), bg="grey", bd=2)
        label.grid(row=i, column=j)
        label.bind("<Button-1>", lambda e, i=i, j=j: player_move(i, j))  # Bind mouse click
        row.append(label)
    labels.append(row)

# Create the Deselect Button
deselect_button = tk.Button(root, text="Deselect Piece", command=deselect_piece)
deselect_button.grid(row=8, column=0, columnspan=8, pady=20, padx=10)

# Start the game
update_board()

# Run the Tkinter event loop
root.mainloop()