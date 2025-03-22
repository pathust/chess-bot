from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QLabel, QVBoxLayout, 
    QHBoxLayout, QComboBox, QPushButton, QDialog, QWidget, QSlider,
    QListWidget, QSplitter, QFrame, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QIcon, QFont, QPalette
import chess
import sys
import time
from chess_engine import find_best_move as find_best_move1
from chess_engine2 import find_best_move as find_best_move2

class AnimatedLabel(QLabel):
    """Custom QLabel with animation capabilities for chess pieces"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)  # 300ms for piece movement
        
    def move_to(self, target_pos):
        """Animate movement to target position"""
        start_pos = self.pos()
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(target_pos)
        self.animation.start()

class ChessSquare(QLabel):
    """Enhanced chess square widget with hover and selection effects"""
    clicked = pyqtSignal(int, int)
    
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(60, 60)
        self.setMargin(0)
        
        # Initialize states
        self.is_highlighted = False
        self.is_last_move = False
        self.is_valid_move = False
        self.is_selected = False
        
    def enterEvent(self, event):
        """Highlight square on mouse hover"""
        if not self.is_selected and not self.is_last_move:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.8)
            self.setGraphicsEffect(effect)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Remove highlight on mouse leave"""
        if not self.is_selected and not self.is_last_move:
            self.setGraphicsEffect(None)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click on square"""
        self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)
        
    def update_appearance(self):
        """Update the square's appearance based on its state"""
        base_color = "#c1bfb0" if (self.row + self.col) % 2 == 0 else "#7a9bbe"
        
        if self.is_selected:
            base_color = "#ffff99"  # Yellow for selected piece
        elif self.is_last_move:
            base_color = "#ffe066"  # Soft yellow for last move
        elif self.is_valid_move:
            base_color = "#90ee90"  # Light green for valid moves
            
        self.setStyleSheet(f"background-color: {base_color}; border: 1px solid black;")

class StartScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chess Game - Mode Selection")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Chess Game")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36pt; font-weight: bold; margin-bottom: 30px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        subtitle = QLabel("Select Game Mode:")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18pt; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Button container with attractive styling
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 15px;
            }
        """)
        buttons_layout = QVBoxLayout(button_container)
        
        self.human_ai_button = QPushButton("Human vs AI")
        self.human_ai_button.setFixedHeight(70)
        self.human_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 18pt;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        self.ai_ai_button = QPushButton("AI vs AI")
        self.ai_ai_button.setFixedHeight(70)
        self.ai_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 18pt;
                padding: 15px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        buttons_layout.addWidget(self.human_ai_button)
        buttons_layout.addWidget(self.ai_ai_button)
        layout.addWidget(button_container)
        
        self.human_ai_button.clicked.connect(self.choose_human_ai)
        self.ai_ai_button.clicked.connect(self.choose_ai_ai)
        
        self.game_mode = None
        self.setLayout(layout)
    
    def choose_human_ai(self):
        self.game_mode = "human_ai"
        self.accept()
    
    def choose_ai_ai(self):
        self.game_mode = "ai_ai"
        self.accept()
    
    def get_mode(self):
        return self.game_mode

class PawnPromotionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pawn Promotion")
        self.setModal(True)
        self.setFixedSize(300, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout()

        self.label = QLabel("Choose a piece to promote to:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16pt; margin-bottom: 20px; color: #333;")
        layout.addWidget(self.label)

        self.promotion_choice = QComboBox()
        self.promotion_choice.setStyleSheet("""
            QComboBox {
                font-size: 14pt;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        self.promotion_choice.addItems(["Queen", "Rook", "Bishop", "Knight"])
        layout.addWidget(self.promotion_choice)

        self.ok_button = QPushButton("Promote")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_choice(self):
        piece_map = {
            "Queen": "q",
            "Rook": "r",
            "Bishop": "b",
            "Knight": "n"
        }
        return piece_map[self.promotion_choice.currentText()]

class GameOverPopup(QDialog):
    def __init__(self, result, parent=None, custom_message=None):
        super().__init__(parent)
        self.setWindowTitle("Game Over")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  
        self.setModal(True)
        self.setFixedSize(450, 250)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 3px solid #4CAF50;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        if custom_message:
            message = custom_message
            if "AI 1" in message:
                color = "#4CAF50"
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #4CAF50; border-radius: 15px; }")
            elif "AI 2" in message:
                color = "#F44336"
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #F44336; border-radius: 15px; }")
            else:
                color = "#2196F3"
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #2196F3; border-radius: 15px; }")
        else:
            if result == '1-0':
                message = "🏆 Player (White) Wins! 🏆"
                color = "#4CAF50"
            elif result == '0-1':
                message = "❌ AI (Black) Wins! ❌"
                color = "#F44336"
            else:
                message = "🤝 It's a Draw! 🤝"
                color = "#2196F3"

        # Add a decorative header
        header = QLabel("GAME OVER", self)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            font-size: 24pt; 
            font-weight: bold; 
            color: {color}; 
            padding: 10px;
            font-family: 'Arial', sans-serif;
            border-bottom: 2px solid {color};
        """)
        layout.addWidget(header)

        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            font-size: 22pt; 
            font-weight: bold; 
            color: {color}; 
            padding: 20px;
            font-family: 'Arial', sans-serif;
        """)
        layout.addWidget(label)

        ok_button = QPushButton("Close", self)
        ok_button.setCursor(Qt.PointingHandCursor)
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 16pt;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: #{color[1:]}dd;
            }}
            QPushButton:pressed {{
                background-color: #{color[1:]}aa;
            }}
        """)
        ok_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addSpacing(10)

        self.setLayout(layout)

class MoveHistoryWidget(QFrame):
    """Widget to display the move history"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            QListWidget {
                background-color: #f5f5f5;
                font-size: 12pt;
                border: none;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: #333;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Move History")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333; padding: 5px;")
        layout.addWidget(title)
        
        self.move_list = QListWidget()
        self.move_list.setAlternatingRowColors(True)
        layout.addWidget(self.move_list)
        
    def add_move(self, piece, from_square, to_square, color="White", capture=False, check=False, promotion=None):
        """Add a move to the history with proper chess notation"""
        piece_symbols = {
            chess.PAWN: "",
            chess.KNIGHT: "N",
            chess.BISHOP: "B",
            chess.ROOK: "R",
            chess.QUEEN: "Q",
            chess.KING: "K"
        }
        
        notation = ""
        
        # Add move number for White moves
        if color == "White":
            move_number = (self.move_list.count() // 2) + 1
            notation = f"{move_number}. "
        
        # Add piece symbol
        notation += piece_symbols.get(piece.piece_type, "")
        
        # Add capture symbol
        if capture:
            if piece.piece_type == chess.PAWN:
                notation += from_square[0] + "x"
            else:
                notation += "x"
                
        # Add destination square
        notation += to_square
        
        # Add promotion piece
        if promotion:
            notation += "=" + piece_symbols.get(promotion, "")
            
        # Add check/checkmate symbol
        if check:
            notation += "+"
            
        # Format the move in the list
        if color == "White":
            self.move_list.addItem(f"{notation.ljust(12)}")
        else:
            # Update the last item to include the black move
            current_item = self.move_list.item(self.move_list.count() - 1)
            current_text = current_item.text()
            current_item.setText(f"{current_text} {notation}")
            
        # Scroll to the bottom
        self.move_list.scrollToBottom()

    def clear_history(self):
        """Clear the move history"""
        self.move_list.clear()

class ThinkingIndicator(QLabel):
    """Visual indicator for AI thinking state"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #333;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            padding: 10px;
        """)
        self.setFixedHeight(40)
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.hide()
        
    def start_thinking(self, ai_name):
        """Start the thinking animation"""
        self.base_text = f"{ai_name} thinking"
        self.dots = 0
        self.setText(f"{self.base_text}...")
        self.show()
        self.timer.start(300)  # Update dots every 300ms
        
    def stop_thinking(self):
        """Stop the thinking animation"""
        self.timer.stop()
        self.hide()
        
    def update_dots(self):
        """Update the thinking dots animation"""
        self.dots = (self.dots + 1) % 4
        dot_text = "." * self.dots
        self.setText(f"{self.base_text}{dot_text.ljust(3)}")

