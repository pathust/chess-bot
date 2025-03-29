from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QFrame, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
import os
import json
import datetime

class LoadGameDialog(QDialog):
    """Dialog to load a saved chess game"""
    
    game_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Saved Game")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Load Saved Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Select a saved game file to load:")
        instructions.setStyleSheet("font-size: 12pt; margin-bottom: 5px;")
        layout.addWidget(instructions)
        
        # Browse button
        browse_button = QPushButton("Browse for Game File")
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 12pt;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        browse_button.clicked.connect(self.browse_for_file)
        layout.addWidget(browse_button)
        
        # Game info display area
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.info_frame.setFrameShape(QFrame.StyledPanel)
        
        info_layout = QVBoxLayout(self.info_frame)
        
        self.info_label = QLabel("No game file selected")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 11pt; color: #777777;")
        info_layout.addWidget(self.info_label)
        
        # Game details
        self.details_label = QLabel("")
        self.details_label.setStyleSheet("font-size: 11pt; margin-top: 10px;")
        self.details_label.setWordWrap(True)
        self.details_label.hide()  # Hide until a game is selected
        info_layout.addWidget(self.details_label)
        
        layout.addWidget(self.info_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load Game")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 12pt;
                padding: 10px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #eeeeee;
            }
        """)
        self.load_button.clicked.connect(self.accept_file)
        self.load_button.setEnabled(False)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 12pt;
                padding: 10px;
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
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Initialize variables
        self.selected_file = None
        self.game_data = None
    
    def browse_for_file(self):
        """Open file dialog to browse for a saved game file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Saved Game", 
            os.path.expanduser("~/Desktop"), 
            "Chess Game Files (*.chess);;All Files (*)"
        )
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    self.game_data = json.load(f)
                    
                self.selected_file = file_path
                self.update_game_info()
                self.load_button.setEnabled(True)
            except Exception as e:
                self.info_label.setText(f"Error loading file: {str(e)}")
                self.details_label.hide()
                self.load_button.setEnabled(False)
                self.game_data = None
    
    def update_game_info(self):
        """Update the display with information about the selected game"""
        if not self.game_data:
            return
        
        self.info_label.setText(f"Game file: {os.path.basename(self.selected_file)}")
        
        # Format game details
        timestamp = self.game_data.get('timestamp', 'Unknown date')
        game_mode = "Human vs AI" if self.game_data.get('mode') == 'human_ai' else "AI vs AI"
        
        # Count moves in the game
        move_count = len(self.game_data.get('move_history', []))
        
        # Determine current turn
        turn = "White" if self.game_data.get('turn') in ['human', 'ai1'] else "Black"
        
        # Create detail text
        details = f"""
        <b>Saved:</b> {timestamp}
        <b>Game mode:</b> {game_mode}
        <b>Moves played:</b> {move_count}
        <b>Current turn:</b> {turn}
        """
        
        self.details_label.setText(details)
        self.details_label.show()
    
    def accept_file(self):
        if self.game_data:
            self.game_selected.emit(self.game_data)
            # Force close this dialog
            self.done(QDialog.Accepted)