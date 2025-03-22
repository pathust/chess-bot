from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QLabel, QVBoxLayout, 
    QHBoxLayout, QComboBox, QPushButton, QDialog, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import chess
from chess_engine import find_best_move

class PawnPromotionDialog(QDialog):
    def __init__(self, parent=None):
        """Initialize the promotion dialog with selection options."""
        super().__init__(parent)
        self.setWindowTitle("Pawn Promotion")
        self.setModal(True)

        # Create dialog layout
        layout = QVBoxLayout()

        # Add instructional label
        self.label = QLabel("Choose a piece to promote to:")
        self.label.setStyleSheet("font-size: 14pt; margin-bottom: 10px;")
        layout.addWidget(self.label)

        # Add dropdown for piece selection
        self.promotion_choice = QComboBox()
        self.promotion_choice.setStyleSheet("font-size: 12pt; padding: 5px;")
        self.promotion_choice.addItems(["Queen", "Rook", "Bishop", "Knight"])
        layout.addWidget(self.promotion_choice)

        # Add confirmation button
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 12pt;
                padding: 8px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_choice(self):
        """
        Return the selected piece in UCI format (q, r, b, n).
        
        Returns:
            str: Single character representing the promotion piece
        """
        piece_map = {
            "Queen": "q",
            "Rook": "r",
            "Bishop": "b",
            "Knight": "n"
        }
        return piece_map[self.promotion_choice.currentText()]

class GameOverPopup(QDialog):
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Over")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  
        self.setModal(True) 
        
        # Set modern styling with rounded corners
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #4CAF50;
                border-radius: 10px;
            }
        """)
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Configure result message and color based on outcome
        if result == '1-0':
            message = "🏆 Player (White) Wins! 🏆"
            color = "#4CAF50"  # Green for win
        elif result == '0-1':
            message = "❌ AI (Black) Wins! ❌"
            color = "#F44336"  # Red for loss
        else:
            message = "🤝 It's a Draw! 🤝"
            color = "#2196F3"  # Blue for draw

        # Create and style the result label
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            font-size: 20pt; 
            font-weight: bold; 
            color: {color}; 
            padding: 20px;
            font-family: 'Arial', sans-serif;
        """)
        layout.addWidget(label)

        # Create a styled OK button
        ok_button = QPushButton("OK", self)
        ok_button.setCursor(Qt.PointingHandCursor)  # Hand cursor for better UX
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16pt;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        ok_button.clicked.connect(self.accept)
        
        # Center the button with a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addSpacing(10)

        self.setLayout(layout)
        self.setFixedSize(400, 200)

