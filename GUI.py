from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QLabel, QVBoxLayout, 
    QHBoxLayout, QComboBox, QPushButton, QDialog, QWidget, QSlider,
    QListWidget, QSplitter, QFrame, QGraphicsOpacityEffect, QListWidgetItem,
    QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal, QSize, QThread, QRect
from PyQt5.QtGui import QColor, QIcon, QFont, QPalette, QBrush, QFontDatabase
import chess
import sys
import time
import os
from chess_engine import find_best_move as find_best_move1
from chess_engine2 import find_best_move as find_best_move2

# Thread class for AI computation to prevent GUI freezing
class AIWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, fen, depth, engine_num=1):
        super().__init__()
        self.fen = fen
        self.depth = depth
        self.engine_num = engine_num
        
    def run(self):
        try:
            if self.engine_num == 1:
                result = find_best_move1(self.fen, self.depth)
            else:
                result = find_best_move2(self.fen, self.depth)
            self.finished.emit(result)
        except Exception as e:
            print(f"AI Worker error: {str(e)}")
            self.finished.emit("")

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
        self.is_castling_move = False
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
        elif self.is_castling_move:
            base_color = "#ff9966"  # Orange for castling moves
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
                color: #333;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                color: #333;
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
    play_again_signal = pyqtSignal()
    return_home_signal = pyqtSignal()
    
    def __init__(self, result, parent=None, custom_message=None):
        super().__init__(parent)
        self.setWindowTitle("Game Over")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  
        self.setModal(True)
        self.setFixedSize(450, 300)  # Made taller for additional buttons
        
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

        # Button container
        button_layout = QHBoxLayout()
        
        # Play Again button
        self.play_again_button = QPushButton("Play Again", self)
        self.play_again_button.setCursor(Qt.PointingHandCursor)
        self.play_again_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px 20px;
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
        self.play_again_button.clicked.connect(self.play_again)
        
        # Return Home button
        self.return_home_button = QPushButton("Return to Home", self)
        self.return_home_button.setCursor(Qt.PointingHandCursor)
        self.return_home_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #607D8B;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background-color: #78909C;
            }}
            QPushButton:pressed {{
                background-color: #455A64;
            }}
        """)
        self.return_home_button.clicked.connect(self.return_home)
        
        button_layout.addWidget(self.play_again_button)
        button_layout.addWidget(self.return_home_button)
        
        layout.addLayout(button_layout)
        layout.addSpacing(10)

        self.setLayout(layout)
    
    def play_again(self):
        self.play_again_signal.emit()
        self.accept()
    
    def return_home(self):
        self.return_home_signal.emit()
        self.accept()

class MoveHistoryWidget(QFrame):
    """Widget to display the move history with improved contrast"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cccccc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Title container with improved visibility
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                border: 1px solid #1a2530;
            }
        """)
        
        title_layout = QVBoxLayout(title_container)
        
        # Title label
        title = QLabel("Move History")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: white; 
            padding: 5px;
        """)
        title_layout.addWidget(title)
        layout.addWidget(title_container)
        
        # Custom styled list widget
        self.move_list = QListWidget()
        self.move_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                alternate-background-color: #f0f0f0;
                font-size: 14pt;
                font-family: 'Arial', monospace;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                color: #222222;
                padding: 5px;
                border-bottom: 1px solid #e0e0e0;
                min-height: 30px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6f7ff;
            }
            QListWidget::item:alternate {
                background-color: #f5f5f5;
            }
        """)
        self.move_list.setAlternatingRowColors(True)
        layout.addWidget(self.move_list)
        
    def add_move(self, piece, from_square, to_square, color="White", capture=False, check=False, promotion=None, castling=False):
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
        
        # Handle castling notation
        if castling:
            if to_square[0] > from_square[0]:  # King-side castling
                notation += "O-O"
            else:  # Queen-side castling
                notation += "O-O-O"
        else:
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
            
        # Format the move in the list with improved styling
        if color == "White":
            item = QListWidgetItem(f"{notation.ljust(12)}")
            item_color = "#0000aa"  # Dark blue for white's moves
            item.setForeground(QBrush(QColor(item_color)))
            self.move_list.addItem(item)
        else:
            # Update the last item to include the black move
            current_item = self.move_list.item(self.move_list.count() - 1)
            if current_item:
                current_text = current_item.text()
                combined_text = f"{current_text} {notation}"
                current_item.setText(combined_text)
                
                # Apply custom styling with a bold font
                font = current_item.font()
                font.setBold(True)
                current_item.setFont(font)
            
        # Scroll to the bottom
        self.move_list.scrollToBottom()

    def clear_history(self):
        """Clear the move history"""
        self.move_list.clear()

class ThinkingIndicator(QLabel):
    """Visual indicator for AI thinking state with improved visibility"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: white;
            background-color: rgba(52, 73, 94, 0.8);
            border-radius: 10px;
            padding: 10px;
            border: 1px solid white;
            margin: 0px;
        """)
        self.setFixedHeight(50)
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

class ControlButton(QPushButton):
    """Enhanced button with better visual feedback"""
    def __init__(self, text, color, icon=None, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)  # Adjusted for better appearance on small screens
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        
        self.updateStyle()
    
    def updateStyle(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self.base_color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(self.base_color, 1.1)};
            }}
            QPushButton:disabled {{
                background-color: #bbbbbb;
                color: #dddddd;
            }}
        """)
    
    def _lighten_color(self, color, factor):
        # Simple implementation to lighten a hex color
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(int(color[0:2], 16) * factor))
        g = min(255, int(int(color[2:4], 16) * factor))
        b = min(255, int(int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor):
        # Simple implementation to darken a hex color
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(int(color[0:2], 16) / factor))
        g = max(0, int(int(color[2:4], 16) / factor))
        b = max(0, int(int(color[4:6], 16) / factor))
        return f"#{r:02x}{g:02x}{b:02x}"

