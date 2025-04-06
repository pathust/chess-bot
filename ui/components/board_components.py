from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

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
        self.is_checked = False  # For check highlighting
        self.hover_effect = None  # Store reference to the hover effect
        
    def enterEvent(self, event):
        """Highlight square on mouse hover"""
        try:
            if not self.is_selected and not self.is_last_move:
                # Create a new effect every time instead of reusing
                effect = QGraphicsOpacityEffect(self)
                effect.setOpacity(0.8)
                self.setGraphicsEffect(effect)
                self.is_highlighted = True
        except Exception as e:
            print(f"Error in enterEvent: {str(e)}")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Remove highlight on mouse leave"""
        try:
            if self.is_highlighted:
                self.setGraphicsEffect(None)
                self.is_highlighted = False
        except Exception as e:
            print(f"Error in leaveEvent: {str(e)}")
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click on square"""
        try:
            # Ensure no highlight effect remains after clicking
            if self.is_highlighted:
                self.setGraphicsEffect(None)
                self.is_highlighted = False
        except Exception as e:
            print(f"Error in mousePressEvent: {str(e)}")
        self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        """Custom painting for the square to include circular indicators"""
        super().paintEvent(event)
        
        # Draw indicators for valid moves, castling, and check
        if self.is_valid_move or self.is_castling_move or self.is_checked:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw circular indicators for valid moves
            if self.is_valid_move:
                painter.setPen(QPen(QColor("#32CD32"), 2))  # Green outline
                painter.setBrush(QBrush(QColor(50, 205, 50, 120)))  # Semi-transparent green fill
                painter.drawEllipse(20, 20, 20, 20)  # Adjust size as needed
            
            # Draw different indicator for castling
            elif self.is_castling_move:
                painter.setPen(QPen(QColor("#FFA500"), 2))  # Orange outline
                painter.setBrush(QBrush(QColor(255, 165, 0, 120)))  # Semi-transparent orange fill
                painter.drawEllipse(20, 20, 20, 20)  # Adjust size as needed
            
            # Draw red highlight for check
            if self.is_checked:
                painter.setPen(QPen(QColor("#FF0000"), 3))  # Red outline
                painter.setBrush(QBrush(QColor(255, 0, 0, 40)))  # Very transparent red fill
                painter.drawRect(2, 2, self.width()-4, self.height()-4)  # Cover almost the whole square
            
            painter.end()
        
    def update_appearance(self):
        """Update the square's appearance based on its state"""
        base_color = "#c1bfb0" if (self.row + self.col) % 2 == 0 else "#7a9bbe"
        
        if self.is_selected:
            base_color = "#ffff99"  # Yellow for selected piece
        elif self.is_last_move:
            base_color = "#ffe066"  # Soft yellow for last move
            
        # Reset any highlight effect if state changed
        try:
            if (self.is_selected or self.is_last_move) and self.is_highlighted:
                self.setGraphicsEffect(None)
                self.is_highlighted = False
        except Exception as e:
            print(f"Error in update_appearance: {str(e)}")
            
        # Set the base color of the square
        self.setStyleSheet(f"background-color: {base_color}; border: 1px solid black;")
        
        # Trigger a repaint for the indicators
        self.update()

class ThinkingIndicator(QLabel):
    """Visual indicator for AI thinking state with improved visibility and animation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: white;
            background-color: rgba(52, 73, 94, 0.9);
            border-radius: 10px;
            padding: 10px;
            border: 2px solid #3498db;
            margin: 0px;
        """)
        self.setFixedHeight(50)
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.pulse_effect)
        self.opacity = 0.9
        self.opacity_increasing = False
        self.hide()
        
    def start_thinking(self, ai_name):
        """Start the thinking animation with pulsing effect"""
        self.base_text = f"{ai_name} is thinking"
        self.dots = 0
        self.setText(f"{self.base_text}...")
        self.show()
        self.timer.start(300)  # Update dots every 300ms
        self.animation_timer.start(100)  # Pulse animation frames
        
    def stop_thinking(self):
        """Stop all animations"""
        self.timer.stop()
        self.animation_timer.stop()
        self.hide()
        
    def update_dots(self):
        """Update the thinking dots animation"""
        self.dots = (self.dots + 1) % 4
        dot_text = "." * self.dots
        self.setText(f"{self.base_text}{dot_text.ljust(3)}")
        
    def pulse_effect(self):
        """Create a subtle pulsing effect by changing opacity"""
        if self.opacity_increasing:
            self.opacity += 0.03
            if self.opacity >= 0.95:
                self.opacity_increasing = False
        else:
            self.opacity -= 0.03
            if self.opacity <= 0.75:
                self.opacity_increasing = True
                
        # Update the stylesheet with new opacity
        self.setStyleSheet(f"""
            font-size: 16pt;
            font-weight: bold;
            color: white;
            background-color: rgba(52, 73, 94, {self.opacity});
            border-radius: 10px;
            padding: 10px;
            border: 2px solid #3498db;
            margin: 0px;
        """)