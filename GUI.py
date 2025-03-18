import tkinter as tk
import chess

# Set up initial chess board
board = chess.Board()

# Create main window for the Tkinter UI
root = tk.Tk()
root.title("Two-Player Chess Game")

# Function to update the board on the interface with color differentiation for dark/light squares
def update_board():
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

# Function to handle player's move
def player_move(i, j):
    global selected_square, turn

    square = chess.square(j, 7 - i)
    current_square = chess.SQUARE_NAMES[square]

    # Highlight the turn with a color change (e.g., green for Black's turn, red for White's turn)
    if turn == 'black':
        root.config(bg='green')  # Green for black's turn
    else:
        root.config(bg='red')  # Red for white's turn

    if selected_square is None:
        piece = board.piece_at(square)

        if piece and piece.color == board.turn:  # Ensure it's the correct turn
            selected_square = current_square
            print(f"Selected piece: {selected_square}")
    else:
        try:
            # Check if the move is the same square
            if selected_square == current_square:
                print(f"Invalid move: {selected_square} to {current_square} (same square)")
                return

            move = chess.Move.from_uci(f'{selected_square}{current_square}')

            if move in board.legal_moves:
                board.push(move)
                update_board()
                selected_square = None
                turn = 'black' if turn == 'white' else 'white'  # Switch turn
            else:
                print(f"Invalid move: {selected_square} to {current_square}")
                print("Legal moves:", [m.uci() for m in board.legal_moves])

        except chess.InvalidMoveError as e:
            print(f"Error while processing move: {e}")
            print("Legal moves:", [m.uci() for m in board.legal_moves])

# Function to deselect the current piece
def deselect_piece():
    global selected_square
    selected_square = None
    print("Deselected piece")
    root.config(bg='black')  # Reset the background color to white (or any other default color)
    update_board()  # Update the board after deselecting

# Create the chessboard grid (8x8) in the UI
selected_square = None
labels = []
turn = 'white'  # Track the current turn, White moves first

# Decrease the size of each square and font size
square_size = 4
font_size = 14

# Create 8x8 grid with Tkinter labels
for i in range(8):
    row = []
    for j in range(8):
        label = tk.Label(root, width=square_size, height=square_size, relief="solid", font=("Arial", font_size), bg="grey", bd=2)
        label.grid(row=i, column=j, padx=2, pady=2)  # Add padding to align properly
        label.bind("<Button-1>", lambda e, i=i, j=j: player_move(i, j))  # Bind mouse click
        row.append(label)
    labels.append(row)

# Create the Deselect Button and adjust its placement
deselect_button = tk.Button(root, text="Deselect Piece", command=deselect_piece)
deselect_button.grid(row=8, column=0, columnspan=8, pady=20, padx=10)

# Start the game
update_board()

# Run the Tkinter event loop
root.mainloop()