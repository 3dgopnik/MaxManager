"""
Modern Header for MaxManager
Contextual header with dynamic tabs
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal


class ModernHeader(QWidget):
    """Contextual header with dynamic tabs."""
    
    # Signal: (context_key, tab_name)
    tab_changed = Signal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        
        # Color mapping for tab indicators
        self.tab_colors = {
            0: '#9C823A',   # yellow
            1: '#669999',   # turquoise
            2: '#CCCC33',   # yellow-green
            3: '#FFCC99',   # peach
            4: '#6666CC',   # blue-violet
        }
        
        self.current_context = None
        self.current_tabs = []
        self.active_tab = None
        self.tab_widgets = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize header UI."""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 40, 0, 0)  # 40px top margin - tabs start at 40px from top
        self.layout.setSpacing(0)  # No spacing between tabs
        
        self.apply_styles()
        
    def set_context(self, context_key, tabs_list):
        """Switch header context (called when sidebar button clicked)."""
        self.current_context = context_key
        self.current_tabs = tabs_list
        
        # Clear existing tabs and stretch
        for widget in self.tab_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        self.tab_widgets.clear()
        
        # Remove any existing stretch items
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                # Just remove the spacer item
                pass
        
        # Create new tabs
        for idx, tab_name in enumerate(tabs_list):
            color = self.tab_colors.get(idx, '#9C823A')
            tab_widget = self.create_tab(tab_name, color)
            self.tab_widgets.append(tab_widget)
            self.layout.addWidget(tab_widget)  # Add directly without spacing
            
            # Add thin separator between tabs
            separator = QWidget()
            separator.setFixedWidth(1)
            separator.setStyleSheet("background-color: #222222;")
            self.layout.addWidget(separator)
        
        # Add stretch at the end to push tabs to the left
        self.layout.addStretch()
        
        # Set first tab as active
        if tabs_list:
            self.set_active_tab(tabs_list[0])
            
    def create_tab(self, name, indicator_color):
        """Create tab button with indicator."""
        container = QWidget()
        container.setFixedSize(160, 40)  # 160px button only (indicator managed separately)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab button
        btn = QPushButton(name)
        btn.setObjectName(f"tab_{name}")
        btn.setFixedSize(160, 40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.on_tab_clicked(name))
        
        # Tooltip
        btn.setToolTip(f"{name} settings")
        
        layout.addWidget(btn)
        
        # Color indicator (10x40) - positioned absolutely
        indicator = QWidget(container)
        indicator.setObjectName(f"ind_{name}")
        indicator.setFixedSize(10, 40)
        indicator.setStyleSheet(f"background-color: {indicator_color};")
        indicator.setVisible(False)  # Hidden by default
        indicator.move(150, 0)  # Position at right edge
        
        return container
        
    def on_tab_clicked(self, tab_name):
        """Handle tab click."""
        self.set_active_tab(tab_name)
        self.tab_changed.emit(self.current_context, tab_name)
        
    def set_active_tab(self, tab_name):
        """Set active tab and update styling."""
        self.active_tab = tab_name
        
        for widget in self.tab_widgets:
            btn = widget.findChild(QPushButton)
            indicator = widget.findChild(QWidget, f"ind_{btn.text()}")
            
            if btn and btn.text() == tab_name:
                # Active tab styling
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4D4D4D;
                        color: white;
                        border: none;
                        outline: none;
                    }
                    QPushButton:focus {
                        outline: none;
                        border: none;
                    }
                    QPushButton:focus-visible {
                        outline: none;
                        border: none;
                    }
                """)
                # Show indicator
                if indicator:
                    indicator.setVisible(True)
            else:
                # Inactive tab styling
                if btn:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: white;
                            border: none;
                            outline: none;
                        }
                        QPushButton:focus {
                            outline: none;
                            border: none;
                        }
                        QPushButton:focus-visible {
                            outline: none;
                            border: none;
                        }
                    """)
                # Hide indicator
                if indicator:
                    indicator.setVisible(False)
                    
    def apply_styles(self):
        """Apply header styles."""
        self.setStyleSheet("""
            ModernHeader {
                background-color: #333333;
            }
            QPushButton {
                font-family: 'Segoe UI Light';
                font-size: 14px;
                outline: none;
                border: none;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
            QPushButton:focus-visible {
                outline: none;
                border: none;
            }
        """)

