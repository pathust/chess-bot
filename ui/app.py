from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtGui import QColor, QFont, QPalette
from ui.board import ChessBoard
from ui.components.popups import StartScreen
from ui.components.load_game_dialog import LoadGameDialog
from ui.components.sidebar import SavedGameManager

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
                self.chess_window = ChessBoard(mode, self)
                self.chess_window.show()
    
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
        """Start a game with the loaded game data"""
        try:
            mode = game_data.get('mode', 'human_ai')
            
            # Close any existing chess window
            if self.chess_window:
                self.chess_window.close()
                self.chess_window.deleteLater()
                self.chess_window = None
            
            # Create a new chess window with the loaded game data
            self.chess_window = ChessBoard(mode, self, game_data)
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