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
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
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


class GameOverPopup(BaseDialog):
    """Enhanced game over popup with visual effects and clear actions."""
    
    play_again_signal = pyqtSignal()
    return_home_signal = pyqtSignal()
    save_game_signal = pyqtSignal()
    
    def __init__(self, result, parent=None, custom_message=None):
        super().__init__("Game Over", parent)
        self.setFixedSize(450, 480)  # Made taller for additional content
        
        # Set color scheme based on result
        if custom_message:
            message = custom_message
            if "AI 1" in message or "White" in message:
                self.result_color = "#4CAF50"  # Green for white
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #4CAF50; border-radius: 30px; }")
            elif "AI 2" in message or "Black" in message:
                self.result_color = "#F44336"  # Red for black
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #F44336; border-radius: 30px; }")
            else:
                self.result_color = "#2196F3"  # Blue for draw
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #2196F3; border-radius: 30px; }")
        else:
            if result == '1-0':
                message = "🏆 Player (White) Wins! 🏆"
                self.result_color = "#4CAF50"  # Green for white
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #4CAF50; border-radius: 30px; }")
            elif result == '0-1':
                message = "❌ AI (Black) Wins! ❌"
                self.result_color = "#F44336"  # Red for black
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #F44336; border-radius: 30px; }")
            else:
                message = "🤝 It's a Draw! 🤝"
                self.result_color = "#2196F3"  # Blue for draw
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #2196F3; border-radius: 30px; }")

        # Add a decorative header
        header = QLabel("GAME OVER", self)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            font-size: 28pt; 
            font-weight: bold; 
            color: {self.result_color}; 
            padding: 10px;
            font-family: 'Arial', sans-serif;
            border-bottom: 2px solid {self.result_color};
        """)
        self.content_layout.addWidget(header)

        # Result message
        result_label = QLabel(message, self)
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setStyleSheet(f"""
            font-size: 22pt; 
            font-weight: bold; 
            color: {self.result_color}; 
            padding: 20px;
            font-family: 'Arial', sans-serif;
        """)
        self.content_layout.addWidget(result_label)
        
        # Add game statistics if available
        if hasattr(self.parent(), 'board') and self.parent().board:
            stats_frame = QFrame()
            stats_frame.setFrameShape(QFrame.StyledPanel)
            stats_frame.setStyleSheet(f"""
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                padding: 10px;
            """)
            
            stats_layout = QVBoxLayout(stats_frame)
            stats_layout.setSpacing(5)
            
            # Add stats heading
            stats_heading = QLabel("Game Statistics")
            stats_heading.setAlignment(Qt.AlignCenter)
            stats_heading.setStyleSheet("""
                font-size: 14pt;
                font-weight: bold;
                color: #495057;
                margin-bottom: 5px;
            """)
            stats_layout.addWidget(stats_heading)
            
            # Get move count
            move_count = len(self.parent().board.move_stack)
            stats_text = QLabel(f"Total Moves: {move_count}")
            stats_text.setAlignment(Qt.AlignCenter)
            stats_text.setStyleSheet("""
                font-size: 12pt;
                color: #495057;
            """)
            stats_layout.addWidget(stats_text)
            
            # Add the stats frame
            self.content_layout.addWidget(stats_frame)
        
        # Add spacer
        self.content_layout.addSpacing(10)
        
        # Button styles
        button_style = f"""
            QPushButton {{
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.7;
            }}
        """
        
        # Save Game button
        self.save_game_button = QPushButton("Save This Game", self)
        self.save_game_button.setCursor(Qt.PointingHandCursor)
        self.save_game_button.setStyleSheet(f"""
            {button_style}
            background-color: #16a085;
        """)
        self.save_game_button.clicked.connect(self.save_game)
        
        # Play Again button
        self.play_again_button = QPushButton("Play Again", self)
        self.play_again_button.setCursor(Qt.PointingHandCursor)
        self.play_again_button.setStyleSheet(f"""
            {button_style}
            background-color: {self.result_color};
        """)
        self.play_again_button.clicked.connect(self.play_again)
        
        # Return Home button
        self.return_home_button = QPushButton("Return to Home", self)
        self.return_home_button.setCursor(Qt.PointingHandCursor)
        self.return_home_button.setStyleSheet(f"""
            {button_style}
            background-color: #607D8B;
        """)
        self.return_home_button.clicked.connect(self.return_home)
        
        # Button container with first button full width
        action_layout = QVBoxLayout()
        action_layout.setSpacing(10)
        
        # First button full width
        action_layout.addWidget(self.save_game_button)
        
        # Second row of buttons side by side
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addWidget(self.play_again_button)
        button_row.addWidget(self.return_home_button)
        action_layout.addLayout(button_row)
        
        self.content_layout.addLayout(action_layout)
        
        # Add drop shadow to all buttons
        for button in [self.save_game_button, self.play_again_button, self.return_home_button]:
            shadow = QGraphicsDropShadowEffect(button)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 5)
            button.setGraphicsEffect(shadow)
        
        # Remove the default button container
        self.button_container.hide()
        
        # Animate the dialog appearance
        self.animate_appearance()
    
    def animate_appearance(self):
        """Animate the dialog appearing with a fade-in effect."""
        self.setWindowOpacity(0.0)
        
        # Create and configure animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
    def save_game(self):
        self.save_game_signal.emit()
        self.accept()
    
    def play_again(self):
        self.play_again_signal.emit()
        self.accept()
    
    def return_home(self):
        self.return_home_signal.emit()
        self.accept()
    
    def closeEvent(self, event):
        """Override to ensure proper cleanup when the dialog is closed."""
        # Disconnect all signals to prevent memory leaks
        try:
            self.play_again_signal.disconnect()
            self.return_home_signal.disconnect()
            self.save_game_signal.disconnect()
        except Exception:
            pass  # It's okay if they're not connected
        super().closeEvent(event)


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