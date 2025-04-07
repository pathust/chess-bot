"""
Dialog for loading saved chess games.
This module provides a user interface for browsing and loading saved games.
"""

import os
import json
import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QFrame, QFileDialog, QTextBrowser, QSplitter, QWidget,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap

class LoadGameDialog(QDialog):
    """Enhanced dialog to load a saved chess game."""
    
    game_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Saved Game")
        self.setModal(True)
        self.setMinimumSize(700, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
            QListWidget {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #cccccc;
                font-size: 12pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6f7ff;
            }
        """)
        
        # Add drop shadow effect for the dialog
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
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
        browse_button.setCursor(Qt.PointingHandCursor)
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
        
        # Add drop shadow to the browse button
        button_shadow = QGraphicsDropShadowEffect(browse_button)
        button_shadow.setBlurRadius(15)
        button_shadow.setColor(QColor(0, 0, 0, 70))
        button_shadow.setOffset(0, 5)
        browse_button.setGraphicsEffect(button_shadow)
        
        # Create a splitter for game info and preview
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
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
        self.info_frame.setMinimumWidth(350)
        
        info_layout = QVBoxLayout(self.info_frame)
        
        self.info_label = QLabel("No game file selected")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 11pt; color: #777777;")
        info_layout.addWidget(self.info_label)
        
        # Game details
        self.details = QTextBrowser()
        self.details.setStyleSheet("""
            background-color: white;
            border: none;
            font-size: 11pt;
        """)
        self.details.setOpenExternalLinks(False)
        self.details.setReadOnly(True)
        self.details.setMinimumHeight(150)
        info_layout.addWidget(self.details)
        
        # Game preview (placeholder for future board preview)
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_frame.setMinimumWidth(250)
        preview_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_title = QLabel("Game Preview")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2c3e50;")
        preview_layout.addWidget(preview_title)
        
        # Add a simple chess board preview widget
        self.preview_content = QLabel()
        self.preview_content.setAlignment(Qt.AlignCenter)
        self.preview_content.setStyleSheet("font-size: 12pt; color: #777777;")
        self.preview_content.setText("Select a game file to see a preview")
        self.preview_content.setWordWrap(True)
        self.preview_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview_content)
        
        # Add frames to splitter
        splitter.addWidget(self.info_frame)
        splitter.addWidget(preview_frame)
        
        # Set initial splitter sizes (60% info, 40% preview)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load Game")
        self.load_button.setCursor(Qt.PointingHandCursor)
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
        cancel_button.setCursor(Qt.PointingHandCursor)
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
        
        # Add drop shadows to buttons
        for button in [self.load_button, cancel_button]:
            shadow = QGraphicsDropShadowEffect(button)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 70))
            shadow.setOffset(0, 5)
            button.setGraphicsEffect(shadow)
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Initialize variables
        self.selected_file = None
        self.game_data = None
        
        # Create mini chessboard preview
        self.create_empty_board_preview()
    
    def create_empty_board_preview(self):
        """Create a simple visual representation of a chess board."""
        # Create a pixmap for the chess board preview
        board_size = 200
        pixmap = QPixmap(board_size, board_size)
        pixmap.fill(Qt.transparent)
        
        # Paint the board
        painter = QPainter(pixmap)
        square_size = board_size // 8
        
        for row in range(8):
            for col in range(8):
                x = col * square_size
                y = row * square_size
                if (row + col) % 2 == 0:
                    color = QColor("#c1bfb0")  # Light squares
                else:
                    color = QColor("#7a9bbe")  # Dark squares
                
                painter.fillRect(x, y, square_size, square_size, color)
        
        painter.end()
        
        # Set the pixmap as the preview image
        self.preview_content.setPixmap(pixmap)
        self.preview_content.setFixedSize(board_size, board_size)
        self.preview_content.setScaledContents(True)
    
    def browse_for_file(self):
        """Open file dialog to browse for a saved game file."""
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
                self.details.setHtml("")
                self.preview_content.setText("Could not load the selected file")
                self.load_button.setEnabled(False)
                self.game_data = None
    
    def update_game_info(self):
        """Update the display with information about the selected game."""
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
        
        # Get custom game name and notes if available
        game_name = self.game_data.get('game_name', 'Unnamed Game')
        game_notes = self.game_data.get('game_notes', '')
        
        # Create HTML formatted detail text
        details_html = f"""
        <style>
        .label {{ color: #555; font-weight: bold; }}
        .value {{ color: #000; }}
        .header {{ color: #2c3e50; font-size: 16px; font-weight: bold; margin-top: 10px; }}
        </style>
        
        <div class="header">{game_name}</div>
        
        <p><span class="label">Saved:</span> <span class="value">{timestamp}</span></p>
        <p><span class="label">Game mode:</span> <span class="value">{game_mode}</span></p>
        <p><span class="label">Moves played:</span> <span class="value">{move_count}</span></p>
        <p><span class="label">Current turn:</span> <span class="value">{turn}</span></p>
        """
        
        if game_notes:
            details_html += f"""
            <div class="header">Notes</div>
            <p>{game_notes}</p>
            """
        
        self.details.setHtml(details_html)
        
        # Update the preview with a simple board representation
        self.update_board_preview()
    
    def update_board_preview(self):
        """Update the board preview based on the FEN in the saved game."""
        if 'fen' in self.game_data:
            fen = self.game_data['fen'].split()[0]  # Get board part of FEN
            board_size = 200
            square_size = board_size // 8
            
            # Create pixmap
            pixmap = QPixmap(board_size, board_size)
            pixmap.fill(Qt.transparent)
            
            # Paint board
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw board squares
            for row in range(8):
                for col in range(8):
                    x = col * square_size
                    y = row * square_size
                    if (row + col) % 2 == 0:
                        color = QColor("#c1bfb0")  # Light squares
                    else:
                        color = QColor("#7a9bbe")  # Dark squares
                    
                    painter.fillRect(x, y, square_size, square_size, color)
            
            # Draw pieces based on FEN
            row = 0
            col = 0
            
            # Map FEN characters to Unicode chess pieces
            piece_map = {
                'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟',
                'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
            }
            
            for char in fen:
                if char == '/':
                    row += 1
                    col = 0
                elif char.isdigit():
                    col += int(char)
                elif char in piece_map:
                    x = col * square_size
                    y = row * square_size
                    
                    # Choose color based on case
                    color = Qt.white if char.isupper() else Qt.black
                    
                    # Draw piece
                    painter.setPen(color)
                    painter.setFont(QFont('Arial', square_size * 0.6))  # Scale font size
                    painter.drawText(
                        x, y, square_size, square_size, 
                        Qt.AlignCenter, piece_map[char]
                    )
                    
                    col += 1
            
            painter.end()
            
            # Set the pixmap as the preview content
            self.preview_content.setPixmap(pixmap)
            self.preview_content.setFixedSize(board_size, board_size)
            self.preview_content.setScaledContents(True)
    
    def accept_file(self):
        """Accept the selected file and emit signal with game data."""
        if self.game_data:
            self.game_selected.emit(self.game_data)
            # Force close this dialog
            self.done(QDialog.Accepted)