"""
Sidebar components for the chess application.
This module provides sidebar widgets for game controls and settings.
"""

import os
import json
import datetime
from PyQt5.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QFileDialog, QMessageBox, QSizePolicy, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

from utils.config import Config
from utils.error_handler import ErrorHandler
from ui.components.controls import ControlButton, EnhancedSlider, ResignButton, UndoButton

class SavedGameManager:
    """Manages saving and loading chess games."""
    
    @staticmethod
    def save_game(board, game_mode, turn, last_move_from, last_move_to, game_name=None, game_notes=None):
        """
        Save the current game state to a file with enhanced error handling.
        
        Args:
            board (chess.Board): The chess board to save
            game_mode (str): The current game mode ("human_ai" or "ai_ai")
            turn (str): The current turn ("human", "ai", "ai1", or "ai2")
            last_move_from (tuple): The starting position of the last move
            last_move_to (tuple): The ending position of the last move
            game_name (str, optional): Custom name for the saved game
            game_notes (str, optional): Notes about the saved game
        
        Returns:
            tuple: (success: bool, file_path: str or None)
        """
        try:
            # Validate critical inputs
            if not board:
                raise ValueError("Cannot save an empty board")
            
            # Create a comprehensive game state dictionary
            game_data = {
                'version': '1.0',  # Add version for future compatibility
                'fen': board.fen(),
                'mode': game_mode,
                'turn': turn,
                'last_move_from': last_move_from,
                'last_move_to': last_move_to,
                'move_history': [move.uci() for move in board.move_stack],
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add optional metadata with validation
            if game_name and isinstance(game_name, str):
                game_data['game_name'] = game_name.strip()[:100]  # Limit name length
            
            if game_notes and isinstance(game_notes, str):
                game_data['game_notes'] = game_notes.strip()[:500]  # Limit notes length
            
            # Open file dialog to select save location
            file_path, _ = QFileDialog.getSaveFileName(
                None, 
                "Save Chess Game", 
                os.path.expanduser("~/Desktop"), 
                "Chess Game Files (*.chess);;All Files (*)"
            )
            
            if not file_path:
                return False, None
            
            # Ensure .chess extension
            if not file_path.lower().endswith('.chess'):
                file_path += '.chess'
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save with proper encoding and error handling
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=4, ensure_ascii=False)
            
            return True, file_path
        
        except PermissionError:
            ErrorHandler.show_error(
                None, 
                "Save Error", 
                "Permission denied. Cannot save file in the selected location."
            )
        except Exception as e:
            # Log the full error for debugging
            print(f"Unexpected error in save_game: {e}")
            ErrorHandler.show_error(
                None, 
                "Save Error", 
                f"An unexpected error occurred: {str(e)}"
            )
        
        return False, None

    @staticmethod
    def load_game(file_path=None):
        """
        Load a saved chess game with robust error handling.
        
        Args:
            file_path (str, optional): Path to the game file to load
        
        Returns:
            tuple: (success: bool, game_data: dict or None)
        """
        try:
            # If no file path provided, open file dialog
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    None, 
                    "Load Chess Game", 
                    os.path.expanduser("~/Desktop"), 
                    "Chess Game Files (*.chess);;All Files (*)"
                )
            
            # Validate file path
            if not file_path or not os.path.exists(file_path):
                return False, None
            
            # Validate file extension
            if not file_path.lower().endswith('.chess'):
                ErrorHandler.show_error(
                    None,
                    "Invalid File", 
                    "Please select a valid .chess game file."
                )
                return False, None
            
            # Read and parse the file with robust handling
            with open(file_path, 'r', encoding='utf-8') as f:
                file_contents = f.read()
                
                # Additional safeguard against empty files
                if not file_contents.strip():
                    ErrorHandler.show_error(
                        None,
                        "Empty File", 
                        "The selected game file is empty."
                    )
                    return False, None
                
                try:
                    game_data = json.loads(file_contents)
                except json.JSONDecodeError:
                    ErrorHandler.show_error(
                        None,
                        "JSON Error", 
                        "The game file is corrupted or not in the correct format."
                    )
                    return False, None
            
            # Validate essential game data
            required_keys = ['fen', 'mode', 'turn', 'move_history']
            if not all(key in game_data for key in required_keys):
                ErrorHandler.show_error(
                    None,
                    "Invalid Game Data", 
                    "The saved game is missing critical information."
                )
                return False, None
            
            return True, game_data
        
        except PermissionError:
            ErrorHandler.show_error(
                None,
                "Permission Denied", 
                "Cannot read the selected file. Check file permissions."
            )
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error in load_game: {e}")
            ErrorHandler.show_error(
                None,
                "Load Error", 
                f"An unexpected error occurred: {str(e)}"
            )
        
        return False, None