# Modify the slider label colors for better visibility
class EnhancedSlider(QWidget):
    """Custom slider with better visual design and labels"""
    valueChanged = pyqtSignal(int)
    
    def __init__(self, title, min_val, max_val, default_val, min_label, max_label, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with improved visibility
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: #e8e8e8;
                border-radius: 6px;
                border: 1px solid #cccccc;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 12pt; 
            font-weight: bold; 
            color: #333333;
        """)
        title_layout.addWidget(title_label)
        layout.addWidget(title_container)
        
        # Create the styled slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval((max_val - min_val) // 4)
        self.slider.setStyleSheet("""
            QSlider {
                height: 25px;
                margin: 5px 0;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #d0d0d0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
                border: 1px solid #1976D2;
            }
            QSlider::sub-page:horizontal {
                background: #64B5F6;
                border-radius: 4px;
            }
        """)
        self.slider.valueChanged.connect(self._emit_value_changed)
        layout.addWidget(self.slider)
        
        # Add min/max labels with IMPROVED CONTRAST
        labels_layout = QHBoxLayout()
        min_text = QLabel(min_label)
        min_text.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")  # Changed to white for better contrast
        
        max_text = QLabel(max_label)
        max_text.setAlignment(Qt.AlignRight)
        max_text.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")  # Changed to white for better contrast
        
        labels_layout.addWidget(min_text)
        labels_layout.addWidget(max_text)
        layout.addLayout(labels_layout)
        
    def _emit_value_changed(self, value):
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
    
    def setValue(self, value):
        self.slider.setValue(value)

# Redesigned AI Control Panel with responsive layout
class AIControlPanel(QScrollArea):
    """AI control panel with improved responsive design"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #2c3e50;  /* Darker blue background for better contrast */
                border-radius: 10px;
                border: 2px solid #1a2530;  /* Darker border */
            }
        """)
        
        # Create inner widget for the scroll area
        inner_widget = QWidget()
        inner_widget.setStyleSheet("background-color: #2c3e50;")  
        self.setWidget(inner_widget)
        
        # Create main layout with adaptive spacing
        main_layout = QVBoxLayout(inner_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title header
        title = QLabel("AI Controls")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: white; 
            padding: 8px;
            background-color: #34495e;  /* Slightly lighter than panel for contrast */
            border-radius: 6px;
        """)
        main_layout.addWidget(title)
                
        # Create a responsive layout that can adapt to window width
        responsive_container = QWidget()
        responsive_layout = QHBoxLayout(responsive_container)
        responsive_layout.setSpacing(10)
        
        # Create button container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(8)
        
        # Start button - brighter green
        self.start_button = ControlButton("▶ Start", "#2ecc71")  # Brighter green

        # Pause button - brighter orange
        self.pause_button = ControlButton("⏸ Pause", "#f39c12")  # Brighter orange

        # Reset button - brighter blue
        self.reset_button = ControlButton("↻ Reset", "#3498db")  # Brighter blue

        # Return to Home button - brighter red
        self.home_button = ControlButton("🏠 Home", "#e74c3c")  # Brighter red
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.home_button)
        button_layout.addStretch(1)
        
        # Add button container to responsive layout
        responsive_layout.addWidget(button_container, 1)
        
        # Create slider container
        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setSpacing(10)
        
        # Create enhanced sliders
        self.speed_slider = EnhancedSlider(
            "AI Move Speed:", 200, 2000, 800, "Fast", "Slow"
        )
        slider_layout.addWidget(self.speed_slider)
        
        self.depth_slider = EnhancedSlider(
            "AI Thinking Depth:", 2, 5, 3, "Shallow", "Deep"
        )
        slider_layout.addWidget(self.depth_slider)
        
        # Add current depth display with improved visibility
        depth_container = QFrame()
        depth_container.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 5px;
                padding: 6px;
            }
        """)
        
        depth_layout = QVBoxLayout(depth_container)
        self.depth_value = QLabel("Current depth: 3")
        self.depth_value.setAlignment(Qt.AlignCenter)
        self.depth_value.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: white;
            padding: 2px;
        """)
        depth_layout.addWidget(self.depth_value)
        slider_layout.addWidget(depth_container)
        slider_layout.addStretch(1)
        
        # Add slider container to responsive layout
        responsive_layout.addWidget(slider_container, 1)
        
        # Add responsive container to main layout
        main_layout.addWidget(responsive_container)
        
        # Set resize behavior to adapt to parent size
        responsive_layout.setStretch(0, 1)
        responsive_layout.setStretch(1, 1)

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

class ChessApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.setStyle("Fusion")  # Use Fusion style for better cross-platform look
        
        # Apply custom palette for better overall aesthetics
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(44, 62, 80))
        palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.Button, QColor(52, 73, 94))
        palette.setColor(QPalette.ButtonText, QColor(236, 240, 241))
        self.setPalette(palette)
        
        # Load a standard font that will be available on all systems
        self.setFont(QFont("Arial", 10))
        
        self.chess_window = None
        self.show_start_screen()
    
    def show_start_screen(self):
        """Show the start screen to select game mode"""
        # Close any existing chess window
        if self.chess_window:
            self.chess_window.close()
            self.chess_window = None
            
        start_screen = StartScreen()
        if start_screen.exec_() == QDialog.Accepted:
            mode = start_screen.get_mode()
            if mode:
                self.chess_window = ChessBoard(mode, self)
                self.chess_window.show()

if __name__ == "__main__":
    app = ChessApp(sys.argv)
    sys.exit(app.exec_())