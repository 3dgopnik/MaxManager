"""
Custom Toggle Switch Widget for MaxManager.

A modern toggle switch based on QCheckBox with smooth visual feedback.
"""

from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QPen


class ToggleSwitch(QCheckBox):
    """
    Custom toggle switch widget.
    
    Features:
    - Modern iOS-style toggle appearance
    - Smooth thumb animation (optional)
    - Customizable colors
    - Works like standard QCheckBox
    """
    
    def __init__(self, parent=None, track_radius=10, thumb_radius=8):
        super().__init__(parent)
        self.setFixedSize(30, 20)  # 30x20 as per design
        
        # Appearance settings
        self._track_radius = track_radius
        self._thumb_radius = thumb_radius
        self._margin = max(0, self._thumb_radius - self._track_radius)
        
        # Colors from design
        self._track_color_off = QColor("#666666")      # Gray when off
        self._track_color_on = QColor("#E0E0E0")       # Light gray when on
        self._thumb_color_off = QColor("#3A3A3A")      # Canvas content background when off
        self._thumb_color_on = QColor("#3A3A3A")       # Canvas content background when on
        self._track_opacity = 1.0
        
    def paintEvent(self, event):
        """Custom paint event for toggle appearance."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        # Calculate dimensions
        track_width = self.width()
        track_height = 2 * self._track_radius
        track_y = (self.height() - track_height) / 2
        
        # Draw track (background oval)
        track_color = self._track_color_on if self.isChecked() else self._track_color_off
        painter.setBrush(track_color)
        painter.drawRoundedRect(
            QRect(0, int(track_y), track_width, int(track_height)),
            self._track_radius,
            self._track_radius
        )
        
        # Calculate thumb position
        thumb_x = track_width - 2 * self._thumb_radius - 4 if self.isChecked() else 4
        thumb_y = (self.height() - 2 * self._thumb_radius) / 2
        
        # Draw thumb (dark circle matching background)
        thumb_color = self._thumb_color_on if self.isChecked() else self._thumb_color_off
        painter.setBrush(thumb_color)
        painter.drawEllipse(
            int(thumb_x),
            int(thumb_y),
            2 * self._thumb_radius,
            2 * self._thumb_radius
        )
        
        painter.end()
        
    def hitButton(self, pos):
        """Ensure the entire widget area is clickable."""
        return self.contentsRect().contains(pos)
        
    def set_track_color_on(self, color: str):
        """Set track color when checked."""
        self._track_color_on = QColor(color)
        self.update()
        
    def set_track_color_off(self, color: str):
        """Set track color when unchecked."""
        self._track_color_off = QColor(color)
        self.update()
        
    def set_thumb_color(self, color: str):
        """Set thumb (circle) color."""
        self._thumb_color = QColor(color)
        self.update()