class ChessBoard(QMainWindow):
    def __init__(self, mode="human_ai"):
        super().__init__()
        
        self.mode = mode
        
        if self.mode == "human_ai":
            self.setWindowTitle("Chess - Human vs AI")
        else:
            self.setWindowTitle("Chess - AI vs AI")
            
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)
        
        self.board = chess.Board()
        self.selected_square = None
        
        if self.mode == "human_ai":
            self.turn = 'human'
        else:
            self.turn = 'ai1'
            
        self.valid_moves = []
        self.last_move_from = None
        self.last_move_to = None
        
        self.ai_game_running = False
        self.move_delay = 800  # Default animation speed
        self.ai_depth = 3  # Default AI search depth

        # Create the main layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # Create the game area
        game_area = QWidget()
        game_layout = QVBoxLayout(game_area)
        game_layout.setSpacing(10)
        
        # Create board container with a nice border
        board_container = QFrame()
        board_container.setFrameShape(QFrame.StyledPanel)
        board_container.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        board_layout = QVBoxLayout(board_container)
        
        # Create board widget
        board_widget = QWidget()
        board_widget.setStyleSheet("background-color: #34495e; padding: 5px; border-radius: 5px;")
        self.board_layout = QGridLayout(board_widget)
        self.board_layout.setSpacing(0)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the squares and labels
        self.squares = []
        # Add column labels (a-h)
        for j in range(8):
            col_label = QLabel(chr(97 + j))  # 'a' through 'h'
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("color: white; font-weight: bold;")
            self.board_layout.addWidget(col_label, 8, j)
            
            # Add row labels (1-8)
            row_label = QLabel(str(8 - j))
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setStyleSheet("color: white; font-weight: bold;")
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
        self.thinking_indicator = ThinkingIndicator()
        
        # Add board widget to container
        board_layout.addWidget(board_widget)
        board_layout.addWidget(self.thinking_indicator)
        
        # Create status label
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 18px; 
            color: #333; 
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            font-weight: bold;
        """)
        
        # Add to game area
        game_layout.addWidget(board_container)
        game_layout.addWidget(self.status_label)
        
        # Create right sidebar for controls and move history
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Create and add move history widget
        self.move_history = MoveHistoryWidget()
        sidebar_layout.addWidget(self.move_history)
        
        # Add AI control panel for AI vs AI mode
        if self.mode == "ai_ai":
            control_panel = QFrame()
            control_panel.setFrameShape(QFrame.StyledPanel)
            control_panel.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                    padding: 10px;
                }
                QLabel {
                    font-size: 12pt;
                    color: #333;
                }
                QSlider {
                    height: 20px;
                }
                QSlider::groove:horizontal {
                    height: 8px;
                    background: #bbb;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #3498db;
                    width: 18px;
                    height: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
            """)
            control_layout = QVBoxLayout(control_panel)
            
            # Add title
            control_title = QLabel("AI Controls")
            control_title.setAlignment(Qt.AlignCenter)
            control_title.setStyleSheet("font-size: 14pt; font-weight: bold; padding-bottom: 10px;")
            control_layout.addWidget(control_title)
            
            # Add button container
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setSpacing(8)
            
            # Style buttons with modern look
            button_style = """
                QPushButton {
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                    color: white;
                }
                QPushButton:hover {
                    opacity: 0.8;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                }
            """
            
            self.start_button = QPushButton("Start")
            self.start_button.setStyleSheet(button_style + "background-color: #27ae60;")
            self.start_button.clicked.connect(self.start_ai_game)
            
            self.pause_button = QPushButton("Pause")
            self.pause_button.setStyleSheet(button_style + "background-color: #f39c12;")
            self.pause_button.clicked.connect(self.pause_ai_game)
            self.pause_button.setEnabled(False)
            
            self.reset_button = QPushButton("Reset")
            self.reset_button.setStyleSheet(button_style + "background-color: #3498db;")
            self.reset_button.clicked.connect(self.reset_game)
            
            button_layout.addWidget(self.start_button)
            button_layout.addWidget(self.pause_button)
            button_layout.addWidget(self.reset_button)
            
            control_layout.addWidget(button_container)
            
            # Add speed slider
            speed_label = QLabel("AI Move Speed:")
            speed_label.setAlignment(Qt.AlignLeft)
            control_layout.addWidget(speed_label)
            
            self.speed_slider = QSlider(Qt.Horizontal)
            self.speed_slider.setMinimum(200)
            self.speed_slider.setMaximum(2000)
            self.speed_slider.setValue(800)
            self.speed_slider.setTickPosition(QSlider.TicksBelow)
            self.speed_slider.setTickInterval(400)
            self.speed_slider.valueChanged.connect(self.update_move_speed)
            control_layout.addWidget(self.speed_slider)
            
            # Add labels for min/max speed
            speed_range = QWidget()
            speed_range_layout = QHBoxLayout(speed_range)
            speed_range_layout.setContentsMargins(0, 0, 0, 0)
            
            fast_label = QLabel("Fast")
            slow_label = QLabel("Slow")
            slow_label.setAlignment(Qt.AlignRight)
            
            speed_range_layout.addWidget(fast_label)
            speed_range_layout.addWidget(slow_label)
            control_layout.addWidget(speed_range)
            
            # Add AI depth control
            depth_label = QLabel("AI Thinking Depth:")
            depth_label.setAlignment(Qt.AlignLeft)
            control_layout.addWidget(depth_label)
            
            self.depth_slider = QSlider(Qt.Horizontal)
            self.depth_slider.setMinimum(2)
            self.depth_slider.setMaximum(5)
            self.depth_slider.setValue(3)
            self.depth_slider.setTickPosition(QSlider.TicksBelow)
            self.depth_slider.setTickInterval(1)
            self.depth_slider.valueChanged.connect(self.update_ai_depth)
            control_layout.addWidget(self.depth_slider)
            
            # Add labels for min/max depth
            depth_range = QWidget()
            depth_range_layout = QHBoxLayout(depth_range)
            depth_range_layout.setContentsMargins(0, 0, 0, 0)
            
            shallow_label = QLabel("Shallow")
            deep_label = QLabel("Deep")
            deep_label.setAlignment(Qt.AlignRight)
            
            depth_range_layout.addWidget(shallow_label)
            depth_range_layout.addWidget(deep_label)
            control_layout.addWidget(depth_range)
            
            # Add current depth display
            self.depth_value = QLabel(f"Current depth: {self.ai_depth}")
            self.depth_value.setAlignment(Qt.AlignCenter)
            self.depth_value.setStyleSheet("font-weight: bold; padding-top: 5px;")
            control_layout.addWidget(self.depth_value)
            
            sidebar_layout.addWidget(control_panel)
        
        # Add everything to main layout
        main_layout.addWidget(game_area, 3)
        main_layout.addWidget(sidebar, 1)
        
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
        
        # Initialize the board
        self.update_board()
    
    def update_move_speed(self, value):
        """Update the AI move animation speed"""
        self.move_delay = value
        if self.ai_game_running:
            self.ai_timer.setInterval(self.move_delay)
    
    def update_ai_depth(self, value):
        """Update the AI thinking depth"""
        self.ai_depth = value
        self.depth_value.setText(f"Current depth: {value}")
    
    def start_ai_game(self):
        """Start the AI vs AI game"""
        if not self.ai_game_running and not self.board.is_game_over():
            self.ai_game_running = True
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.turn = 'ai1' if self.board.turn == chess.WHITE else 'ai2'
            
            # Update status with animated thinking indicator
            ai_name = "AI 1" if self.turn == 'ai1' else "AI 2"
            self.thinking_indicator.start_thinking(ai_name)
            
            # Start the AI move timer
            self.ai_timer.start(self.move_delay)
    
    def pause_ai_game(self):
        """Pause the AI vs AI game"""
        self.ai_game_running = False
        self.ai_timer.stop()
        self.thinking_indicator.stop_thinking()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.status_label.setText("Game paused")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.ai_game_running = False
        self.ai_timer.stop()
        self.thinking_indicator.stop_thinking()
        self.board = chess.Board()
        self.turn = 'ai1'
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
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
        animated_piece.setStyleSheet(f"font-size: 36px; background-color: transparent; color: {piece_color};")
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
        if self.ai_game_running and not self.board.is_game_over():
            # Determine current player
            current_color = "White" if self.board.turn == chess.WHITE else "Black"
            current_ai = "AI 1" if self.turn == 'ai1' else "AI 2"
            
            # Update thinking indicator
            self.thinking_indicator.start_thinking(current_ai)
            
            # Find the best move (run in a non-blocking way)
            fen = self.board.fen()
            
            # Use different engines for different AIs
            if self.turn == 'ai1':
                best_move_uci = find_best_move1(fen, self.ai_depth)
            else:
                best_move_uci = find_best_move2(fen, self.ai_depth)
            
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
                piece_symbol = piece_symbols.get((piece.piece_type, piece.color), "")
                
                # Check if move is a capture
                is_capture = self.board.is_capture(move)
                
                # Start the animation
                self.ai_timer.stop()  # Pause the AI timer during animation
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
                        move.promotion
                    )
                    
                    # Update the board display
                    self.last_move_from = from_pos
                    self.last_move_to = to_pos
                    self.update_board()
                    
                    # Check if game is over
                    if self.board.is_game_over():
                        self.ai_game_running = False
                        self.start_button.setEnabled(False)
                        self.pause_button.setEnabled(False)
                        self.show_game_over_popup()
                    else:
                        # Switch to next AI
                        self.turn = 'ai2' if self.turn == 'ai1' else 'ai1'
                        
                        # Resume the AI timer for next move
                        self.ai_timer.start(self.move_delay)
                
                # Animate the piece movement
                self.animate_piece_movement(from_pos, to_pos, piece_symbol, piece_color, is_capture, after_animation)
            else:
                # No valid move found
                self.ai_game_running = False
                self.ai_timer.stop()
                self.thinking_indicator.stop_thinking()
                self.status_label.setText("No valid moves available")
        else:
            # Game is over or paused
            self.ai_timer.stop()
            self.thinking_indicator.stop_thinking()
    
    def find_valid_moves(self, from_square):
        """Find all valid moves for a piece on the given square"""
        valid_moves = []
        from_square_index = chess.parse_square(from_square)
        
        for move in self.board.legal_moves:
            if move.from_square == from_square_index:
                valid_moves.append(move)
                
        return valid_moves

    def update_board(self):
        """Update the visual representation of the chess board"""
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

        selected = chess.parse_square(self.selected_square) if self.selected_square else None
        valid_destinations = [move.to_square for move in self.valid_moves]

        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)
                piece = self.board.piece_at(square)
                square_widget = self.squares[i][j]

                # Reset states
                square_widget.is_selected = False
                square_widget.is_last_move = False
                square_widget.is_valid_move = False
                
                # Set states based on game state
                if selected == square:
                    square_widget.is_selected = True
                if (i, j) == self.last_move_from or (i, j) == self.last_move_to:
                    square_widget.is_last_move = True
                if square in valid_destinations:
                    square_widget.is_valid_move = True
                    
                # Update the square appearance
                square_widget.update_appearance()
                
                # Draw piece or empty square
                if piece:
                    symbol = piece_symbols.get((piece.piece_type, piece.color), "")
                    piece_color = "#000000" if piece.color == chess.BLACK else "#FFFFFF"
                    square_widget.setText(symbol)
                    square_widget.setStyleSheet(square_widget.styleSheet() + f"font-size: 36px; color: {piece_color};")
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
                if self.mode == "ai_ai":
                    self.start_button.setEnabled(False)
                    self.pause_button.setEnabled(False)
                    self.show_game_over_popup()
        else:
            # Update status label based on turn
            if self.mode == "human_ai":
                if self.turn == 'human':
                    self.status_label.setText("Your turn")
                    self.thinking_indicator.stop_thinking()
                else:
                    self.status_label.setText("AI is thinking...")
                    self.thinking_indicator.start_thinking("AI")
            else:
                if not self.ai_game_running:
                    self.thinking_indicator.stop_thinking()
                    if self.turn == 'ai1':
                        self.status_label.setText("Press 'Start' to begin AI vs AI game")
                    else:
                        self.status_label.setText("Press 'Start' to continue AI vs AI game")

    def player_move(self, i, j):
        """Handle player move selection"""
        if self.mode != "human_ai" or self.turn != 'human' or self.board.is_game_over():
            return
            
        square = chess.square(j, 7 - i)
        current_square = chess.SQUARE_NAMES[square]

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = current_square
                self.valid_moves = self.find_valid_moves(current_square)
                self.update_board()
        else:
            if self.selected_square == current_square:
                self.selected_square = None
                self.valid_moves = []
                self.update_board()
                return
                
            move_made = False
            for move in self.valid_moves:
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
                    
                    # Get animation info
                    from_pos = (7 - chess.square_rank(from_square), chess.square_file(from_square))
                    to_pos = (7 - chess.square_rank(square), chess.square_file(square))
                    
                    # Determine piece symbol for animation
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
                    piece_symbol = piece_symbols.get((piece.piece_type, piece.color), "")
                    piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#000000"
                    is_capture = self.board.is_capture(move)
                    
                    # Reset selection
                    self.selected_square = None
                    self.valid_moves = []
                    
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
                            move.promotion if is_promotion else None
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
                            
                            # Update status with "thinking" animation
                            self.thinking_indicator.start_thinking("AI")
                            
                            # Allow UI to update before AI starts computing
                            QTimer.singleShot(800, self.ai_move)
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
                    self.valid_moves = self.find_valid_moves(current_square)
                else:
                    # Invalid move - deselect
                    self.valid_moves = []
                    self.selected_square = None
                
                self.update_board()

    def ai_move(self):
        """Calculate and execute the AI's move"""
        try:
            # Update status with thinking animation
            self.thinking_indicator.start_thinking("AI")
            
            fen = self.board.fen()

            # Check if game is already over
            if self.board.is_game_over():
                self.thinking_indicator.stop_thinking()
                self.show_game_over_popup()
                return

            # Find best move
            best_move_uci = find_best_move1(fen, self.ai_depth)

            if best_move_uci:
                move = chess.Move.from_uci(best_move_uci)
                
                # Get animation info
                from_square = move.from_square
                to_square = move.to_square
                piece = self.board.piece_at(from_square)
                
                from_pos = (7 - chess.square_rank(from_square), chess.square_file(from_square))
                to_pos = (7 - chess.square_rank(to_square), chess.square_file(to_square))
                
                # Determine piece symbol and color for animation
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
                piece_symbol = piece_symbols.get((piece.piece_type, piece.color), "")
                piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#000000"
                is_capture = self.board.is_capture(move)
                
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
                        move.promotion
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
        except Exception as e:
            self.thinking_indicator.stop_thinking()
            self.status_label.setText(f"Error during AI move: {str(e)}")

    def show_game_over_popup(self):
        """Show the game over popup with appropriate message"""
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
        
        if self.popup.exec_() == QDialog.Accepted:
            if self.mode == "human_ai":
                self.close_game()
            else:
                self.reset_game()

    def close_game(self):
        """Close the game window"""
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")  # Use Fusion style for better cross-platform look
    
    # Apply custom palette for better overall aesthetics
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
    app.setPalette(palette)
    
    start_screen = StartScreen()
    if start_screen.exec_() == QDialog.Accepted:
        mode = start_screen.get_mode()
        if mode:
            window = ChessBoard(mode)
            window.show()
            app.exec_()
    else:
        sys.exit()