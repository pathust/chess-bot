"""
UI control components for the chess application.
This module provides custom button and slider components for the chess UI.
"""

from PyQt5.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QColor

from utils.config import Config

class ControlButton(QPushButton):
    """Enhanced button with better visual feedback."""
    
    def __init__(self, text, color, icon=None, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)  # Base height
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        
        self.updateStyle()
    
    def updateStyle(self):
        """Update the button style with modern visuals."""
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
        
        # Add drop shadow effect for depth (instead of box-shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def _lighten_color(self, color, factor):
        """Lighten a hex color by a given factor."""
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(int(color[0:2], 16) * factor))
        g = min(255, int(int(color[2:4], 16) * factor))
        b = min(255, int(int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor):
        """Darken a hex color by a given factor."""
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(int(color[0:2], 16) / factor))
        g = max(0, int(int(color[2:4], 16) / factor))
        b = max(0, int(int(color[4:6], 16) / factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def sizeHint(self):
        """Return the preferred size for the button."""
        base_size = super().sizeHint()
        return QSize(max(base_size.width(), 120), 50)

class EnhancedSlider(QWidget):
    """Custom slider with better visual design and labels."""
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, title, min_val, max_val, default_val, min_label, max_label, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with improved visibility
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                border: none;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 12pt; 
            font-weight: bold; 
            color: white;
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
                background: #3d566e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 1px solid #1976D2;
            }
            QSlider::sub-page:horizontal {
                background: #64B5F6;
                border-radius: 4px;
            }
        """)
        self.slider.valueChanged.connect(self._emit_value_changed)
        layout.addWidget(self.slider)
        
        # Add min/max labels with improved contrast
        labels_layout = QHBoxLayout()
        self.min_label = QLabel(min_label)
        self.min_label.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")
        
        self.max_label = QLabel(max_label)
        self.max_label.setAlignment(Qt.AlignRight)
        self.max_label.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")
        
        # Add value display
        self.value_label = QLabel(f"Value: {default_val}")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")
        
        labels_layout.addWidget(self.min_label)
        labels_layout.addWidget(self.value_label)
        labels_layout.addWidget(self.max_label)
        
        layout.addLayout(labels_layout)
        
    def _emit_value_changed(self, value):
        """Handle value changes and update display."""
        self.value_label.setText(f"Value: {value}")
        self.valueChanged.emit(value)
        
    def value(self):
        """Get the current slider value."""
        return self.slider.value()
    
    def setValue(self, value):
        """Set the slider value."""
        self.slider.setValue(value)
        self.value_label.setText(f"Value: {value}")
    
    def setMinLabel(self, text):
        """Set the minimum label text."""
        self.min_label.setText(text)
    
    def setMaxLabel(self, text):
        """Set the maximum label text."""
        self.max_label.setText(text)
    
    def setValueLabel(self, text):
        """Set the custom value label text (overrides default)."""
        self.value_label.setText(text)


class UndoButton(QPushButton):
    """Button specifically for the undo move functionality."""
    
    def __init__(self, parent=None):
        super().__init__("↩ Undo", parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setToolTip("Undo the last move")
        self.updateStyle()
    
    def updateStyle(self):
        """Set the button style."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.UNDO_BUTTON_COLOR};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(Config.UNDO_BUTTON_COLOR)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(Config.UNDO_BUTTON_COLOR)};
            }}
            QPushButton:disabled {{
                background-color: #bbbbbb;
                color: #dddddd;
            }}
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def _lighten_color(self, color, factor=1.1):
        """Lighten a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(int(color[0:2], 16) * factor))
        g = min(255, int(int(color[2:4], 16) * factor))
        b = min(255, int(int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor=1.1):
        """Darken a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(int(color[0:2], 16) / factor))
        g = max(0, int(int(color[2:4], 16) / factor))
        b = max(0, int(int(color[4:6], 16) / factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def sizeHint(self):
        """Return the preferred size for the button."""
        base_size = super().sizeHint()
        return QSize(max(base_size.width(), 120), 50)


class ResignButton(QPushButton):
    """Button for the player to resign the game."""
    
    def __init__(self, parent=None):
        super().__init__("🏳️ Resign", parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setToolTip("Resign the current game")
        self.updateStyle()
    
    def updateStyle(self):
        """Set the button style with warning colors."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.RESIGN_BUTTON_COLOR};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(Config.RESIGN_BUTTON_COLOR)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(Config.RESIGN_BUTTON_COLOR)};
            }}
            QPushButton:disabled {{
                background-color: #bbbbbb;
                color: #dddddd;
            }}
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def _lighten_color(self, color, factor=1.1):
        """Lighten a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = min(255, int(int(color[0:2], 16) * factor))
        g = min(255, int(int(color[2:4], 16) * factor))
        b = min(255, int(int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, factor=1.1):
        """Darken a hex color."""
        if color.startswith('#'):
            color = color[1:]
        r = max(0, int(int(color[0:2], 16) / factor))
        g = max(0, int(int(color[2:4], 16) / factor))
        b = max(0, int(int(color[4:6], 16) / factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def sizeHint(self):
        """Return the preferred size for the button."""
        base_size = super().sizeHint()
        return QSize(max(base_size.width(), 120), 50)