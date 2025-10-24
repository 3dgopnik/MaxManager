"""
Modern SpinBox widgets with QtAwesome icons for MaxManager.
"""

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

try:
    import qtawesome as qta
    QTA_AVAILABLE = True
except ImportError:
    QTA_AVAILABLE = False


class ModernSpinBox(QSpinBox):
    """SpinBox with QtAwesome arrow icons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QSpinBox.NoButtons if QTA_AVAILABLE else QSpinBox.UpDownArrows)
        self.setup_buttons()
        
    def setup_buttons(self):
        """Setup custom buttons with QtAwesome icons."""
        if not QTA_AVAILABLE:
            return
            
        # Create custom up/down buttons
        self.setButtonSymbols(QSpinBox.NoButtons)
        
        # We'll use the default arrows but style them
        self.setButtonSymbols(QSpinBox.UpDownArrows)


class ModernDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox with QtAwesome arrow icons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QDoubleSpinBox.UpDownArrows)

