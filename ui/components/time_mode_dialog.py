"""
Enhanced Time mode selection dialog with much better visibility and larger UI elements.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSpinBox, QRadioButton, QButtonGroup, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem, QGridLayout, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class TimeModeDialog(QDialog):
    """Enhanced dialog for selecting time control settings with much better visibility."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Time Control Settings")
        self.setModal(True)
        self.setFixedSize(800, 700)  # Much bigger dialog window
        
        # Use standard window flags
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Much better contrast and visibility styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #000000;
                font-size: 10pt;
            }
            QLabel {
                color: #000000;
                font-weight: bold;
                font-size: 10pt;
            }
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 6px;
                padding: 8px;
            }
            QRadioButton {
                color: #000000;
                font-size: 12pt;
                font-weight: bold;
                spacing: 8px;
                padding: 4px;
                background-color: #ffffff;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #333333;
                border-radius: 9px;
                background-color: #ffffff;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #007bff;
                border-radius: 9px;
                background-color: #007bff;
            }
            QPushButton {
                font-size: 11pt;
                font-weight: bold;
                padding: 6px 10px;
                border-radius: 4px;
                border: 1px solid #333333;
                min-height: 26px;
                min-width: 70px;
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QSpinBox {
                padding: 6px;
                border: 2px solid #333333;
                border-radius: 4px;
                background-color: #ffffff;
                color: #000000;
                font-size: 11pt;
                font-weight: bold;
                min-height: 22px;
                min-width: 70px;
            }
            QSpinBox:focus {
                border: 2px solid #007bff;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI with bigger window but smaller content inside."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)  # Bigger margins for bigger window
        layout.setSpacing(20)  # More spacing between sections
        
        # High contrast title
        title = QLabel("⏱️ Time Control Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #000000;
            padding: 10px;
            background-color: #007bff;
            color: #ffffff;
            border-radius: 6px;
            border: 2px solid #0056b3;
        """)
        layout.addWidget(title)
        
        # Time mode selection with small elements
        mode_frame = QFrame()
        mode_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        mode_layout = QVBoxLayout(mode_frame)
        
        mode_title = QLabel("Choose Time Mode:")
        mode_title.setStyleSheet("""
            font-size: 14pt; 
            color: #000000; 
            margin-bottom: 6px;
            font-weight: bold;
            background-color: #ffffff;
            padding: 4px;
            border-radius: 3px;
        """)
        mode_layout.addWidget(mode_title)
        
        self.time_mode_group = QButtonGroup()
        
        # Small radio buttons with clear text
        self.no_time_radio = QRadioButton("🚫 No Time Limit")
        self.no_time_radio.setChecked(True)
        self.no_time_radio.setStyleSheet("""
            color: #000000; 
            font-size: 12pt;
            font-weight: bold;
            padding: 3px;
        """)
        self.time_mode_group.addButton(self.no_time_radio, 0)
        mode_layout.addWidget(self.no_time_radio)
        
        self.time_mode_radio = QRadioButton("⏰ Time Control")
        self.time_mode_radio.setStyleSheet("""
            color: #000000; 
            font-size: 12pt;
            font-weight: bold;
            padding: 3px;
        """)
        self.time_mode_group.addButton(self.time_mode_radio, 1)
        mode_layout.addWidget(self.time_mode_radio)
        
        layout.addWidget(mode_frame)
        
        # Time settings frame with small elements
        self.time_settings_frame = QFrame()
        self.time_settings_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        time_settings_layout = QVBoxLayout(self.time_settings_frame)
        
        # Preset buttons section with small buttons
        presets_label = QLabel("⚡ Quick Presets:")
        presets_label.setStyleSheet("""
            font-size: 12pt; 
            color: #000000; 
            margin-bottom: 4px;
            font-weight: bold;
        """)
        time_settings_layout.addWidget(presets_label)
        
        # Create small preset buttons
        presets_container = QWidget()
        presets_layout = QHBoxLayout(presets_container)
        presets_layout.setSpacing(4)
        
        preset_times = [
            ("1 min", 1 * 60 * 1000),
            ("3 min", 3 * 60 * 1000),
            ("5 min", 5 * 60 * 1000),
            ("10 min", 10 * 60 * 1000),
            ("15 min", 15 * 60 * 1000)
        ]
        
        for preset_name, preset_ms in preset_times:
            btn = QPushButton(preset_name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #007bff;
                    font-size: 10pt;
                    font-weight: bold;
                    min-width: 50px;
                    min-height: 26px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #007bff;
                    color: white;
                    border: 2px solid #0056b3;
                }
                QPushButton:pressed {
                    background-color: #0056b3;
                }
            """)
            btn.clicked.connect(lambda checked, ms=preset_ms: self.set_preset_time(ms))
            presets_layout.addWidget(btn)
            
        time_settings_layout.addWidget(presets_container)
        
        
        # Custom time inputs with small controls
        custom_container = QWidget()
        custom_layout = QHBoxLayout(custom_container)
        custom_layout.setSpacing(8)
        
        # Minutes with small controls
        min_label = QLabel("Minutes:")
        min_label.setStyleSheet("""
            font-size: 10pt; 
            color: #000000;
            font-weight: bold;
        """)
        custom_layout.addWidget(min_label)
        
        self.minutes_spinbox = QSpinBox()
        self.minutes_spinbox.setRange(1, 60)
        self.minutes_spinbox.setValue(5)
        self.minutes_spinbox.setSuffix(" min")
        self.minutes_spinbox.setStyleSheet("""
            font-size: 10pt;
            padding: 4px;
            min-width: 65px;
            min-height: 20px;
        """)
        custom_layout.addWidget(self.minutes_spinbox)
        
        # Seconds with small controls
        sec_label = QLabel("Seconds:")
        sec_label.setStyleSheet("""
            font-size: 10pt; 
            color: #000000;
            font-weight: bold;
        """)
        custom_layout.addWidget(sec_label)
        
        self.seconds_spinbox = QSpinBox()
        self.seconds_spinbox.setRange(0, 59)
        self.seconds_spinbox.setValue(0)
        self.seconds_spinbox.setSuffix(" sec")
        self.seconds_spinbox.setStyleSheet("""
            font-size: 10pt;
            padding: 4px;
            min-width: 65px;
            min-height: 20px;
        """)
        custom_layout.addWidget(self.seconds_spinbox)
        
        custom_layout.addStretch()
        time_settings_layout.addWidget(custom_container)
        
        layout.addWidget(self.time_settings_frame)
        
        increment_label = QLabel("⏲️ Time Increment (per move):")
        increment_label.setStyleSheet("""
            font-size: 12pt; 
            color: #000000; 
            margin-top: 8px; 
            margin-bottom: 4px;
            font-weight: bold;
        """)
        time_settings_layout.addWidget(increment_label)
        
        # Increment inputs with small controls
        increment_container = QWidget()
        increment_layout = QHBoxLayout(increment_container)
        increment_layout.setSpacing(8)
        
        # Increment seconds
        inc_label = QLabel("Increment:")
        inc_label.setStyleSheet("""
            font-size: 10pt; 
            color: #000000;
            font-weight: bold;
        """)
        increment_layout.addWidget(inc_label)
        
        self.increment_spinbox = QSpinBox()
        self.increment_spinbox.setRange(0, 30)
        self.increment_spinbox.setValue(3)  # Default 3 seconds
        self.increment_spinbox.setSuffix(" sec")
        self.increment_spinbox.setStyleSheet("""
            font-size: 10pt;
            padding: 4px;
            min-width: 65px;
            min-height: 20px;
        """)
        increment_layout.addWidget(self.increment_spinbox)
        
        # Add explanation
        inc_explain = QLabel("(added after each move)")
        inc_explain.setStyleSheet("""
            font-size: 9pt; 
            color: #666666;
            font-style: italic;
        """)
        increment_layout.addWidget(inc_explain)
        
        increment_layout.addStretch()
        time_settings_layout.addWidget(increment_container)
        
        # Initially disable time settings
        self.time_settings_frame.setEnabled(False)
        
        # Connect signals
        self.time_mode_group.buttonClicked.connect(self.on_mode_changed)
        
        # Small but visible buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.ok_button = QPushButton("✅ Start Game")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 8px 12px;
                min-width: 120px;
                min-height: 32px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 8px 12px;
                min-width: 120px;
                min-height: 32px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def on_mode_changed(self, button):
        """Handle time mode radio button changes with visual feedback."""
        is_time_mode = self.time_mode_radio.isChecked()
        self.time_settings_frame.setEnabled(is_time_mode)
        
        if is_time_mode:
            self.ok_button.setText("✅ Start Timed Game")
            self.time_settings_frame.setStyleSheet("""
                QFrame {
                    background-color: #e6ffe6;
                    border: 1px solid #00cc00;
                    border-radius: 4px;
                    padding: 8px;
                }
            """)
        else:
            self.ok_button.setText("✅ Start Game")
            self.time_settings_frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                }
            """)
    
    def set_preset_time(self, time_ms):
        """Set preset time values and enable time control with visual feedback."""
        total_seconds = time_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        self.minutes_spinbox.setValue(minutes)
        self.seconds_spinbox.setValue(seconds)
        
        # Automatically enable time control mode
        self.time_mode_radio.setChecked(True)
        self.on_mode_changed(self.time_mode_radio)
        
        # Highlight the selected time with visual feedback
        time_str = f"{minutes}:{seconds:02d}"
        self.ok_button.setText(f"✅ Start Timed Game ({time_str})")
    
    def get_time_settings(self):
        """Get the selected time settings including increment."""
        is_time_mode = self.time_mode_radio.isChecked()
        
        if is_time_mode:
            minutes = self.minutes_spinbox.value()
            seconds = self.seconds_spinbox.value()
            increment_seconds = self.increment_spinbox.value()
            
            time_ms = (minutes * 60 + seconds) * 1000
            increment_ms = increment_seconds * 1000
            
            return is_time_mode, time_ms, time_ms, increment_ms, increment_ms
        else:
            return False, 0, 0, 0, 0
    
    def accept(self):
        """Accept the dialog with validation and user feedback."""
        is_time_mode, white_time, black_time, white_inc, black_inc = self.get_time_settings()
        
        # Validate time settings with clear feedback
        if is_time_mode and white_time <= 0:
            # Change button to show error
            self.ok_button.setText("❌ Please set valid time!")
            self.ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    font-size: 18pt;
                    font-weight: bold;
                    padding: 15px 30px;
                    min-width: 200px;
                    min-height: 60px;
                    border-radius: 10px;
                }
            """)
            # Reset button after 2 seconds
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.reset_ok_button)
            return
        
        # Accept the dialog
        super().accept()
    
    def reset_ok_button(self):
        """Reset the OK button to normal state."""
        is_time_mode = self.time_mode_radio.isChecked()
        if is_time_mode:
            self.ok_button.setText("✅ Start Timed Game")
        else:
            self.ok_button.setText("✅ Start Game")
        
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 8px 12px;
                min-width: 120px;
                min-height: 32px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)