from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

class ChessSquare(QLabel):
    """Enhanced chess square widget with hover and selection effects"""
    clicked = pyqtSignal(int, int)
    
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(60, 60)
        self.setMargin(0)
        
        # Initialize states
        self.is_highlighted = False
        self.is_last_move = False
        self.is_valid_move = False
        self.is_castling_move = False
        self.is_selected = False
        
    def enterEvent(self, event):
        """Highlight square on mouse hover"""
        if not self.is_selected and not self.is_last_move:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.8)
            self.setGraphicsEffect(effect)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Remove highlight on mouse leave"""
        if not self.is_selected and not self.is_last_move:
            self.setGraphicsEffect(None)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click on square"""
        self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)
        
    def update_appearance(self):
        """Update the square's appearance based on its state"""
        base_color = "#c1bfb0" if (self.row + self.col) % 2 == 0 else "#7a9bbe"
        
        if self.is_selected:
            base_color = "#ffff99"  # Yellow for selected piece
        elif self.is_last_move:
            base_color = "#ffe066"  # Soft yellow for last move
        elif self.is_castling_move:
            base_color = "#ff9966"  # Orange for castling moves
        elif self.is_valid_move:
            base_color = "#90ee90"  # Light green for valid moves
            
        self.setStyleSheet(f"background-color: {base_color}; border: 1px solid black;")

class ThinkingIndicator(QLabel):
    """Visual indicator for AI thinking state with improved visibility"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: white;
            background-color: rgba(52, 73, 94, 0.8);
            border-radius: 10px;
            padding: 10px;
            border: 1px solid white;
            margin: 0px;
        """)
        self.setFixedHeight(50)
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.hide()
        
    def start_thinking(self, ai_name):
        """Start the thinking animation"""
        self.base_text = f"{ai_name} is thinking"
        self.dots = 0
        self.setText(f"{self.base_text}...")
        self.show()
        self.timer.start(300)  # Update dots every 300ms
        
    def stop_thinking(self):
        """Stop the thinking animation"""
        self.timer.stop()
        self.hide()
        
    def update_dots(self):
        """Update the thinking dots animation"""
        self.dots = (self.dots + 1) % 4
        dot_text = "." * self.dots
        self.setText(f"{self.base_text}{dot_text.ljust(3)}")