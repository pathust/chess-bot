from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

class AnimatedLabel(QLabel):
    """Custom QLabel with animation capabilities for chess pieces"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)  # 300ms for piece movement
        
    def move_to(self, target_pos):
        """Animate movement to target position"""
        start_pos = self.pos()
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(target_pos)
        self.animation.start()