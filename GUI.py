import sys
import chess
from chess_engine import find_best_move  # Import the chess engine's best move function
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QGridLayout, QWidget, QVBoxLayout, QComboBox, QDialog
from PyQt5.QtCore import Qt

class PawnPromotionDialog(QDialog):
    """Dialog for selecting the promotion piece."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pawn Promotion")
        self.setModal(True)

        layout = QVBoxLayout()

        self.label = QLabel("Choose a piece to promote to:")
        layout.addWidget(self.label)

        self.promotion_choice = QComboBox()
        self.promotion_choice.addItems(["Queen", "Rook", "Bishop", "Knight"])
        layout.addWidget(self.promotion_choice)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_choice(self):
        """Return the selected piece in UCI format (q, r, b, n)."""
        piece_map = {
            "Queen": "q",
            "Rook": "r",
            "Bishop": "b",
            "Knight": "n"
        }
        return piece_map[self.promotion_choice.currentText()]

class ChessBoard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chess - One Player Game (vs AI)")
        self.setGeometry(100, 100, 500, 500)  # Set size of the window

        self.board = chess.Board("8/7p/4k1p1/8/8/p3KNP1/1b5P/8 w - - 0 50")
        self.selected_square = None  # For storing the selected piece
        self.turn = 'human'  # The game starts with the human player's turn

        # Create a QWidget for the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a grid layout for the chessboard
        self.layout = QGridLayout(self.central_widget)
        self.layout.setSpacing(0)  # Remove the space between the buttons

        # Create labels for the chessboard (8x8 grid)
        self.labels = []
        for i in range(8):
            row = []
            for j in range(8):
                label = QLabel(self)
                label.setAlignment(Qt.AlignCenter)
                label.setFixedSize(50, 50)  # Set the size for each square
                label.setStyleSheet("background-color: grey; border: 1px solid black;")
                label.mousePressEvent = lambda event, x=i, y=j: self.player_move(x, y)  # Connect each square to a move
                self.layout.addWidget(label, i, j)
                row.append(label)
            self.labels.append(row)

        # Create the Deselect Button
        self.deselect_button = QPushButton('Deselect Piece', self)
        self.deselect_button.clicked.connect(self.deselect_piece)
        self.layout.addWidget(self.deselect_button, 8, 0, 1, 8)

        self.update_board()

    def update_board(self):
        """Update the PyQt5 window with the current board state."""
        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)  # Correct the coordinate mapping
                piece = self.board.piece_at(square)
                label = self.labels[i][j]
                if piece:
                    piece_color = 'white' if piece.color == chess.WHITE else 'black'
                    label.setText(piece.symbol())
                    label.setStyleSheet(f"background-color: grey; border: 1px solid black; color: {piece_color}")
                else:
                    label.setText("")
                    label.setStyleSheet("background-color: grey; border: 1px solid black;")

    def player_move(self, i, j):
        """Handle the player's move."""
        square = chess.square(j, 7 - i)
        current_square = chess.SQUARE_NAMES[square]

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:  # Ensure it's the correct turn
                self.selected_square = current_square
        else:
            # Check if the move is the same square
            if self.selected_square == current_square:
                self.selected_square = None  # Deselect piece after invalid move
                self.update_board()
                return

            # Check if the move is a pawn promotion
            from_square = chess.parse_square(self.selected_square)
            to_square = chess.parse_square(current_square)
            piece = self.board.piece_at(from_square)

            is_promotion = (piece and piece.piece_type == chess.PAWN and
                            (chess.square_rank(to_square) == 0 or chess.square_rank(to_square) == 7))

            if is_promotion:
                dialog = PawnPromotionDialog(self)
                if dialog.exec_() == QDialog.Accepted:
                    promotion_piece = dialog.get_choice()
                    move = chess.Move(from_square, to_square, promotion=chess.Piece.from_symbol(promotion_piece.upper()).piece_type)
                else:
                    return  # If the player cancels, do nothing
            else:
                move = chess.Move(from_square, to_square)

            print("Move attempted:", move)

            # Check if the move is valid
            if move in self.board.legal_moves:
                self.board.push(move)
                self.update_board()
                self.selected_square = None  # Reset selected square after valid move
                print(self.board.fen())
                self.turn = 'ai'  # Switch turn to AI after human move
                self.ai_move()  # Let AI make its move
            else:
                print('Invalid move')
                self.selected_square = None  # Reset selected square after invalid move
                self.update_board()


    def deselect_piece(self):
        """Reset the selected piece."""
        self.selected_square = None
        self.update_board()

    def ai_move(self):
        """AI's move: Uses the chess engine to calculate and make the best move."""
        try:
            print("AI is thinking...")
            fen = self.board.fen()  # Get the FEN string from the current board state
            print(f"AI thinking with FEN: {fen}")

            print(fen)
            depth = 3  # You can adjust the depth based on performance
            best_move_uci = find_best_move(fen, depth)
            print(f"Best move from AI: {best_move_uci}")

            if best_move_uci:
                move = chess.Move.from_uci(best_move_uci)
                self.board.push(move)
                print(f"AI moves: {move.uci()}")
                self.update_board()
                self.turn = 'human'  # Switch turn to human after AI move
        except Exception as e:
            print(f"Error during AI move: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessBoard()
    window.show()
    sys.exit(app.exec_())