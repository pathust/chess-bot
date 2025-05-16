"""
Dialog and popup components for the chess application.
This module provides various dialog and popup windows for user interaction.
"""

import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QWidget, QLineEdit, QFormLayout, QMessageBox, QSpacerItem,
    QComboBox, QGraphicsDropShadowEffect, QTextEdit, QScrollArea,
    QFrame, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve, QSize
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter, QPainterPath

from utils.config import Config

class BaseDialog(QDialog):
    """Base dialog class with common styling and functionality."""
    
    def __init__(self, title, parent=None, modal=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        if modal:
            self.setModal(True)
        
        # Remove window decoration for custom styling
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Set up base styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 15px;
                border: 2px solid #3498db;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
                background-color: white;
                font-size: 12pt;
            }
        """)
        
        # Add shadow for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Title bar
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 20pt;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        
        title_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.title_bar)
        
        # Content area - to be filled by subclasses
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_widget)
        
        # Button container
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setSpacing(15)
        self.main_layout.addWidget(self.button_container)
        
    def add_close_button(self, text="Close", accent_color="#e74c3c"):
        """Add a close button to the dialog."""
        close_button = QPushButton(text)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(accent_color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(accent_color)};
            }}
        """)
        close_button.clicked.connect(self.reject)
        self.button_layout.addWidget(close_button)
        return close_button
    
    def _lighten_color(self, color, factor=1.1):
        """Lighten a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(int(color[0:2], 16) * factor))
        g = min(255, int(int(color[2:4], 16) * factor))
        b = min(255, int(int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor=1.1):
        """Darken a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(int(color[0:2], 16) / factor))
        g = max(0, int(int(color[2:4], 16) / factor))
        b = max(0, int(int(color[4:6], 16) / factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def mousePressEvent(self, event):
        """Track mouse press events for window dragging."""
        if self.title_bar.geometry().contains(event.pos()):
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for window dragging."""
        if hasattr(self, '_drag_position') and self._drag_position is not None:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Reset drag tracking on mouse release."""
        self._drag_position = None
        super().mouseReleaseEvent(event)


class SaveGameDialog(BaseDialog):
    """Enhanced dialog for saving a game with name and notes."""
    
    def __init__(self, parent=None):
        super().__init__("Save Your Game", parent)
        
        # Form for game details
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setSpacing(12)
        
        # Game name field
        self.game_name = QLineEdit()
        self.game_name.setPlaceholderText("Enter a name for your saved game")
        form_layout.addRow("Game Name:", self.game_name)
        
        # Notes field (multiline)
        self.game_notes = QTextEdit()
        self.game_notes.setPlaceholderText("Add optional notes about this game")
        self.game_notes.setMaximumHeight(120)
        form_layout.addRow("Notes:", self.game_notes)
        
        self.content_layout.addLayout(form_layout)
        
        # Add some spacing
        self.content_layout.addItem(QSpacerItem(20, 20))
        
        # Buttons
        save_button = QPushButton("Save Game")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        save_button.clicked.connect(self.accept)
        self.button_layout.addWidget(save_button)
        
        cancel_button = self.add_close_button("Cancel", "#e74c3c")
        
        # Set the game name field as initial focus
        self.game_name.setFocus()
    
    def get_game_name(self):
        """Return the entered game name or a default if empty."""
        name = self.game_name.text().strip()
        if not name:
            import datetime
            return f"Chess Game - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        return name
    
    def get_game_notes(self):
        """Return any game notes entered."""
        return self.game_notes.toPlainText().strip()


class StartScreen(BaseDialog):
    """Initial screen to select game mode or load a saved game."""
    
    def __init__(self, parent=None):
        super().__init__("Chess Game - Mode Selection", parent)
        self.setFixedSize(500, 500)
        
        # Style title as chess title
        self.title_label.setText("♚ Chess Game ♔")
        self.title_label.setStyleSheet("""
            font-size: 36pt; 
            font-weight: bold; 
            margin-bottom: 30px; 
            color: #2c3e50;
        """)
        
        subtitle = QLabel("Select Game Mode:")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18pt; margin-bottom: 30px;")
        self.content_layout.addWidget(subtitle)
        
        # Button container with attractive styling
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 15px;
            }
        """)
        buttons_layout = QVBoxLayout(button_container)
        buttons_layout.setSpacing(20)
        
        self.human_ai_button = QPushButton("Human vs AI")
        self.human_ai_button.setFixedHeight(70)
        self.human_ai_button.setCursor(Qt.PointingHandCursor)
        self.human_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 18pt;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
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
        self.ai_ai_button.setCursor(Qt.PointingHandCursor)
        self.ai_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 18pt;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Add Load Game button
        self.load_game_button = QPushButton("Load Saved Game")
        self.load_game_button.setFixedHeight(70)
        self.load_game_button.setCursor(Qt.PointingHandCursor)
        self.load_game_button.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                font-size: 18pt;
                padding: 15px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
            QPushButton:pressed {
                background-color: #0e6655;
            }
        """)
        
        buttons_layout.addWidget(self.human_ai_button)
        buttons_layout.addWidget(self.ai_ai_button)
        buttons_layout.addWidget(self.load_game_button)
        
        self.content_layout.addWidget(button_container)
        
        # Add shadow effects to buttons
        for button in [self.human_ai_button, self.ai_ai_button, self.load_game_button]:
            shadow = QGraphicsDropShadowEffect(button)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 5)
            button.setGraphicsEffect(shadow)
        
        self.human_ai_button.clicked.connect(self.choose_human_ai)
        self.ai_ai_button.clicked.connect(self.choose_ai_ai)
        
        self.game_mode = None
        
        # Remove the default button container since we're using custom buttons
        self.button_container.hide()
    
    def choose_human_ai(self):
        self.game_mode = Config.MODE_HUMAN_AI
        self.accept()
    
    def choose_ai_ai(self):
        self.game_mode = Config.MODE_AI_AI
        self.accept()
    
    def get_mode(self):
        return self.game_mode


