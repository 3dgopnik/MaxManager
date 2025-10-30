"""
Modern Header for MaxManager
Contextual header with dynamic tabs
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics


class ModernHeader(QWidget):
    """Contextual header with dynamic tabs."""
    
    # Signal: (context_key, tab_name)
    tab_changed = Signal(str, str)
    
    def __init__(self, translation_manager=None, parent=None):
        super().__init__(parent)
        self.translation_manager = translation_manager
        self.setFixedHeight(80)
        # Width set dynamically in set_context() based on tab count
        
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
        print(f"[ModernHeader] init_ui: height={self.height()}")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # NO margins
        self.layout.setSpacing(0)  # No spacing between tabs
        self.setContentsMargins(0, 40, 0, 0)  # 40px top margin on widget itself
        print(f"[ModernHeader] Layout margins: {self.layout.contentsMargins()}")
        print(f"[ModernHeader] Widget margins: {self.contentsMargins()}")
        
        self.apply_styles()
        
    def set_context(self, context_key, tabs_list):
        """Switch header context (called when sidebar button clicked)."""
        print(f"[ModernHeader] set_context: {context_key}, tabs={tabs_list}")
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
        
        # Adjust width dynamically based on tab count
        required_width = len(tabs_list) * 160
        self.setMinimumWidth(required_width)
        
        # Create new tabs
        for idx, tab_name in enumerate(tabs_list):
            color = self.tab_colors.get(idx, '#9C823A')
            tab_widget = self.create_tab(tab_name, color)
            self.tab_widgets.append(tab_widget)
            self.layout.addWidget(tab_widget)  # Add directly without spacing
            
            # Separators removed - transparent tabs with hover effect provide visual feedback
        
        # Add stretch at the end to push tabs to the left
        self.layout.addStretch()
        
        # Set first tab as active
        if tabs_list:
            self.set_active_tab(tabs_list[0])
            
    def create_tab(self, name, indicator_color):
        """Create tab button with indicator."""
        container = QWidget()
        # Use UNIFORM width for all tabs for visual consistency
        TAB_WIDTH = 200
        TAB_HEIGHT = 40
        container.setFixedSize(TAB_WIDTH, TAB_HEIGHT)
        print(f"[ModernHeader] Created tab '{name}': size={TAB_WIDTH}x{TAB_HEIGHT}")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab button with translation
        # Try to translate tab name
        translated_name = name
        if self.translation_manager:
            tab_key = f"tab_{name.lower()}"
            translated_name = self.translation_manager.get(tab_key, name)
        # Elide long labels to keep uniform width, add tooltip with full text
        btn = QPushButton()
        metrics = QFontMetrics(btn.font())
        elided = metrics.elidedText(translated_name, Qt.ElideRight, TAB_WIDTH - 24)
        btn.setText(elided)
        if elided != translated_name:
            btn.setToolTip(translated_name)
        btn.setObjectName(f"tab_{name}")
        btn.setFixedSize(TAB_WIDTH, TAB_HEIGHT)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.on_tab_clicked(name))
        
        # No tooltip - name is already visible
        
        layout.addWidget(btn)
        
        # Color indicator positioned absolutely at bottom
        indicator = QWidget(container)
        indicator.setObjectName(f"ind_{name}")
        indicator.setFixedSize(TAB_WIDTH, 5)
        indicator.setStyleSheet(f"background-color: {indicator_color};")
        indicator.setVisible(False)  # Hidden by default
        indicator.move(0, TAB_HEIGHT - 5)  # Position at bottom
        
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
                        background-color: transparent;
                        color: white;
                        border: none;
                        outline: none;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 30);
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
                        QPushButton:hover {
                            background-color: rgba(255, 255, 255, 20);
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
                background-color: transparent;
            }
            QToolTip {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444444;
                padding: 5px 10px;
                font-family: 'Segoe UI';
                font-size: 10px;
            }
            QPushButton {
                font-family: 'Segoe UI';
                font-size: 18px;
                outline: none;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border-top-left-radius: 7.5px;
                border-top-right-radius: 7.5px;
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