class ChessBoard(QMainWindow):
    """
    Main chess game window that displays the board and handles game logic.
    
    Features:
    - 8x8 chess board with proper piece display
    - Human vs AI gameplay
    - Move validation
    - Pawn promotion
    - Game over detection
    - Highlight available moves for selected piece
    """
    def __init__(self):
        """Initialize the chess game window with board and pieces."""
        super().__init__()

        # Configure main window
        self.setWindowTitle("Chess - One Player Game (vs AI)")
        self.setGeometry(100, 100, 500, 500)
        
        # Initialize chess logic
        self.board = chess.Board()
        self.selected_square = None
        self.turn = 'human'  # Start with human player
        self.valid_moves = []  # Store valid moves for the selected piece

        # Create central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create chess board grid layout
        self.layout = QGridLayout(self.central_widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create square labels for the chess board
        self.labels = []
        for i in range(8):
            row = []
            for j in range(8):
                label = QLabel(self)
                label.setAlignment(Qt.AlignCenter)
                label.setFixedSize(60, 60)
                label.setMargin(0)
                label.mousePressEvent = lambda event, x=i, y=j: self.player_move(x, y)
                self.layout.addWidget(label, i, j)
                row.append(label)
            self.labels.append(row)

        # Add status label at the bottom
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: #000000; padding: 10px;")
        self.layout.addWidget(self.status_label, 8, 0, 1, 8)
        
        # Set initial status
        if self.turn == 'human':
            self.status_label.setText("Your turn")
        
        # Now render the initial board state after all UI elements are created
        self.update_board()

    def find_valid_moves(self, from_square):
        valid_moves = []
        from_square_index = chess.parse_square(from_square)
        
        # Iterate through all legal moves and filter moves for the selected piece
        for move in self.board.legal_moves:
            if move.from_square == from_square_index:
                valid_moves.append(move)
                
        return valid_moves

    def update_board(self):
        """Update the visual representation of the chess board."""
        # Unicode symbols for chess pieces
        piece_symbols = {
            (chess.PAWN, chess.WHITE): "♟",
            (chess.PAWN, chess.BLACK): "♟",
            (chess.KNIGHT, chess.WHITE): "♞",
            (chess.KNIGHT, chess.BLACK): "♞",
            (chess.BISHOP, chess.WHITE): "♝",
            (chess.BISHOP, chess.BLACK): "♝",
            (chess.ROOK, chess.WHITE): "♜",
            (chess.ROOK, chess.BLACK): "♜",
            (chess.QUEEN, chess.WHITE): "♛",
            (chess.QUEEN, chess.BLACK): "♛",
            (chess.KING, chess.WHITE): "♚",
            (chess.KING, chess.BLACK): "♚",
        }

        # Highlight the selected square if any
        selected = chess.parse_square(self.selected_square) if self.selected_square else None
        
        # Get valid destination squares
        valid_destinations = [move.to_square for move in self.valid_moves]

        # Update each square on the board
        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)  # Convert to chess library coordinates
                piece = self.board.piece_at(square)
                label = self.labels[i][j]

                # Determine square color (alternating pattern)
                if (i + j) % 2 == 0:
                    bg_color = "#c1bfb0"  # Light square
                else:
                    bg_color = "#7a9bbe"  # Dark square
                
                # Highlight selected square
                if selected == square:
                    bg_color = "#ffff99"  # Yellow highlight for selected piece
                
                # Highlight valid destination squares
                elif square in valid_destinations:
                    bg_color = "#90ee90"  # Light green highlight for valid moves
                
                # Draw piece or empty square
                if piece:
                    symbol = piece_symbols.get((piece.piece_type, piece.color), "")
                    piece_color = "#000000" if piece.color == chess.BLACK else "#FFFFFF"
                    label.setText(symbol)
                    label.setStyleSheet(f"background-color: {bg_color}; border: 1px solid black; font-size: 36px; color: {piece_color};")
                else:
                    label.setText("")
                    label.setStyleSheet(f"background-color: {bg_color}; border: 1px solid black;")

        # Check for game over
        if self.board.is_game_over():
            result = self.board.result()
            if result == '1-0':
                self.status_label.setText("Player (White) Wins!")
            elif result == '0-1':
                self.status_label.setText("AI (Black) Wins!")
            else:
                self.status_label.setText("It's a Draw!")
            
            self.show_game_over_popup()
        else:
            # Update status label based on turn
            if self.turn == 'human':
                self.status_label.setText("Your turn")
                self.status_label.setStyleSheet("font-size: 20px; color: #FFFFFF; padding: 10px;")
            else:
                self.status_label.setText("AI is thinking...")
                self.status_label.setStyleSheet("font-size: 20px; color: #FFFFFF; padding: 10px;")

    def player_move(self, i, j):
        # Convert UI coordinates to chess coordinates
        square = chess.square(j, 7 - i)
        current_square = chess.SQUARE_NAMES[square]

        # If no piece is selected yet, select it
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = current_square
                self.valid_moves = self.find_valid_moves(current_square)
                self.update_board()  # Update to show selection and valid moves
        else:
            # If clicking the same square, deselect it
            if self.selected_square == current_square:
                self.selected_square = None
                self.valid_moves = []
                self.update_board()
                return
                
            # If clicking a destination square that is valid
            move_made = False
            for move in self.valid_moves:
                if move.to_square == square:
                    # Check for pawn promotion
                    from_square = chess.parse_square(self.selected_square)
                    piece = self.board.piece_at(from_square)
                    
                    is_promotion = (piece and piece.piece_type == chess.PAWN and
                                (chess.square_rank(square) == 0 or chess.square_rank(square) == 7))

                    # Handle pawn promotion
                    if is_promotion:
                        dialog = PawnPromotionDialog(self)
                        if dialog.exec_() == QDialog.Accepted:
                            promotion_piece = dialog.get_choice()
                            move = chess.Move(from_square, square, 
                                            promotion=chess.Piece.from_symbol(promotion_piece.upper()).piece_type)
                        else:
                            return  # Cancelled promotion
                    
                    print("Move attempted:", move)
                    self.board.push(move)
                    move_made = True
                    break
            
            # Reset selection
            self.selected_square = None
            self.valid_moves = []
            
            if move_made:
                # Update board immediately after player's move
                self.update_board()
                print(self.board.fen())
                
                # Check if game is over after player's move
                if not self.board.is_game_over():
                    # Switch to AI's turn
                    self.turn = 'ai'
                    self.status_label.setText("AI is thinking...")
                    
                    # Force UI update before AI begins thinking
                    QApplication.processEvents()
                    
                    # Use a timer to delay the AI move by 1 second
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(1000, self.ai_move)
            else:
                # If clicking another piece of the same color, select it instead
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = current_square
                    self.valid_moves = self.find_valid_moves(current_square)
                else:
                    # Invalid move - deselect
                    self.valid_moves = []
                
                self.update_board()

    def ai_move(self):
        """
        Calculate and execute the AI's move using the chess engine.
        """
        try:
            print("AI is thinking...")
            fen = self.board.fen()
            print(f"AI thinking with FEN: {fen}")

            # Check if game is already over
            if self.board.is_game_over():
                print("Game is over, no more moves can be made.")
                self.show_game_over_popup()
                return

            # Find and execute best move
            depth = 3  # Search depth (can be adjusted)
            best_move_uci = find_best_move(fen, depth)

            if best_move_uci:
                move = chess.Move.from_uci(best_move_uci)
                print(f"AI moves: {move.uci()}")
                self.board.push(move)
                self.update_board()
                self.turn = 'human'  # Switch back to human's turn
                self.status_label.setText("Your turn")
            else:
                print("AI could not find a valid move!")
        except Exception as e:
            print(f"Error during AI move: {e}")

    def show_game_over_popup(self):
        result = self.board.result()
        self.popup = GameOverPopup(result, self)
        
        # Close the game when the user clicks OK
        if self.popup.exec_() == QDialog.Accepted:
            self.close_game()

    def close_game(self):
        """
        Close the game window.
        """
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = ChessBoard()
    window.show()
    app.exec_()