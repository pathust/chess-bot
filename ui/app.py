# Update the ui/app.py file to handle time mode selection

from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtGui import QColor, QFont, QPalette
from ui.board import ChessBoard
from ui.components.popups import StartScreen
from ui.components.load_game_dialog import LoadGameDialog
from ui.components.sidebar import SavedGameManager
from ui.components.time_mode_dialog import TimeModeDialog

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
        # Close any existing chess window and ensure proper cleanup
        if self.chess_window:
            # Explicitly clean up any popup
            if hasattr(self.chess_window, 'popup') and self.chess_window.popup:
                self.chess_window.popup.close()
                self.chess_window.popup = None
                
            self.chess_window.close()
            self.chess_window.deleteLater()  # Ensure Qt properly destroys the window
            self.chess_window = None
                
        start_screen = StartScreen()
        start_screen.load_game_button.clicked.connect(self.load_saved_game)
        
        if start_screen.exec_() == QDialog.Accepted:
            mode = start_screen.get_mode()
            if mode:
                self.start_new_game_with_time_selection(mode)
    
    def start_new_game_with_time_selection(self, mode):
        """Start a new game with time mode selection."""
        # Show time mode dialog
        time_dialog = TimeModeDialog()
        
        if time_dialog.exec_() == QDialog.Accepted:
            is_time_mode, white_time_ms, black_time_ms, white_inc_ms, black_inc_ms = time_dialog.get_time_settings()
            
            # Create chess window with the selected mode
            self.chess_window = ChessBoard(mode, self)
            
            # Setup time mode with increments after window creation
            self.chess_window.setup_time_mode(is_time_mode, white_time_ms, black_time_ms, white_inc_ms, black_inc_ms)
            
            # Start timer for human vs AI mode
            if mode == "human_ai" and is_time_mode:
                self.chess_window.switch_timer_to_player('human')
            
            self.chess_window.show()
        else:
            # User canceled time selection, go back to start screen
            self.show_start_screen()
    
    def load_saved_game(self):
        """Show dialog to load a saved game"""
        load_dialog = LoadGameDialog()
        load_dialog.game_selected.connect(self.start_loaded_game)
        
        result = load_dialog.exec_()
        
        if result == QDialog.Accepted and hasattr(load_dialog, 'game_data'):
            # Find and close the start screen
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QDialog) and widget.windowTitle() == "Chess Game - Mode Selection":
                    widget.close()
                    break
            # The signal already called start_loaded_game
        else:
            # User canceled, just keep the start screen open
            pass
    
    def start_loaded_game(self, game_data):
        """Start a game with the loaded game data including increments."""
        try:
            mode = game_data.get('mode', 'human_ai')
            
            # Close any existing chess window
            if self.chess_window:
                self.chess_window.close()
                self.chess_window.deleteLater()
                self.chess_window = None
            
            # Check if the loaded game has timer data
            has_timer_data = 'timer_settings' in game_data
            is_time_mode = False
            white_time_ms = 0
            black_time_ms = 0
            white_inc_ms = 3000  # Default increment
            black_inc_ms = 3000  # Default increment
            
            if has_timer_data:
                timer_settings = game_data['timer_settings']
                is_time_mode = timer_settings.get('enabled', False)
                white_time_ms = timer_settings.get('white_time_ms', 0)
                black_time_ms = timer_settings.get('black_time_ms', 0)
                # Load saved increment values or use defaults
                white_inc_ms = timer_settings.get('white_increment_ms', 3000)
                black_inc_ms = timer_settings.get('black_increment_ms', 3000)
            else:
                # Ask user if they want to enable time mode for this loaded game
                time_dialog = TimeModeDialog()
                time_dialog.setWindowTitle("Time Control for Loaded Game")
                
                if time_dialog.exec_() == QDialog.Accepted:
                    is_time_mode, white_time_ms, black_time_ms, white_inc_ms, black_inc_ms = time_dialog.get_time_settings()
            
            # Create a new chess window with the loaded game data
            self.chess_window = ChessBoard(mode, self, game_data)
            
            # Setup time mode with increments
            self.chess_window.setup_time_mode(is_time_mode, white_time_ms, black_time_ms, white_inc_ms, black_inc_ms)
            
            # If time mode is enabled, start the timer for the current player
            if is_time_mode:
                current_player = game_data.get('turn', 'human')
                if mode == "human_ai":
                    if current_player == 'human':
                        self.chess_window.switch_timer_to_player('human')
                    else:
                        self.chess_window.switch_timer_to_player('ai')
                else:  # AI vs AI
                    if current_player == 'ai1':
                        self.chess_window.switch_timer_to_player('ai1')
                    else:
                        self.chess_window.switch_timer_to_player('ai2')
            
            self.chess_window.show()
            
            # Get the load dialog and its parent (start screen)
            load_dialog = self.sender()
            if load_dialog:
                # If this is coming from LoadGameDialog
                start_screen = load_dialog.parent()
                if start_screen:
                    # Force close the start screen
                    start_screen.done(QDialog.Accepted)
                # Close the load dialog itself if it's still open
                load_dialog.done(QDialog.Accepted)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load game: {str(e)}")
            print(f"Error loading game: {str(e)}")