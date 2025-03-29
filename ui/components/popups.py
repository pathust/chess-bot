from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class StartScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chess Game - Mode Selection")
        self.setModal(True)
        self.setFixedSize(500, 500)  # Increased height for additional button
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
                margin-bottom: 20px;
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
        # Bảo đảm rằng combo box có một lựa chọn
        selection = self.promotion_choice.currentText()
        if not selection:
            return "q"  # Mặc định là Hậu nếu không có lựa chọn
        return piece_map.get(selection, "q")

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
                border-radius: 30px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        if custom_message:
            message = custom_message
            if "AI 1" in message:
                color = "#4CAF50"
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #4CAF50; border-radius: 30px; }")
            elif "AI 2" in message:
                color = "#F44336"
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #F44336; border-radius: 30px; }")
            else:
                color = "#2196F3"
                self.setStyleSheet("QDialog { background-color: white; border: 3px solid #2196F3; border-radius: 30px; }")
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
        self.close()  # Force close the dialog

    def closeEvent(self, event):
        """Override to ensure proper cleanup when the dialog is closed"""
        # Disconnect all signals to prevent memory leaks
        try:
            self.play_again_signal.disconnect()
            self.return_home_signal.disconnect()
        except Exception:
            pass  # It's okay if they're not connected
        super().closeEvent(event)