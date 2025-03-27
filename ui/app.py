from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QColor, QFont, QPalette
from ui.board import ChessBoard
from ui.components.popups import StartScreen

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
        if start_screen.exec_() == QDialog.Accepted:
            mode = start_screen.get_mode()
            if mode:
                self.chess_window = ChessBoard(mode, self)
                self.chess_window.show()