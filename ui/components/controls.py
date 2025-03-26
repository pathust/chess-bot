from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QSize

class ControlButton(QPushButton):
    """Enhanced button with better visual feedback"""
    def __init__(self, text, color, icon=None, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)  # Adjusted for better appearance on small screens
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        
        self.updateStyle()
    
    def updateStyle(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self.base_color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(self.base_color, 1.1)};
            }}
            QPushButton:disabled {{
                background-color: #bbbbbb;
                color: #dddddd;
            }}
        """)
    
    def _lighten_color(self, color, factor):
        # Simple implementation to lighten a hex color
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(int(color[0:2], 16) * factor))
        g = min(255, int(int(color[2:4], 16) * factor))
        b = min(255, int(int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor):
        # Simple implementation to darken a hex color
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(int(color[0:2], 16) / factor))
        g = max(0, int(int(color[2:4], 16) / factor))
        b = max(0, int(int(color[4:6], 16) / factor))
        return f"#{r:02x}{g:02x}{b:02x}"

class EnhancedSlider(QWidget):
    """Custom slider with better visual design and labels"""
    valueChanged = pyqtSignal(int)
    
    def __init__(self, title, min_val, max_val, default_val, min_label, max_label, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with improved visibility
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: #e8e8e8;
                border-radius: 6px;
                border: 1px solid #cccccc;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 12pt; 
            font-weight: bold; 
            color: #333333;
        """)
        title_layout.addWidget(title_label)
        layout.addWidget(title_container)
        
        # Create the styled slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval((max_val - min_val) // 4)
        self.slider.setStyleSheet("""
            QSlider {
                height: 25px;
                margin: 5px 0;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #d0d0d0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
                border: 1px solid #1976D2;
            }
            QSlider::sub-page:horizontal {
                background: #64B5F6;
                border-radius: 4px;
            }
        """)
        self.slider.valueChanged.connect(self._emit_value_changed)
        layout.addWidget(self.slider)
        
        # Add min/max labels with IMPROVED CONTRAST
        labels_layout = QHBoxLayout()
        min_text = QLabel(min_label)
        min_text.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")  # Changed to white for better contrast
        
        max_text = QLabel(max_label)
        max_text.setAlignment(Qt.AlignRight)
        max_text.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")  # Changed to white for better contrast
        
        labels_layout.addWidget(min_text)
        labels_layout.addWidget(max_text)
        layout.addLayout(labels_layout)
        
    def _emit_value_changed(self, value):
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
    
    def setValue(self, value):
        self.slider.setValue(value)