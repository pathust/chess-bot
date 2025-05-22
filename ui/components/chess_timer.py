"""
Improved Chess timer component with better UI visibility.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QTime
from PyQt5.QtGui import QFont, QColor, QPalette

class ChessTimer(QWidget):
    """Improved Chess timer widget with better visibility."""
    
    time_expired = pyqtSignal(str)  # Emitted when a player's time expires
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(140)  # Increased height for better visibility
        
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
        """Setup the timer UI components with improved visibility."""
        # Main container with better styling
        self.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border-radius: 12px;
                border: 3px solid #3498db;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Title with better visibility
        self.title_label = QLabel("Game Timers")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #ffffff;
            background-color: #2c3e50;
            padding: 8px;
            border-radius: 6px;
            border: 2px solid #3498db;
        """)
        layout.addWidget(self.title_label)
        
        # Timer displays with improved layout
        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(25)
        
        # White player timer
        self.white_timer_frame = self.create_timer_display("White", True)
        timer_layout.addWidget(self.white_timer_frame)
        
        # VS separator
        vs_label = QLabel("VS")
        vs_label.setAlignment(Qt.AlignCenter)
        vs_label.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #3498db;
            background-color: transparent;
            padding: 5px;
        """)
        timer_layout.addWidget(vs_label)
        
        # Black player timer  
        self.black_timer_frame = self.create_timer_display("Black", False)
        timer_layout.addWidget(self.black_timer_frame)
        
        layout.addLayout(timer_layout)
        
        # Initially hide the timer (will be shown when time mode is enabled)
        self.hide()
        
    def create_timer_display(self, player_name, is_white):
        """Create an improved timer display for a player."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(80)  # Fixed height for consistency
        
        # Improved styling with better contrast
        if is_white:
            frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 3px solid #bdc3c7;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
            text_color = "#2c3e50"
            time_color = "#2c3e50"
        else:
            frame.setStyleSheet("""
                QFrame {
                    background-color: #2c3e50;
                    border: 3px solid #bdc3c7;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
            text_color = "#ffffff"
            time_color = "#ffffff"
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Player name with better styling
        name_label = QLabel(player_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"""
            font-size: 13pt;
            font-weight: bold;
            color: {text_color};
            background-color: transparent;
            padding: 2px;
        """)
        layout.addWidget(name_label)
        
        # Time display with much better visibility
        time_label = QLabel("00:00")
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet(f"""
            font-size: 24pt;
            font-weight: bold;
            font-family: 'Arial', 'Courier New', monospace;
            color: {time_color};
            background-color: transparent;
            padding: 4px;
            border: 2px solid {text_color};
            border-radius: 5px;
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
            # Update title with time information
            time_str = self.format_time(white_time_ms)
            self.title_label.setText(f"Game Timers - {time_str} each")
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
        """Update timer colors based on remaining time with better visibility."""
        # White timer styling based on time remaining
        if self.white_time_ms <= 30000:  # Less than 30 seconds
            white_time_style = """
                font-size: 24pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: #e74c3c;
                padding: 4px;
                border: 2px solid #c0392b;
                border-radius: 5px;
            """
        elif self.white_time_ms <= 60000:  # Less than 1 minute
            white_time_style = """
                font-size: 24pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: #f39c12;
                padding: 4px;
                border: 2px solid #e67e22;
                border-radius: 5px;
            """
        else:
            white_time_style = """
                font-size: 24pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #2c3e50;
                background-color: transparent;
                padding: 4px;
                border: 2px solid #2c3e50;
                border-radius: 5px;
            """
            
        # Black timer styling based on time remaining
        if self.black_time_ms <= 30000:  # Less than 30 seconds
            black_time_style = """
                font-size: 24pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: #e74c3c;
                padding: 4px;
                border: 2px solid #c0392b;
                border-radius: 5px;
            """
        elif self.black_time_ms <= 60000:  # Less than 1 minute
            black_time_style = """
                font-size: 24pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: #f39c12;
                padding: 4px;
                border: 2px solid #e67e22;
                border-radius: 5px;
            """
        else:
            black_time_style = """
                font-size: 24pt;
                font-weight: bold;
                font-family: 'Arial', 'Courier New', monospace;
                color: #ffffff;
                background-color: transparent;
                padding: 4px;
                border: 2px solid #ffffff;
                border-radius: 5px;
            """
            
        self.white_time_label.setStyleSheet(white_time_style)
        self.black_time_label.setStyleSheet(black_time_style)
        
    def update_active_player_display(self):
        """Update the display to highlight the active player with better visibility."""
        if not self.is_time_mode or not self.active_player:
            self.reset_player_displays()
            return
            
        # Highlight active player's frame with glowing effect
        if self.active_player == 'white':
            self.white_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 4px solid #3498db;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
            self.black_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #2c3e50;
                    border: 3px solid #7f8c8d;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
        else:
            self.white_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 3px solid #7f8c8d;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
            self.black_timer_frame.setStyleSheet("""
                QFrame {
                    background-color: #2c3e50;
                    border: 4px solid #3498db;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)
            
    def reset_player_displays(self):
        """Reset player displays to default styling."""
        self.white_timer_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 3px solid #bdc3c7;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        self.black_timer_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 3px solid #bdc3c7;
                border-radius: 10px;
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