"""
Chess board UI components.
This module provides the UI components for the chess board display.
"""

from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize, QRect, QEvent, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QResizeEvent

from utils.config import Config

class ChessSquare(QLabel):
    """Enhanced chess square widget with hover and selection effects."""
    
    clicked = pyqtSignal(int, int)
    
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAlignment(Qt.AlignCenter)
        
        # Ensure the square remains square by using a special size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(40, 40)  # Minimum size for small screens
        
        # Initialize states
        self.is_highlighted = False
        self.is_last_move = False
        self.is_valid_move = False
        self.is_castling_move = False
        self.is_en_passant_move = False  # New: Flag for en passant moves
        self.is_selected = False
        self.is_checked = False  # For check highlighting
        
        # Store the effect as an instance variable to prevent deletion
        self.hover_effect = None
        
        # Install event filter to maintain square aspect ratio
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """Event filter to maintain square aspect ratio."""
        if (obj is self and event.type() == QEvent.Resize):
            # Calculate new size to maintain square aspect ratio
            size = min(self.width(), self.height())
            if size > 0:
                # Update font size based on the square size
                font = self.font()
                font.setPointSize(max(8, size // 2))  # Font size as 50% of square size, min 8pt
                self.setFont(font)
            
            # Let the resize event propagate normally
            return False
        return super().eventFilter(obj, event)
        
    def enterEvent(self, event):
        """Highlight square on mouse hover."""
        try:
            if not self.is_selected and not self.is_last_move and not self.is_highlighted:
                # Create a new effect only if we don't have one
                self.hover_effect = QGraphicsOpacityEffect(self)
                self.hover_effect.setOpacity(0.8)
                self.setGraphicsEffect(self.hover_effect)
                self.is_highlighted = True
        except Exception as e:
            print(f"Error in enterEvent: {str(e)}")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Remove highlight on mouse leave."""
        try:
            if self.is_highlighted:
                # Don't delete the effect, just remove it from the widget
                self.setGraphicsEffect(None)
                self.is_highlighted = False
        except Exception as e:
            print(f"Error in leaveEvent: {str(e)}")
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click on square."""
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
        """Custom painting for the square to include circular indicators."""
        # Call the parent's paintEvent to ensure proper rendering
        super().paintEvent(event)
        
        # Draw indicators for valid moves, castling, en passant, and check
        if self.is_valid_move or self.is_castling_move or self.is_checked or self.is_en_passant_move:
            try:
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                square_width = self.width()
                square_height = self.height()
                
                # Calculate indicator size based on square size
                indicator_size = min(square_width, square_height) * 0.4
                indicator_size_int = int(indicator_size)  # Convert to int for drawEllipse
                x_pos = int((square_width - indicator_size) / 2)  # Convert to int
                y_pos = int((square_height - indicator_size) / 2)  # Convert to int
                
                # Draw circular indicators for valid moves
                if self.is_valid_move:
                    painter.setPen(QPen(QColor(Config.VALID_MOVE_COLOR), 2))
                    painter.setBrush(QBrush(QColor(Config.VALID_MOVE_COLOR).lighter(160)))
                    # Use integers for all parameters
                    painter.drawEllipse(x_pos, y_pos, indicator_size_int, indicator_size_int)
                
                # Draw different indicator for castling
                elif self.is_castling_move:
                    painter.setPen(QPen(QColor(Config.CASTLING_MOVE_COLOR), 2))
                    painter.setBrush(QBrush(QColor(Config.CASTLING_MOVE_COLOR).lighter(160)))
                    # Use integers for all parameters
                    painter.drawEllipse(x_pos, y_pos, indicator_size_int, indicator_size_int)
                
                # Draw unique indicator for en passant
                elif self.is_en_passant_move:
                    painter.setPen(QPen(QColor(Config.EN_PASSANT_COLOR), 2))
                    painter.setBrush(QBrush(QColor(Config.EN_PASSANT_COLOR).lighter(160)))
                    # Use integers for all parameters
                    painter.drawEllipse(x_pos, y_pos, indicator_size_int, indicator_size_int)
                    
                    # Add a distinctive diamond shape for en passant
                    diamond_size = int(indicator_size * 0.7)  # Convert to int
                    painter.setPen(QPen(QColor(Config.EN_PASSANT_COLOR).darker(150), 1))
                    
                    # Calculate diamond points
                    center_x = x_pos + indicator_size_int // 2
                    center_y = y_pos + indicator_size_int // 2
                    half_size = diamond_size // 2
                    
                    # Draw diamond inside circle
                    points = [
                        QPoint(center_x, center_y - half_size),  # Top
                        QPoint(center_x + half_size, center_y),  # Right
                        QPoint(center_x, center_y + half_size),  # Bottom
                        QPoint(center_x - half_size, center_y),  # Left
                    ]
                    
                    # Draw the diamond
                    painter.drawPolygon(points)
                
                # Draw red highlight for check - but make it semi-transparent
                if self.is_checked:
                    # Use semi-transparent color for the check highlight
                    check_color = QColor(Config.CHECK_COLOR)
                    check_color.setAlpha(150)  # Make it semi-transparent
                    
                    painter.setPen(QPen(check_color, 3))
                    painter.setBrush(QBrush())  # No fill, just border
                    
                    # Draw border around the entire square
                    border_padding = 2
                    painter.drawRect(
                        border_padding, 
                        border_padding, 
                        self.width() - 2 * border_padding, 
                        self.height() - 2 * border_padding
                    )
                
                # Make sure to end painting
                painter.end()
            except Exception as e:
                print(f"Error in paintEvent: {str(e)}")
        
    def update_appearance(self):
        """Update the square's appearance based on its state."""
        # Determine base color based on square position and state
        if self.is_selected:
            base_color = Config.SELECTED_SQUARE_COLOR
        elif self.is_last_move:
            base_color = Config.LAST_MOVE_COLOR
        else:
            # Regular checkerboard pattern
            base_color = Config.LIGHT_SQUARE_COLOR if (self.row + self.col) % 2 == 0 else Config.DARK_SQUARE_COLOR
        
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
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to adjust font size for pieces."""
        super().resizeEvent(event)
        # Resize logic is now handled in the event filter

    def sizeHint(self):
        """Provide the preferred size for layout management."""
        return QSize(60, 60)  # Default preferred size
    
    def minimumSizeHint(self):
        """Provide the minimum acceptable size."""
        return QSize(40, 40)  # Minimum size to ensure pieces are visible
        
    def hasHeightForWidth(self):
        """Tell the layout system this widget maintains a square aspect ratio."""
        return True
        
    def heightForWidth(self, width):
        """Ensure height equals width to maintain square aspect ratio."""
        return width

class ThinkingIndicator(QLabel):
    """Visual indicator for AI thinking state with improved visibility and animation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        """Start the thinking animation with pulsing effect."""
        self.base_text = f"{ai_name} is thinking"
        self.dots = 0
        self.setText(f"{self.base_text}...")
        self.show()
        self.timer.start(Config.THINKING_DOT_INTERVAL)  # Update dots interval
        self.animation_timer.start(100)  # Pulse animation frames
        
    def stop_thinking(self):
        """Stop all animations and hide the indicator."""
        self.timer.stop()
        self.animation_timer.stop()
        self.hide()
        
    def update_dots(self):
        """Update the thinking dots animation."""
        self.dots = (self.dots + 1) % 4
        dot_text = "." * self.dots
        self.setText(f"{self.base_text}{dot_text.ljust(3)}")
        
    def pulse_effect(self):
        """Create a subtle pulsing effect by changing opacity."""
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