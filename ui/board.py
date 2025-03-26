from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QSplitter, QFrame
)
from PyQt5.QtCore import Qt, QPoint, QTimer
import chess
import sys

from ui.components.board_components import ChessSquare, ThinkingIndicator
from ui.components.history import MoveHistoryWidget
from ui.components.sidebar import AIControlPanel
from ui.components.popups import PawnPromotionDialog, GameOverPopup
from ui.components.animations import AnimatedLabel
from ui.workers import AIWorker

class ChessBoard(QMainWindow):
    def __init__(self, mode="human_ai", parent_app=None):
        super().__init__()
        
        self.mode = mode
        self.parent_app = parent_app
        
        if self.mode == "human_ai":
            self.setWindowTitle("Chess - Human vs AI")
        else:
            self.setWindowTitle("Chess - AI vs AI")
            
        self.setGeometry(100, 100, 1000, 700)  # Increased window size for better display
        self.setMinimumSize(800, 600)  # Set minimum size to prevent too small windows
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
        """)
        
        self.board = chess.Board()
        self.selected_square = None
        
        if self.mode == "human_ai":
            self.turn = 'human'
        else:
            self.turn = 'ai1'
            
        self.valid_moves = []
        self.castling_moves = []  # Store castling moves separately for special highlighting
        self.last_move_from = None
        self.last_move_to = None
        
        self.ai_game_running = False
        self.move_delay = 800  # Default animation speed
        self.ai_depth = 3  # Default AI search depth
        self.ai_worker = None  # For background AI computation
        self.ai_computation_active = False  # Flag to track if AI is actively computing

        # Create the main layout with splitter for resizable panels
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #2c3e50;")

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Create a splitter for resizable sections
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setHandleWidth(2)  # Thinner splitter handle
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #455a64;
            }
        """)
        main_layout.addWidget(self.main_splitter)

        # Create the game area
        game_area = QWidget()
        game_layout = QVBoxLayout(game_area)
        game_layout.setSpacing(15)
        
        # Create board container with a nice border
        board_container = QFrame()
        board_container.setFrameShape(QFrame.StyledPanel)
        board_container.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #455a64;
            }
        """)
        board_layout = QVBoxLayout(board_container)
        
        # Create board widget with fixed size
        board_widget = QWidget()
        board_widget.setStyleSheet("background-color: #455a64; padding: 5px; border-radius: 5px;")
        self.board_layout = QGridLayout(board_widget)
        self.board_layout.setSpacing(0)
        self.board_layout.setContentsMargins(5, 5, 5, 5)

        for j in range(8):
            col_label = QLabel(chr(97 + j))  # 'a' through 'h'
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
            self.board_layout.addWidget(col_label, 8, j)
            
        for i in range(8):
            row_label = QLabel(str(8 - i))  # This ensures proper numbering from 8 to 1
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
            self.board_layout.addWidget(row_label, i, 8)
        
        for i in range(9):  # 8 squares + 1 label column
            self.board_layout.setColumnMinimumWidth(i, 60)
            if i < 9:  # 8 squares + 1 label row
                self.board_layout.setRowMinimumHeight(i, 60)
        
        # Create the squares and labels
        self.squares = []
        # Add column labels (a-h) with improved visibility
        for j in range(8):
            col_label = QLabel(chr(97 + j))  # 'a' through 'h'
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
            self.board_layout.addWidget(col_label, 8, j)
            
            # Add row labels (1-8) with improved visibility - FIXED ORDER
            row_label = QLabel(str(8 - j))  # This ensures proper numbering from 8 to 1
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
            self.board_layout.addWidget(row_label, j, 8)
        
        for i in range(8):
            row = []
            for j in range(8):
                square = ChessSquare(i, j)
                square.clicked.connect(self.player_move)
                self.board_layout.addWidget(square, i, j)
                row.append(square)
            self.squares.append(row)
            
        # Add the thinking indicator

        board_layout.addWidget(board_widget)
    
        # Create a space reservation for the thinking indicator
        indicator_space = QWidget()
        indicator_space.setFixedHeight(60)  # Set a fixed height for indicator space
        indicator_layout = QVBoxLayout(indicator_space)
        indicator_layout.setContentsMargins(0, 5, 0, 0)
        
        # Add the thinking indicator to the reserved space
        self.thinking_indicator = ThinkingIndicator()
        indicator_layout.addWidget(self.thinking_indicator)
        
        # Add the indicator space to the board layout
        board_layout.addWidget(indicator_space)
        
        # Create status label with improved visibility
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(60)  # Fixed height to prevent resizing
        self.status_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold;
            color: white; 
            padding: 10px;
            background-color: #34495e;
            border-radius: 5px;
            border: 1px solid #455a64;
            margin: 0px;
        """)
        
        # Add to game area
        game_layout.addWidget(board_container)
        game_layout.addWidget(self.status_label)
        
        # Create right sidebar for controls and move history
        sidebar = QWidget()
        sidebar.setMinimumWidth(250)  # Ensure sidebar has minimum width
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(15)
        
        # Create a nested splitter for sidebar elements
        sidebar_splitter = QSplitter(Qt.Vertical)
        sidebar_layout.addWidget(sidebar_splitter)
        
        # Create and add move history widget
        self.move_history = MoveHistoryWidget()
        sidebar_splitter.addWidget(self.move_history)
        
        # Add AI control panel
        self.control_panel = AIControlPanel()
        sidebar_splitter.addWidget(self.control_panel)
        
        # Set initial splitter sizes for sidebar elements
        sidebar_splitter.setSizes([300, 300])
        
        # Connect signals from control panel elements
        self.control_panel.start_button.clicked.connect(self.start_ai_game)
        self.control_panel.pause_button.clicked.connect(self.pause_ai_game)
        self.control_panel.reset_button.clicked.connect(self.reset_game)
        self.control_panel.home_button.clicked.connect(self.return_to_home)
        
        # Disable pause button initially
        self.control_panel.pause_button.setEnabled(False)
        
        self.control_panel.speed_slider.valueChanged.connect(self.update_move_speed)
        self.control_panel.depth_slider.valueChanged.connect(self.update_ai_depth)
        
        # Add everything to the main splitter
        self.main_splitter.addWidget(game_area)
        self.main_splitter.addWidget(sidebar)
        
        # Set initial splitter sizes (75% game area, 25% sidebar)
        self.main_splitter.setSizes([700, 300])
        
        # Hide AI control panel in Human vs AI mode
        if self.mode == "human_ai":
            self.control_panel.hide()
        
        # Set initial status
        if self.mode == "human_ai":
            if self.turn == 'human':
                self.status_label.setText("Your turn")
        else:
            self.status_label.setText("Press 'Start' to begin AI vs AI game")
        
        # Set up timers for animations and AI moves
        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.ai_vs_ai_step)
        
        # Store piece images for animations
        self.animated_pieces = {}
        
        # Load custom chess piece symbols
        self.piece_symbols = self.initialize_piece_symbols()
        
        # Initialize the board
        self.update_board()
    
    def initialize_piece_symbols(self):
        """Create enhanced chess piece symbols with better visibility and style"""
        # Using filled/solid symbols for white pieces instead of outline versions
        piece_symbols = {
            (chess.PAWN, chess.WHITE): "♟︎",    # Solid white pawn
            (chess.PAWN, chess.BLACK): "♟",     # Black pawn
            (chess.KNIGHT, chess.WHITE): "♞︎",   # Solid white knight
            (chess.KNIGHT, chess.BLACK): "♞",    # Black knight
            (chess.BISHOP, chess.WHITE): "♝︎",   # Solid white bishop
            (chess.BISHOP, chess.BLACK): "♝",    # Black bishop
            (chess.ROOK, chess.WHITE): "♜︎",     # Solid white rook
            (chess.ROOK, chess.BLACK): "♜",      # Black rook
            (chess.QUEEN, chess.WHITE): "♛︎",    # Solid white queen
            (chess.QUEEN, chess.BLACK): "♛",     # Black queen
            (chess.KING, chess.WHITE): "♚︎",     # Solid white king
            (chess.KING, chess.BLACK): "♚",      # Black king
        }
        return piece_symbols
    
    def return_to_home(self):
        """Return to the start screen"""
        # Cancel any AI computation before closing
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker = None
            self.ai_computation_active = False
            
        self.close()
        if self.parent_app:
            self.parent_app.show_start_screen()
        
    def update_move_speed(self, value):
        """Update the AI move animation speed"""
        self.move_delay = value
        if self.ai_game_running:
            self.ai_timer.setInterval(self.move_delay)
    
    def update_ai_depth(self, value):
        """Update the AI thinking depth"""
        self.ai_depth = value
        self.control_panel.depth_value.setText(f"Current depth: {value}")
    
    def start_ai_game(self):
        if not self.ai_game_running and not self.board.is_game_over() and not self.ai_computation_active:
            self.ai_game_running = True
            self.control_panel.start_button.setEnabled(False)
            self.control_panel.pause_button.setEnabled(True)
            self.turn = 'ai1' if self.board.turn == chess.WHITE else 'ai2'
            
            # Clear the status label and show thinking indicator
            self.status_label.setText("")
            if self.turn == 'ai1':
                self.thinking_indicator.start_thinking("AI 1")
            else:
                self.thinking_indicator.start_thinking("AI 2")
            
            # Start the AI move timer
            self.ai_timer.start(self.move_delay)
    
    def pause_ai_game(self):
        """Pause the AI vs AI game"""
        self.ai_game_running = False
        self.ai_timer.stop()
        self.thinking_indicator.stop_thinking()
        
        # Cancel any ongoing AI computation
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker = None
            self.ai_computation_active = False
            
        self.control_panel.start_button.setEnabled(True)
        self.control_panel.pause_button.setEnabled(False)
        self.status_label.setText("Game paused")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.ai_game_running = False
        self.ai_timer.stop()
        self.thinking_indicator.stop_thinking()
        
        # Cancel any ongoing AI computation
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker = None
            self.ai_computation_active = False
            
        self.board = chess.Board()
        if self.mode == "human_ai":
            self.turn = 'human'
        else:
            self.turn = 'ai1'
            
        self.control_panel.start_button.setEnabled(True)
        self.control_panel.pause_button.setEnabled(False)
        
        if self.mode == "human_ai":
            self.status_label.setText("Your turn")
        else:
            self.status_label.setText("Press 'Start' to begin AI vs AI game")
            
        self.last_move_from = None
        self.last_move_to = None
        self.move_history.clear_history()
        self.update_board()
    
    def animate_piece_movement(self, from_pos, to_pos, piece_symbol, piece_color, capture=False, callback=None):
        """Animate a piece moving from one square to another"""
        # Create the animated piece (temporary overlay)
        animated_piece = AnimatedLabel(self.central_widget)
        animated_piece.setText(piece_symbol)
        animated_piece.setAlignment(Qt.AlignCenter)
        animated_piece.setStyleSheet(f"""
            font-size: 40px; 
            background-color: transparent; 
            color: {piece_color};
            font-weight: bold;
        """)
        animated_piece.setFixedSize(60, 60)
        
        # Position at the starting square
        from_rect = self.squares[from_pos[0]][from_pos[1]].geometry()
        global_from_pos = self.squares[from_pos[0]][from_pos[1]].mapTo(self.central_widget, QPoint(0, 0))
        
        animated_piece.move(global_from_pos)
        animated_piece.show()
        
        # Calculate the end position
        global_to_pos = self.squares[to_pos[0]][to_pos[1]].mapTo(self.central_widget, QPoint(0, 0))
        
        # Set up animation
        animated_piece.animation.finished.connect(lambda: self.finish_animation(animated_piece, callback))
        
        # Start the animation
        animated_piece.move_to(global_to_pos)
        
        # Store the animated piece to prevent garbage collection
        self.animated_pieces[id(animated_piece)] = animated_piece
    
    def finish_animation(self, animated_piece, callback=None):
        """Clean up after animation is complete and call the callback"""
        # Remove the animated piece from display and memory
        animated_piece.hide()
        self.animated_pieces.pop(id(animated_piece), None)
        
        # Call the callback if provided
        if callback:
            callback()
    
    def ai_vs_ai_step(self):
        """Execute a single step in the AI vs AI game with smooth animation"""
        if self.ai_game_running and not self.board.is_game_over() and not self.ai_computation_active:
            # Set flag to prevent overlapping computations
            self.ai_computation_active = True
            
            # Determine current player
            current_color = "White" if self.board.turn == chess.WHITE else "Black"
            current_ai = "AI 1" if self.turn == 'ai1' else "AI 2"
            
            # Update thinking indicator
            self.thinking_indicator.start_thinking(current_ai)
            self.status_label.setText("")  # Clear status label when thinking
            
            # Stop the AI timer during calculation
            self.ai_timer.stop()
            
            # Use AI worker thread to prevent GUI freezing
            engine_num = 1 if self.turn == 'ai1' else 2
            self.ai_worker = AIWorker(self.board.fen(), self.ai_depth, engine_num)
            self.ai_worker.finished.connect(self.handle_ai_move_result)
            self.ai_worker.start()
    
    def handle_ai_move_result(self, best_move_uci):
        """Handle the result from the AI computation thread"""
        # Reset the AI computation flag
        self.ai_computation_active = False
        
        if not self.ai_game_running:
            return
            
        if best_move_uci:
            # Convert the move to chess.Move object
            move = chess.Move.from_uci(best_move_uci)
            
            # Get information for the move
            from_square = chess.square_rank(move.from_square), chess.square_file(move.from_square)
            to_square = chess.square_rank(move.to_square), chess.square_file(move.to_square)
            
            # Convert to UI coordinates
            from_pos = (7 - from_square[0], from_square[1])
            to_pos = (7 - to_square[0], to_square[1])
            
            # Get the piece information
            piece = self.board.piece_at(move.from_square)
            piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#000000"
            
            # Determine piece symbol for animation
            piece_symbol = self.piece_symbols.get((piece.piece_type, piece.color), "")
            
            # Check if move is a capture
            is_capture = self.board.is_capture(move)
            
            # Check if move is castling
            is_castling = piece and piece.piece_type == chess.KING and abs(move.from_square % 8 - move.to_square % 8) > 1
            
            # Stop thinking indicator during animation
            self.thinking_indicator.stop_thinking()
            
            # Function to execute after animation completes
            def after_animation():
                # Make the move on the actual board
                self.board.push(move)
                
                # Add move to history
                from_uci = chess.square_name(move.from_square)
                to_uci = chess.square_name(move.to_square)
                is_check = self.board.is_check()
                
                self.move_history.add_move(
                    piece, 
                    from_uci, 
                    to_uci, 
                    "White" if piece.color == chess.WHITE else "Black",
                    is_capture,
                    is_check,
                    move.promotion,
                    is_castling
                )
                
                # Update the board display
                self.last_move_from = from_pos
                self.last_move_to = to_pos
                self.update_board()
                
                # Check if game is over
                if self.board.is_game_over():
                    self.ai_game_running = False
                    self.control_panel.start_button.setEnabled(False)
                    self.control_panel.pause_button.setEnabled(False)
                    self.show_game_over_popup()
                else:
                    # Switch to next AI
                    self.turn = 'ai2' if self.turn == 'ai1' else 'ai1'
                    
                    # Update status text (will be hidden when AI starts thinking)
                    next_ai = "AI 1" if self.turn == 'ai1' else "AI 2"
                    self.thinking_indicator.start_thinking(next_ai)
                    self.status_label.setText("")
                    
                    # Resume the AI timer for next move
                    self.ai_timer.start(self.move_delay)
            
            # Animate the piece movement
            self.animate_piece_movement(from_pos, to_pos, piece_symbol, piece_color, is_capture, after_animation)
        else:
            # No valid move found
            self.ai_game_running = False
            self.thinking_indicator.stop_thinking()
            self.control_panel.start_button.setEnabled(True)
            self.control_panel.pause_button.setEnabled(False)
            self.status_label.setText("No valid moves available")
    
    def find_valid_moves(self, from_square):
        """Find all valid moves for a piece on the given square"""
        valid_moves = []
        castling_moves = []
        from_square_index = chess.parse_square(from_square)
        
        piece = self.board.piece_at(from_square_index)
        
        for move in self.board.legal_moves:
            if move.from_square == from_square_index:
                # Identify castling moves for special highlighting
                if piece and piece.piece_type == chess.KING and abs(move.from_square % 8 - move.to_square % 8) > 1:
                    castling_moves.append(move)
                else:
                    valid_moves.append(move)
                
        return valid_moves, castling_moves

    def update_board(self):
        """Update the visual representation of the chess board"""

        selected = chess.parse_square(self.selected_square) if self.selected_square else None
        valid_destinations = [move.to_square for move in self.valid_moves]
        castling_destinations = [move.to_square for move in self.castling_moves]

        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)
                piece = self.board.piece_at(square)
                square_widget = self.squares[i][j]

                # Reset states
                square_widget.is_selected = False
                square_widget.is_last_move = False
                square_widget.is_valid_move = False
                square_widget.is_castling_move = False
                
                # Set states based on game state
                if selected == square:
                    square_widget.is_selected = True
                if (i, j) == self.last_move_from or (i, j) == self.last_move_to:
                    square_widget.is_last_move = True
                if square in valid_destinations:
                    square_widget.is_valid_move = True
                if square in castling_destinations:
                    square_widget.is_castling_move = True
                    
                # Update the square appearance
                square_widget.update_appearance()
                
                # Draw piece or empty square
                if piece:
                    symbol = self.piece_symbols.get((piece.piece_type, piece.color), "")
                    piece_color = "#000000" if piece.color == chess.BLACK else "#FFFFFF"
                    square_widget.setText(symbol)
                    square_widget.setStyleSheet(square_widget.styleSheet() + f"""
                        font-size: 40px; 
                        color: {piece_color};
                        font-weight: bold;
                    """)
                else:
                    square_widget.setText("")

        # Check for game over
        if self.board.is_game_over():
            result = self.board.result()
            if result == '1-0':
                winner = "Player (White)" if self.mode == "human_ai" else "AI 1 (White)"
                self.status_label.setText(f"{winner} Wins!")
            elif result == '0-1':
                winner = "AI (Black)" if self.mode == "human_ai" else "AI 2 (Black)"
                self.status_label.setText(f"{winner} Wins!")
            else:
                self.status_label.setText("It's a Draw!")
            
            # Stop the AI game if running
            if self.ai_game_running:
                self.ai_game_running = False
                self.ai_timer.stop()
                self.thinking_indicator.stop_thinking()
                if self.ai_worker and self.ai_worker.isRunning():
                    self.ai_worker.terminate()
                    self.ai_worker = None
                    self.ai_computation_active = False
                    
                self.control_panel.start_button.setEnabled(False)
                self.control_panel.pause_button.setEnabled(False)
                self.show_game_over_popup()
        else:
            # Status update based on game mode and state
            if self.mode == "human_ai":
                if self.turn == 'human':
                    self.status_label.setText("Your turn")
                else:
                    # Don't update status here for AI turn, let the AI move function handle it
                    pass
            else:  # AI vs AI mode
                if self.ai_game_running:
                    # Status is handled by the thinking indicator, leave status label empty
                    self.status_label.setText("")
                else:
                    # Game not running, show start message
                    if self.turn == 'ai1':
                        self.status_label.setText("Press 'Start' to begin AI vs AI game")
                    else:
                        self.status_label.setText("Press 'Start' to continue AI vs AI game")

    def player_move(self, i, j):
        """Handle player move selection"""
        if self.mode != "human_ai" or self.turn != 'human' or self.board.is_game_over() or self.ai_computation_active:
            return
            
        square = chess.square(j, 7 - i)
        current_square = chess.SQUARE_NAMES[square]

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = current_square
                self.valid_moves, self.castling_moves = self.find_valid_moves(current_square)
                self.update_board()
        else:
            if self.selected_square == current_square:
                self.selected_square = None
                self.valid_moves = []
                self.castling_moves = []
                self.update_board()
                return
                
            move_made = False
            
            # Check both regular and castling moves
            all_valid_moves = self.valid_moves + self.castling_moves
            
            for move in all_valid_moves:
                if move.to_square == square:
                    from_square = chess.parse_square(self.selected_square)
                    piece = self.board.piece_at(from_square)
                    
                    # Handle pawn promotion
                    is_promotion = (piece and piece.piece_type == chess.PAWN and
                                (chess.square_rank(square) == 0 or chess.square_rank(square) == 7))

                    if is_promotion:
                        dialog = PawnPromotionDialog(self)
                        if dialog.exec_() == QDialog.Accepted:
                            promotion_piece = dialog.get_choice()
                            move = chess.Move(from_square, square, 
                                            promotion=chess.Piece.from_symbol(promotion_piece.upper()).piece_type)
                        else:
                            return
                    
                    # Check if move is castling
                    is_castling = piece and piece.piece_type == chess.KING and abs(move.from_square % 8 - move.to_square % 8) > 1
                    
                    # Get animation info
                    from_pos = (7 - chess.square_rank(from_square), chess.square_file(from_square))
                    to_pos = (7 - chess.square_rank(square), chess.square_file(square))
                    
                    # Determine piece symbol for animation
                    piece_symbol = self.piece_symbols.get((piece.piece_type, piece.color), "")
                    piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#000000"
                    is_capture = self.board.is_capture(move)
                    
                    # Reset selection
                    self.selected_square = None
                    self.valid_moves = []
                    self.castling_moves = []
                    
                    # Animate move
                    def after_player_move():
                        # Execute move on the board
                        self.board.push(move)
                        
                        # Add to move history
                        from_uci = chess.square_name(from_square)
                        to_uci = chess.square_name(square)
                        is_check = self.board.is_check()
                        
                        self.move_history.add_move(
                            piece, 
                            from_uci, 
                            to_uci, 
                            "White",
                            is_capture,
                            is_check,
                            move.promotion if is_promotion else None,
                            is_castling
                        )
                        
                        # Update last move highlighting
                        self.last_move_from = from_pos
                        self.last_move_to = to_pos
                        
                        # Update board display
                        self.update_board()
                        
                        # Check if game is over
                        if not self.board.is_game_over():
                            # Switch to AI's turn
                            self.turn = 'ai'
                            
                            # Update status with "thinking" animation and clear status label
                            self.status_label.setText("")
                            self.thinking_indicator.start_thinking("AI")
                            
                            # Allow UI to update before AI starts computing
                            QTimer.singleShot(100, self.ai_move)
                        else:
                            self.show_game_over_popup()
                    
                    # Start animation
                    self.animate_piece_movement(from_pos, to_pos, piece_symbol, piece_color, is_capture, after_player_move)
                    move_made = True
                    break
            
            if not move_made:
                # If clicking another piece of the same color, select it instead
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = current_square
                    self.valid_moves, self.castling_moves = self.find_valid_moves(current_square)
                else:
                    # Invalid move - deselect
                    self.valid_moves = []
                    self.castling_moves = []
                    self.selected_square = None
                
                self.update_board()

    def ai_move(self):
        """Calculate and execute the AI's move using a background thread"""
        try:
            # Set flag to prevent overlapping AI computations
            self.ai_computation_active = True
            
            # Update status with thinking animation
            self.status_label.setText("")
            self.thinking_indicator.start_thinking("AI")
            
            # Check if game is already over
            if self.board.is_game_over():
                self.thinking_indicator.stop_thinking()
                self.ai_computation_active = False
                self.show_game_over_popup()
                return

            # Use a worker thread to prevent GUI freezing
            self.ai_worker = AIWorker(self.board.fen(), self.ai_depth)
            self.ai_worker.finished.connect(self.handle_human_ai_move_result)
            self.ai_worker.start()
            
        except Exception as e:
            self.thinking_indicator.stop_thinking()
            self.ai_computation_active = False
            self.status_label.setText(f"Error during AI move: {str(e)}")
    
    def handle_human_ai_move_result(self, best_move_uci):
        """Handle the result of AI computation for human vs AI mode"""
        # Reset the AI computation flag
        self.ai_computation_active = False
        
        if best_move_uci:
            move = chess.Move.from_uci(best_move_uci)
            
            # Get animation info
            from_square = move.from_square
            to_square = move.to_square
            piece = self.board.piece_at(from_square)
            
            from_pos = (7 - chess.square_rank(from_square), chess.square_file(from_square))
            to_pos = (7 - chess.square_rank(to_square), chess.square_file(to_square))
            
            # Determine piece symbol and color for animation
            piece_symbol = self.piece_symbols.get((piece.piece_type, piece.color), "")
            piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#000000"
            is_capture = self.board.is_capture(move)
            
            # Check if move is castling
            is_castling = piece and piece.piece_type == chess.KING and abs(move.from_square % 8 - move.to_square % 8) > 1
            
            # Stop thinking indicator during animation
            self.thinking_indicator.stop_thinking()
            
            # Animate the move
            def after_ai_move():
                # Execute move on the board
                self.board.push(move)
                
                # Add to move history
                from_uci = chess.square_name(from_square)
                to_uci = chess.square_name(to_square)
                is_check = self.board.is_check()
                
                self.move_history.add_move(
                    piece, 
                    from_uci, 
                    to_uci, 
                    "Black",
                    is_capture,
                    is_check,
                    move.promotion,
                    is_castling
                )
                
                # Update last move highlighting
                self.last_move_from = from_pos
                self.last_move_to = to_pos
                
                # Update board and switch back to human's turn
                self.update_board()
                self.turn = 'human'
                
                # Check if game is over
                if self.board.is_game_over():
                    self.show_game_over_popup()
            
            # Start animation
            self.animate_piece_movement(from_pos, to_pos, piece_symbol, piece_color, is_capture, after_ai_move)
        else:
            self.thinking_indicator.stop_thinking()
            self.status_label.setText("AI could not find a valid move!")

    def show_game_over_popup(self):
        """Show the game over popup with appropriate message and options"""
        result = self.board.result()
        
        if self.mode == "human_ai":
            self.popup = GameOverPopup(result, self)
        else:
            winner_text = ""
            if result == '1-0':
                winner_text = "🏆 AI 1 (White) Wins! 🏆"
            elif result == '0-1':
                winner_text = "🏆 AI 2 (Black) Wins! 🏆"
            else:
                winner_text = "🤝 It's a Draw! 🤝"
                
            self.popup = GameOverPopup(result, self, winner_text)
        
        # Connect popup signals
        self.popup.play_again_signal.connect(self.reset_game)
        self.popup.return_home_signal.connect(self.return_to_home)
        
        self.popup.exec_()

    def close_game(self):
        """Close the game window"""
        self.close()
    
    def resizeEvent(self, event):
        """Handle window resize events to ensure proper layout"""
        super().resizeEvent(event)
        
        # Get current window width
        window_width = self.width()
        
        # Calculate appropriate sizes based on window width
        if window_width < 900:
            # For smaller screens, give more space to the game board
            board_portion = int(window_width * 0.75)
            sidebar_portion = int(window_width * 0.25)
        else:
            # For larger screens, give more space to the sidebar
            board_portion = int(window_width * 0.7) 
            sidebar_portion = int(window_width * 0.3)
        
        # Ensure minimum sidebar width
        min_sidebar = 250
        if sidebar_portion < min_sidebar:
            sidebar_portion = min_sidebar
            board_portion = window_width - min_sidebar
        
        # Apply the new sizes
        self.main_splitter.setSizes([board_portion, sidebar_portion])