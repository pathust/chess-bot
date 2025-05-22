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
from ui.components.controls import ControlButton, ResignButton, UndoButton

class SavedGameManager:
    """Manages saving and loading chess games."""
    
    # Update the SavedGameManager in ui/components/sidebar.py to include timer settings

    @staticmethod
    def save_game(board, game_mode, turn, last_move_from, last_move_to, 
                  game_name=None, game_notes=None, timer_settings=None):
        """
        Save the current game state to a file with enhanced error handling and timer support.
        
        Args:
            board (chess.Board): The chess board to save
            game_mode (str): The current game mode ("human_ai" or "ai_ai")
            turn (str): The current turn ("human", "ai", "ai1", or "ai2")
            last_move_from (tuple): The starting position of the last move
            last_move_to (tuple): The ending position of the last move
            game_name (str, optional): Custom name for the saved game
            game_notes (str, optional): Notes about the saved game
            timer_settings (dict, optional): Timer configuration and current state
        
        Returns:
            tuple: (success: bool, file_path: str or None)
        """
        try:
            # Validate critical inputs
            if not board:
                raise ValueError("Cannot save an empty board")
            
            # Create a comprehensive game state dictionary
            game_data = {
                'version': '2.0',  # Updated version for timer support
                'fen': board.fen(),
                'mode': game_mode,
                'turn': turn,
                'last_move_from': last_move_from,
                'last_move_to': last_move_to,
                'move_history': [move.uci() for move in board.move_stack],
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add timer settings if provided
            if timer_settings:
                game_data['timer_settings'] = {
                    'enabled': timer_settings.get('enabled', False),
                    'initial_white_time_ms': timer_settings.get('initial_white_time_ms', 0),
                    'initial_black_time_ms': timer_settings.get('initial_black_time_ms', 0),
                    'white_time_ms': timer_settings.get('white_time_ms', 0),
                    'black_time_ms': timer_settings.get('black_time_ms', 0),
                    'active_player': timer_settings.get('active_player', None)
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
    AI control panel with simplified interface - no AI difficulty settings.
    Provides only game management buttons for better usability.
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
        
        # Create main layout with moderate spacing
        self.main_layout = QVBoxLayout(inner_widget)
        self.main_layout.setSpacing(10) # Reduced spacing
        self.main_layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        
        # Title header
        self.title = QLabel("Game Controls")
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
        
        # Create grid layout for more compact button arrangement
        button_grid = QWidget()
        grid_layout = QGridLayout(button_grid)
        grid_layout.setSpacing(8) # Tight spacing between buttons
        
        # Make buttons smaller and arrange in a grid
        button_height = 45  # Smaller height
        
        # Start button (top-left)
        self.start_button = ControlButton("▶ Start", Config.START_BUTTON_COLOR)
        self.start_button.setFixedHeight(button_height)
        grid_layout.addWidget(self.start_button, 0, 0)

        # Pause button (top-right)
        self.pause_button = ControlButton("⏸ Pause", Config.PAUSE_BUTTON_COLOR)
        self.pause_button.setFixedHeight(button_height)
        grid_layout.addWidget(self.pause_button, 0, 1)

        # Reset button (middle-left)
        self.reset_button = ControlButton("↻ Reset", Config.RESET_BUTTON_COLOR)
        self.reset_button.setFixedHeight(button_height)
        grid_layout.addWidget(self.reset_button, 1, 0)
        
        # Save Game button (middle-right)
        self.save_button = ControlButton("💾 Save", Config.SAVE_BUTTON_COLOR)
        self.save_button.setFixedHeight(button_height)
        grid_layout.addWidget(self.save_button, 1, 1)
        
        # Resign button (bottom-left)
        self.resign_button = ResignButton()
        self.resign_button.setFixedHeight(button_height)
        grid_layout.addWidget(self.resign_button, 2, 0)

        # Return to Home button (bottom-right)
        self.home_button = ControlButton("🏠 Home", Config.HOME_BUTTON_COLOR)
        self.home_button.setFixedHeight(button_height)
        grid_layout.addWidget(self.home_button, 2, 1)
        
        # Undo button container in its own row (spans both columns)
        self.undo_button_container = QWidget()
        self.undo_button_layout = QVBoxLayout(self.undo_button_container)
        self.undo_button_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.undo_button_container, 3, 0, 1, 2)  # Span both columns
        
        # Add the grid to the main layout
        self.main_layout.addWidget(button_grid)
        
        # Add a stretcher to push everything to the top
        self.main_layout.addStretch(1)
        
        # Set initial button states
        self.pause_button.setEnabled(False)
        
        # For backward compatibility - create hidden dummy sliders that don't do anything
        # but have the required signals to prevent connection errors
        from PyQt5.QtCore import pyqtSignal
        
        # Create a hidden dummy widget for the depth slider
        self.depth_container = QWidget()
        self.depth_container.hide()  # Hide it completely
        self.main_layout.addWidget(self.depth_container)
        
        # Create a minimal slider class that just has the valueChanged signal
        class DummySlider(QWidget):
            valueChanged = pyqtSignal(int)
            
            def setValue(self, value):
                pass
                
            def value(self):
                return Config.DEFAULT_AI_SEARCH_DEPTH
        
        # Create the dummy sliders
        self.depth_slider = DummySlider()
        self.speed_slider = self.depth_slider  # Same object for both
        
        # Create a dummy value label for compatibility
        self.depth_value = QLabel("")
        self.depth_value.hide()
    
    def set_human_ai_mode(self):
        """Configure the panel for Human vs AI mode."""
        self.title.setText("Game Controls")
        self.start_button.hide()
        self.pause_button.hide()
    
    def set_ai_ai_mode(self):
        """Configure the panel for AI vs AI mode."""
        self.title.setText("AI vs AI Controls")
        self.start_button.show()
        self.pause_button.show()
    
    def sizeHint(self):
        """Provide a size hint for layout management."""
        return QSize(250, 400)