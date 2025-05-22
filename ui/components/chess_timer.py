"""
Enhanced Chess timer component with much better visibility and larger UI elements.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QTime
from PyQt5.QtGui import QFont, QColor, QPalette

class ChessTimer(QWidget):
    """Enhanced Chess timer widget with much better visibility and larger UI."""
    
    time_expired = pyqtSignal(str)  # Emitted when a player's time expires
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(100)  # Much smaller height since we're using horizontal layout
        
        # Timer state
        self.white_time_ms = 0
        self.black_time_ms = 0
        self.active_player = None  # 'white' or 'black'
        self.is_paused = True
        self.is_time_mode = False
        
        # Internal timer for updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.setInterval(100)  # Update every 100ms for smooth display
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the timer UI components with much better visibility."""
        # Main container with high contrast styling - WHITE background
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 15px;
                border: 4px solid #007bff;
            }
        """)
        
        # Add strong shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 123, 255, 150))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)  # Increased margins
        layout.setSpacing(12)
        
        # NO TITLE - just timer displays
        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(25)  # More space between timers
        
        # White player timer
        self.white_timer_frame = self.create_timer_display("White", True)
        timer_layout.addWidget(self.white_timer_frame)
        
        # Black player timer  
        self.black_timer_frame = self.create_timer_display("Black", False)
        timer_layout.addWidget(self.black_timer_frame)
        
        layout.addLayout(timer_layout)
        
        # Initially hide the timer (will be shown when time mode is enabled)
        self.hide()
        
    def create_timer_display(self, player_name, is_white):
        """Create a horizontal timer display with player name and time side by side."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(80)  # Smaller height since we're using horizontal layout
        
        # High contrast styling with MUCH better visibility
        if is_white:
            frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 4px solid #28a745;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
            text_color = "#000000"
            time_color = "#000000"
            border_color = "#28a745"
        else:
            frame.setStyleSheet("""
                QFrame {
                    background-color: #495057;
                    border: 4px solid #ffffff;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
            text_color = "#ffffff"
            time_color = "#ffffff"
            border_color = "#ffffff"
        
        # Use horizontal layout to place name and time side by side
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 1, 8, 16)
        layout.setSpacing(10)  # Reduce spacing to give more room for content
        
        # Player name on the left - make it wider to fit the text properly
        if is_white:
            display_name = "You (White)"  # Keep on single line but make box wider
        else:
            display_name = "AI (Black)"
            
        name_label = QLabel(display_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"""
            font-size: 15pt;
            font-weight: bold;
            color: {text_color};
            background-color: transparent;
            padding: 8px;
            margin: 2px;
            border: 2px solid {border_color};
            border-radius: 6px;
            min-width: 100px;
            max-width: 120px;
            min-height: 35px;
        """)
        layout.addWidget(name_label)
        
        # Time display on the right - adjust width for better balance
        time_label = QLabel("00:00")
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet(f"""
            font-size: 20pt;
            font-weight: bold;
            font-family: 'Arial', 'Courier New', monospace;
            color: {time_color};
            background-color: transparent;
            padding: 8px;
            border: 2px solid {border_color};
            border-radius: 6px;
            min-height: 35px;
            min-width: 85px;
            max-width: 100px;
        """)
        layout.addWidget(time_label)
        
        # Store references for easy access
        if is_white:
            self.white_name_label = name_label
            self.white_time_label = time_label
        else:
            self.black_name_label = name_label
            self.black_time_label = time_label
            
        return frame
        
    def set_time_mode(self, enabled, white_time_ms=0, black_time_ms=0):
        """Enable or disable time mode with specified times."""
        self.is_time_mode = enabled
        
        if enabled:
            self.white_time_ms = white_time_ms
            self.black_time_ms = black_time_ms
            self.update_display()
            self.show()
            # Update title with time information - NO TITLE NOW
            pass
        else:
            self.stop_timer()
            self.hide()
            
    def start_timer(self, player):
        """Start the timer for the specified player ('white' or 'black')."""
        if not self.is_time_mode:
            return
            
        self.active_player = player
        self.is_paused = False
        self.update_timer.start()
        self.update_active_player_display()
        
    def stop_timer(self):
        """Stop the timer."""
        self.update_timer.stop()
        self.is_paused = True
        self.active_player = None
        self.reset_player_displays()
        
    def pause_timer(self):
        """Pause the timer."""
        if self.is_time_mode:
            self.update_timer.stop()
            self.is_paused = True
            
    def resume_timer(self):
        """Resume the timer."""
        if self.is_time_mode and not self.is_paused and self.active_player:
            self.update_timer.start()
            
    def switch_player(self, new_player):
        """Switch the active timer to the new player."""
        if not self.is_time_mode:
            return
            
        self.active_player = new_player
        self.update_active_player_display()
        
    def update_display(self):
        """Update the timer displays and check for time expiration."""
        if not self.is_time_mode:
            return
            
        # Decrease time for active player
        if not self.is_paused and self.active_player:
            if self.active_player == 'white':
                self.white_time_ms = max(0, self.white_time_ms - 100)
                if self.white_time_ms <= 0:
                    self.time_expired.emit('white')
                    self.stop_timer()
                    return
            else:
                self.black_time_ms = max(0, self.black_time_ms - 100)
                if self.black_time_ms <= 0:
                    self.time_expired.emit('black')
                    self.stop_timer()
                    return
        
        # Update displays
        self.white_time_label.setText(self.format_time(self.white_time_ms))
        self.black_time_label.setText(self.format_time(self.black_time_ms))
        
        # Update colors based on remaining time
        self.update_time_colors()
        
    def update_time_colors(self):
        """Update timer colors based on remaining time with high visibility."""
        # White timer styling based on time remaining
        if self.white_time_ms <= 30000:  # Less than 30 seconds - RED ALERT
            white_time_style = """
                font-size: 20pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: #dc3545;
                padding: 8px;
                border: 2px solid #c82333;
                border-radius: 6px;
                min-height: 35px;
                min-width: 85px;
                max-width: 100px;
            """
        elif self.white_time_ms <= 60000:  # Less than 1 minute - ORANGE WARNING
            white_time_style = """
                font-size: 20pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #000000;
                background-color: #ffc107;
                padding: 8px;
                border: 2px solid #e0a800;
                border-radius: 6px;
                min-height: 35px;
                min-width: 85px;
                max-width: 100px;
            """
        else:  # Normal time - high contrast
            white_time_style = """
                font-size: 20pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #000000;
                background-color: transparent;
                padding: 8px;
                border: 2px solid #28a745;
                border-radius: 6px;
                min-height: 35px;
                min-width: 85px;
                max-width: 100px;
            """
            
        # Black timer styling based on time remaining
        if self.black_time_ms <= 30000:  # Less than 30 seconds - RED ALERT
            black_time_style = """
                font-size: 20pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: #dc3545;
                padding: 8px;
                border: 2px solid #c82333;
                border-radius: 6px;
                min-height: 35px;
                min-width: 85px;
                max-width: 100px;
            """
        elif self.black_time_ms <= 60000:  # Less than 1 minute - ORANGE WARNING
            black_time_style = """
                font-size: 20pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #000000;
                background-color: #ffc107;
                padding: 8px;
                border: 2px solid #e0a800;
                border-radius: 6px;
                min-height: 35px;
                min-width: 85px;
                max-width: 100px;
            """
        else:  # Normal time - high contrast
            black_time_style = """
                font-size: 20pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: transparent;
                padding: 8px;
                border: 2px solid #ffffff;
                border-radius: 6px;
                min-height: 35px;
                min-width: 85px;
                max-width: 100px;
            """
            
        self.white_time_label.setStyleSheet(white_time_style)
        self.black_time_label.setStyleSheet(black_time_style)
        
    def update_active_player_display(self):
        """Update the display to highlight the active player with high visibility."""
        if not self.is_time_mode or not self.active_player:
            self.reset_player_displays()
            return
            
        # Highlight active player's frame with bigger white background
        if self.active_player == 'white':
            self.white_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 5px solid #007bff;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
            self.black_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #495057;
                    border: 4px solid #6c757d;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
        else:
            self.white_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 4px solid #6c757d;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
            self.black_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #495057;
                    border: 5px solid #007bff;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
            
    def reset_player_displays(self):
        """Reset player displays to default styling with bigger white background."""
        self.white_timer_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 4px solid #28a745;
                border-radius: 12px;
                padding: 8px;
            }
        """)
        self.black_timer_frame.setStyleSheet("""
            QFrame {
                background-color: #495057;
                border: 4px solid #ffffff;
                border-radius: 12px;
                padding: 8px;
            }
        """)
        
    def format_time(self, milliseconds):
        """Format time in milliseconds to MM:SS format."""
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_remaining_times(self):
        """Get the remaining times for both players."""
        return self.white_time_ms, self.black_time_ms
        
    def set_player_names(self, white_name, black_name):
        """Set custom names for the players."""
        self.white_name_label.setText(white_name)
        self.black_name_label.setText(black_name)