class AIControlPanel(QScrollArea):
    """
    AI control panel with improved responsive design.
    Provides controls for AI game settings and game management.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #2c3e50;
                border-radius: 10px;
                border: 2px solid #1a2530;
            }
        """)
        
        # Add shadow for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Create inner widget for the scroll area
        inner_widget = QWidget()
        inner_widget.setStyleSheet("background-color: #2c3e50;")  
        self.setWidget(inner_widget)
        
        # Create main layout with adaptive spacing
        self.main_layout = QVBoxLayout(inner_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title header
        self.title = QLabel("AI Controls")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: white; 
            padding: 8px;
            background-color: #34495e;
            border-radius: 6px;
        """)
        self.main_layout.addWidget(self.title)
                
        # Create a responsive layout that can adapt to window width
        responsive_container = QWidget()
        responsive_layout = QGridLayout(responsive_container)
        responsive_layout.setSpacing(10)
        
        # Create button container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        # Start button
        self.start_button = ControlButton("▶ Start", Config.START_BUTTON_COLOR)
        button_layout.addWidget(self.start_button)

        # Pause button
        self.pause_button = ControlButton("⏸ Pause", Config.PAUSE_BUTTON_COLOR)
        button_layout.addWidget(self.pause_button)

        # Reset button
        self.reset_button = ControlButton("↻ Reset", Config.RESET_BUTTON_COLOR)
        button_layout.addWidget(self.reset_button)
        
        # Save Game button
        self.save_button = ControlButton("💾 Save", Config.SAVE_BUTTON_COLOR)
        button_layout.addWidget(self.save_button)
        
        # Resign button
        self.resign_button = ResignButton()
        button_layout.addWidget(self.resign_button)

        # Return to Home button
        self.home_button = ControlButton("🏠 Home", Config.HOME_BUTTON_COLOR)
        button_layout.addWidget(self.home_button)
        
        # Undo button (will be added in board.py setup_undo_button)
        self.undo_button_container = QWidget()
        self.undo_button_layout = QVBoxLayout(self.undo_button_container)
        self.undo_button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.undo_button_container)
        
        button_layout.addStretch(1)
        
        # Add button container to responsive layout
        responsive_layout.addWidget(button_container, 0, 0, 1, 1)
        
        # Create slider container
        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setSpacing(15)
        
        # Create enhanced depth slider with thinking time estimation
        self.depth_slider = EnhancedSlider(
            "AI Thinking Depth:", 
            Config.MIN_AI_SEARCH_DEPTH, 
            Config.MAX_AI_SEARCH_DEPTH, 
            Config.DEFAULT_AI_SEARCH_DEPTH, 
            "Basic", 
            "Deep"
        )
        self.depth_slider.valueChanged.connect(self.update_depth_info)
        slider_layout.addWidget(self.depth_slider)
        
        # For backward compatibility - use the depth slider as the speed slider
        # This allows existing code that calls self.control_panel.speed_slider to continue working
        self.speed_slider = self.depth_slider
        
        # Add current depth display with improved visibility
        depth_container = QFrame()
        depth_container.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        depth_layout = QVBoxLayout(depth_container)
        self.depth_value = QLabel(f"Current depth: {Config.DEFAULT_AI_SEARCH_DEPTH}")
        self.depth_value.setAlignment(Qt.AlignCenter)
        self.depth_value.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: white;
            padding: 2px;
        """)
        depth_layout.addWidget(self.depth_value)
        
        # Add estimated thinking time
        self.thinking_time = QLabel(
            f"Est. thinking time: {Config.get_estimated_thinking_time(Config.DEFAULT_AI_SEARCH_DEPTH)/1000:.1f}s"
        )
        self.thinking_time.setAlignment(Qt.AlignCenter)
        self.thinking_time.setStyleSheet("""
            font-size: 11pt;
            color: #ecf0f1;
            padding: 2px;
        """)
        depth_layout.addWidget(self.thinking_time)
        
        slider_layout.addWidget(depth_container)
        slider_layout.addStretch(1)
        
        # Add slider container to responsive layout
        responsive_layout.addWidget(slider_container, 0, 1, 1, 1)
        
        # Add responsive container to main layout
        self.main_layout.addWidget(responsive_container)
        
        # Set initial button states
        self.pause_button.setEnabled(False)
        
        # Update displayed values
        self.update_depth_info(Config.DEFAULT_AI_SEARCH_DEPTH)
    
    def update_depth_info(self, depth):
        """Update the displayed depth information and estimated thinking time."""
        self.depth_value.setText(f"Current depth: {depth}")
        thinking_time = Config.get_estimated_thinking_time(depth)
        self.thinking_time.setText(f"Est. thinking time: {thinking_time/1000:.1f}s")
    
    def set_human_ai_mode(self):
        """Configure the panel for Human vs AI mode."""
        self.title.setText("AI Settings")
        self.start_button.hide()
        self.pause_button.hide()
    
    def set_ai_ai_mode(self):
        """Configure the panel for AI vs AI mode."""
        self.title.setText("AI vs AI Controls")
        self.start_button.show()
        self.pause_button.show()
    
    def sizeHint(self):
        """Provide a size hint for layout management."""
        return QSize(250, 300)