from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt
from ui.components.controls import ControlButton, EnhancedSlider

class AIControlPanel(QScrollArea):
    """AI control panel with improved responsive design"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #2c3e50;  /* Darker blue background for better contrast */
                border-radius: 10px;
                border: 2px solid #1a2530;  /* Darker border */
            }
        """)
        
        # Create inner widget for the scroll area
        inner_widget = QWidget()
        inner_widget.setStyleSheet("background-color: #2c3e50;")  
        self.setWidget(inner_widget)
        
        # Create main layout with adaptive spacing
        self.main_layout = QVBoxLayout(inner_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title header
        title = QLabel("AI Controls")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: white; 
            padding: 8px;
            background-color: #34495e;  /* Slightly lighter than panel for contrast */
            border-radius: 6px;
        """)
        self.main_layout.addWidget(title)
                
        # Create a responsive layout that can adapt to window width
        responsive_container = QWidget()
        responsive_layout = QHBoxLayout(responsive_container)
        responsive_layout.setSpacing(10)
        
        # Create button container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(8)
        
        # Start button - brighter green
        self.start_button = ControlButton("▶ Start", "#2ecc71")  # Brighter green

        # Pause button - brighter orange
        self.pause_button = ControlButton("⏸ Pause", "#f39c12")  # Brighter orange

        # Reset button - brighter blue
        self.reset_button = ControlButton("↻ Reset", "#3498db")  # Brighter blue

        # Return to Home button - brighter red
        self.home_button = ControlButton("🏠 Home", "#e74c3c")  # Brighter red
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.home_button)
        button_layout.addStretch(1)
        
        # Add button container to responsive layout
        responsive_layout.addWidget(button_container, 1)
        
        # Create slider container
        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setSpacing(10)
        
        # Create enhanced sliders
        self.speed_slider = EnhancedSlider(
            "AI Move Speed:", 200, 2000, 800, "Fast", "Slow"
        )
        slider_layout.addWidget(self.speed_slider)
        
        self.depth_slider = EnhancedSlider(
            "AI Thinking Depth:", 2, 5, 3, "Shallow", "Deep"
        )
        slider_layout.addWidget(self.depth_slider)
        
        # Add current depth display with improved visibility
        depth_container = QFrame()
        depth_container.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 5px;
                padding: 6px;
            }
        """)
        
        depth_layout = QVBoxLayout(depth_container)
        self.depth_value = QLabel("Current depth: 3")
        self.depth_value.setAlignment(Qt.AlignCenter)
        self.depth_value.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: white;
            padding: 2px;
        """)
        depth_layout.addWidget(self.depth_value)
        slider_layout.addWidget(depth_container)
        slider_layout.addStretch(1)
        
        # Add slider container to responsive layout
        responsive_layout.addWidget(slider_container, 1)
        
        # Add responsive container to main layout
        self.main_layout.addWidget(responsive_container)
        
        # Set resize behavior to adapt to parent size
        responsive_layout.setStretch(0, 1)
        responsive_layout.setStretch(1, 1)