class PawnPromotionDialog(BaseDialog):
    """Dialog for selecting a piece during pawn promotion."""
    
    def __init__(self, parent=None):
        super().__init__("Pawn Promotion", parent)
        self.setFixedSize(300, 350)
        
        # Instructions
        self.label = QLabel("Choose a piece to promote to:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16pt; margin-bottom: 20px; color: #333;")
        self.content_layout.addWidget(self.label)
        
        # Create piece buttons
        piece_layout = QHBoxLayout()
        piece_layout.setSpacing(10)
        
        piece_data = [
            ("Queen", "♛", "#9c27b0"),  # Purple
            ("Rook", "♜", "#f44336"),   # Red
            ("Bishop", "♝", "#2196f3"), # Blue
            ("Knight", "♞", "#4caf50")  # Green
        ]
        
        self.piece_buttons = {}
        for piece_name, symbol, color in piece_data:
            piece_button = QPushButton(symbol)
            piece_button.setFixedSize(60, 60)
            piece_button.setCursor(Qt.PointingHandCursor)
            piece_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {color};
                    font-size: 30pt;
                    border-radius: 5px;
                    border: 2px solid {color};
                }}
                QPushButton:hover {{
                    background-color: {self._lighten_color(color, 0.9)};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: {color};
                    color: white;
                }}
            """)
            
            # Add shadow for depth
            shadow = QGraphicsDropShadowEffect(piece_button)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 70))
            shadow.setOffset(0, 5)
            piece_button.setGraphicsEffect(shadow)
            
            piece_button.clicked.connect(lambda _, p=piece_name.lower()[0]: self.select_piece(p))
            piece_layout.addWidget(piece_button)
            self.piece_buttons[piece_name.lower()[0]] = piece_button
        
        self.content_layout.addLayout(piece_layout)
        
        # Add piece labels
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(10)
        
        for piece_name, _, _ in piece_data:
            label = QLabel(piece_name)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333;")
            labels_layout.addWidget(label)
        
        self.content_layout.addLayout(labels_layout)
        self.content_layout.addSpacing(20)
        
        # Remove default button container
        self.button_container.hide()
        
        # Selected piece (default to queen)
        self.selected_piece = "q"
    
    def select_piece(self, piece):
        """Handle piece selection and close the dialog."""
        self.selected_piece = piece
        self.accept()
    
    def get_choice(self):
        """Return the selected promotion piece."""
        return self.selected_piece


class GameOverPopup(QDialog):
    """Simple and reliable game over popup with play again and return home options."""
    
    play_again_signal = pyqtSignal()
    return_home_signal = pyqtSignal()
    
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Over")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
        """)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Determine the result message
        if result == '1-0':
            message = "White Wins!"
            result_color = "#4CAF50"  # Green for white
        elif result == '0-1':
            message = "Black Wins!"
            result_color = "#F44336"  # Red for black
        else:
            message = "It's a Draw!"
            result_color = "#2196F3"  # Blue for draw
        
        # Game over title
        title = QLabel("GAME OVER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 24pt; 
            font-weight: bold; 
            color: {result_color}; 
        """)
        layout.addWidget(title)
        
        # Result message
        result_label = QLabel(message)
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setStyleSheet(f"""
            font-size: 20pt; 
            font-weight: bold; 
            color: {result_color}; 
            padding: 10px;
        """)
        layout.addWidget(result_label)
        
        # Add spacer
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.play_again_button = QPushButton("Play Again")
        self.play_again_button.setCursor(Qt.PointingHandCursor)
        self.play_again_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {result_color};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """)
        self.play_again_button.clicked.connect(self.play_again)
        
        self.return_home_button = QPushButton("Return to Home")
        self.return_home_button.setCursor(Qt.PointingHandCursor)
        self.return_home_button.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.return_home_button.clicked.connect(self.return_home)
        
        button_layout.addWidget(self.play_again_button)
        button_layout.addWidget(self.return_home_button)
        
        layout.addLayout(button_layout)
    
    def play_again(self):
        """Emit signal to play again and close the dialog"""
        self.play_again_signal.emit()
        self.accept()
    
    def return_home(self):
        """Emit signal to return to home screen and close the dialog"""
        self.return_home_signal.emit()
        self.accept()

        
