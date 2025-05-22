"""
Final fixed Time mode selection dialog - no double popup.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSpinBox, QRadioButton, QButtonGroup, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem, QGridLayout, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class TimeModeDialog(QDialog):
    """Fixed dialog for selecting time control settings - no double popup."""
    
    # Remove the signal that was causing issues
    # time_settings_selected = pyqtSignal(bool, int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Time Control Settings")
        self.setModal(True)
        self.setFixedSize(500, 450)
        
        # Use standard window flags
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Simple, high contrast styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #212529;
            }
            QLabel {
                color: #212529;
                font-weight: bold;
            }
            QFrame {
                background-color: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QRadioButton {
                color: #212529;
                font-size: 14pt;
                font-weight: bold;
                spacing: 10px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #6c757d;
                border-radius: 9px;
                background-color: #ffffff;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #007bff;
                border-radius: 9px;
                background-color: #007bff;
            }
            QPushButton {
                font-size: 12pt;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                min-height: 30px;
            }
            QSpinBox {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 12pt;
                min-height: 20px;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #007bff;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI with visible content."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⏱️ Time Control Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 20pt;
            font-weight: bold;
            color: #212529;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 8px;
            border: 2px solid #007bff;
        """)
        layout.addWidget(title)
        
        # Time mode selection
        mode_frame = QFrame()
        mode_layout = QVBoxLayout(mode_frame)
        
        mode_title = QLabel("Choose Time Mode:")
        mode_title.setStyleSheet("font-size: 14pt; color: #212529; margin-bottom: 10px;")
        mode_layout.addWidget(mode_title)
        
        self.time_mode_group = QButtonGroup()
        
        self.no_time_radio = QRadioButton("🚫 No Time Limit")
        self.no_time_radio.setChecked(True)
        self.no_time_radio.setStyleSheet("color: #212529; font-size: 14pt;")
        self.time_mode_group.addButton(self.no_time_radio, 0)
        mode_layout.addWidget(self.no_time_radio)
        
        self.time_mode_radio = QRadioButton("⏰ Time Control")
        self.time_mode_radio.setStyleSheet("color: #212529; font-size: 14pt;")
        self.time_mode_group.addButton(self.time_mode_radio, 1)
        mode_layout.addWidget(self.time_mode_radio)
        
        layout.addWidget(mode_frame)
        
        # Time settings frame
        self.time_settings_frame = QFrame()
        time_settings_layout = QVBoxLayout(self.time_settings_frame)
        
        # Preset buttons section
        presets_label = QLabel("⚡ Quick Presets:")
        presets_label.setStyleSheet("font-size: 14pt; color: #212529; margin-bottom: 8px;")
        time_settings_layout.addWidget(presets_label)
        
        # Create preset buttons
        presets_container = QWidget()
        presets_layout = QHBoxLayout(presets_container)
        presets_layout.setSpacing(8)
        
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
                    background-color: #e9ecef;
                    color: #495057;
                    border: 2px solid #ced4da;
                    font-size: 11pt;
                    min-width: 60px;
                    min-height: 30px;
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
        
        # Custom time section
        custom_label = QLabel("🔧 Custom Time (per player):")
        custom_label.setStyleSheet("font-size: 14pt; color: #212529; margin-top: 15px; margin-bottom: 8px;")
        time_settings_layout.addWidget(custom_label)
        
        # Custom time inputs
        custom_container = QWidget()
        custom_layout = QHBoxLayout(custom_container)
        custom_layout.setSpacing(15)
        
        # Minutes
        min_label = QLabel("Minutes:")
        min_label.setStyleSheet("font-size: 12pt; color: #212529;")
        custom_layout.addWidget(min_label)
        
        self.minutes_spinbox = QSpinBox()
        self.minutes_spinbox.setRange(1, 60)
        self.minutes_spinbox.setValue(5)
        self.minutes_spinbox.setSuffix(" min")
        custom_layout.addWidget(self.minutes_spinbox)
        
        # Seconds  
        sec_label = QLabel("Seconds:")
        sec_label.setStyleSheet("font-size: 12pt; color: #212529;")
        custom_layout.addWidget(sec_label)
        
        self.seconds_spinbox = QSpinBox()
        self.seconds_spinbox.setRange(0, 59)
        self.seconds_spinbox.setValue(0)
        self.seconds_spinbox.setSuffix(" sec")
        custom_layout.addWidget(self.seconds_spinbox)
        
        custom_layout.addStretch()
        time_settings_layout.addWidget(custom_container)
        
        layout.addWidget(self.time_settings_frame)
        
        # Initially disable time settings
        self.time_settings_frame.setEnabled(False)
        
        # Connect signals
        self.time_mode_group.buttonClicked.connect(self.on_mode_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.ok_button = QPushButton("✅ Start Game")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 150px;
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
                font-size: 14pt;
                font-weight: bold;
                padding: 12px 24px;
                min-width: 150px;
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
        """Handle time mode radio button changes."""
        is_time_mode = self.time_mode_radio.isChecked()
        self.time_settings_frame.setEnabled(is_time_mode)
        
        if is_time_mode:
            self.ok_button.setText("✅ Start Timed Game")
            self.time_settings_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #007bff;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        else:
            self.ok_button.setText("✅ Start Game")
            self.time_settings_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
    
    def set_preset_time(self, time_ms):
        """Set preset time values and enable time control."""
        total_seconds = time_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        self.minutes_spinbox.setValue(minutes)
        self.seconds_spinbox.setValue(seconds)
        
        # Automatically enable time control mode
        self.time_mode_radio.setChecked(True)
        self.on_mode_changed(self.time_mode_radio)
    
    def get_time_settings(self):
        """Get the selected time settings."""
        is_time_mode = self.time_mode_radio.isChecked()
        
        if is_time_mode:
            minutes = self.minutes_spinbox.value()
            seconds = self.seconds_spinbox.value()
            time_ms = (minutes * 60 + seconds) * 1000
            return is_time_mode, time_ms, time_ms
        else:
            return False, 0, 0
    
    def accept(self):
        """Accept the dialog without emitting signals."""
        is_time_mode, white_time, black_time = self.get_time_settings()
        
        # Validate time settings
        if is_time_mode and white_time <= 0:
            print("Error: Please set a valid time (greater than 0)")
            return
        
        # FIXED: Don't emit signal - just accept the dialog
        # The parent will get settings via get_time_settings() method
        super().accept()