# Enhance the ResignConfirmationDialog for better user experience
class ResignConfirmationDialog(BaseDialog):
    """Dialog to confirm resignation from a game."""
    
    def __init__(self, parent=None):
        super().__init__("Confirm Resignation", parent)
        self.setFixedSize(400, 250)
        
        # Warning message
        warning = QLabel("Are you sure you want to resign this game?")
        warning.setAlignment(Qt.AlignCenter)
        warning.setStyleSheet("""
            font-size: 16pt;
            color: #e74c3c;
            margin: 20px 0;
        """)
        self.content_layout.addWidget(warning)
        
        # Explanation
        explanation = QLabel("Resigning means you forfeit the game and your opponent will be declared the winner.")
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        explanation.setStyleSheet("""
            font-size: 12pt;
            color: #34495e;
            margin: 10px 0;
        """)
        self.content_layout.addWidget(explanation)
        
        # Buttons
        resign_button = QPushButton("Yes, Resign")
        resign_button.setCursor(Qt.PointingHandCursor)
        resign_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        resign_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #717d7e;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        self.button_layout.addWidget(resign_button)
        self.button_layout.addWidget(cancel_button)
        
        # Add shadow effects to buttons
        for button in [resign_button, cancel_button]:
            shadow = QGraphicsDropShadowEffect(button)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 70))
            shadow.setOffset(0, 5)
            button.setGraphicsEffect(shadow)


class ResignConfirmationDialog(BaseDialog):
    """Dialog to confirm resignation from a game."""
    
    def __init__(self, parent=None):
        super().__init__("Confirm Resignation", parent)
        self.setFixedSize(400, 300)  # Slightly taller to accommodate all content properly
        
        # Create main content container with explicit white background
        content_container = QFrame()
        content_container.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 5px;
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(15)
        
        # Create proper warning label with fixed text
        warning = QLabel("Are you sure you want to resign this game?", content_container)
        warning.setAlignment(Qt.AlignCenter)
        warning.setWordWrap(True)
        warning.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #e74c3c;
            background-color: #fef5f5;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        """)
        content_layout.addWidget(warning)
        
        # Explanation with better styling
        explanation = QLabel("Resigning means you forfeit the game and your opponent will be declared the winner.", content_container)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        explanation.setStyleSheet("""
            font-size: 12pt;
            color: #34495e;
            padding: 5px;
            margin: 5px;
        """)
        content_layout.addWidget(explanation)
        
        # Add the content container to the main layout
        self.content_layout.addWidget(content_container)
        
        # Create compact button size but maintain readability
        button_size = QSize(160, 45)  # Smaller button size
        
        # Buttons with better spacing
        resign_button = QPushButton("Yes, Resign")
        resign_button.setCursor(Qt.PointingHandCursor)
        resign_button.setFixedSize(button_size)
        resign_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #c0392b;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        resign_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setFixedSize(button_size)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #6c7a7d;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #717d7e;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        # Set button layout with proper spacing
        self.button_layout.setSpacing(15)
        self.button_layout.setContentsMargins(10, 0, 10, 10)
        self.button_layout.addWidget(resign_button)
        self.button_layout.addWidget(cancel_button)
        
        # Add shadow effects to buttons
        for button in [resign_button, cancel_button]:
            shadow = QGraphicsDropShadowEffect(button)
            shadow.setBlurRadius(10)  # Reduced blur for smaller buttons
            shadow.setColor(QColor(0, 0, 0, 70))
            shadow.setOffset(0, 4)  # Reduced offset for smaller buttons
            button.setGraphicsEffect(shadow)