"""
Modern Sidebar for MaxManager
Based on SVG design with 5 buttons and expandable width
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, Signal
from PySide6.QtGui import QFont, QPainter, QColor


class ModernSidebar(QWidget):
    """Modern sidebar with expandable width and 5 main buttons."""
    
    # Signals
    button_clicked = Signal(str)  # Emits button name when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Dimensions
        self.collapsed_width = 60   # Only text
        self.expanded_width = 200   # Text + description
        self.current_width = self.collapsed_width
        self.button_height = 40
        
        # Button data from SVG with placeholder icons
        self.buttons_data = {
            'ini': {'text': '.ini', 'description': 'INI Files', 'color': '#9C823A', 'icon': '📄'},
            'ui': {'text': 'ui', 'description': 'Interface', 'color': '#4D4D4D', 'icon': '🎨'},
            'script': {'text': 'script', 'description': 'Scripts', 'color': '#4D4D4D', 'icon': '📜'},
            'cuix': {'text': 'cuix', 'description': 'Panels', 'color': '#4D4D4D', 'icon': '🪟'},
            'projects': {'text': 'projects', 'description': 'Projects', 'color': '#4D4D4D', 'icon': '📁'},
        }
        
        self.active_button = 'ini'  # Default active
        self.buttons = {}
        self.animation = None
        self.parent_window = None  # Will be set by parent
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        """Initialize the sidebar UI."""
        self.setFixedWidth(self.current_width)
        self.setMinimumHeight(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create buttons
        for key, data in self.buttons_data.items():
            button = self.create_button(key, data)
            self.buttons[key] = button
            layout.addWidget(button)
        
        # Add spacer to push buttons to top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        # Set initial active button
        self.set_active_button(self.active_button)
        
    def create_button(self, key, data):
        """Create a sidebar button with icon and text."""
        button = QPushButton()
        button.setObjectName(f"sidebar_button_{key}")
        button.setFixedHeight(self.button_height)
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        
        # Button layout
        layout = QHBoxLayout(button)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)
        
        # Icon label
        icon_label = QLabel(data['icon'])
        icon_label.setObjectName(f"button_icon_{key}")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedWidth(20)  # Fixed width for icon
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(data['text'])
        text_label.setObjectName(f"button_text_{key}")
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_label.setVisible(False)  # Hidden when collapsed
        layout.addWidget(text_label)
        
        # Description label (hidden when collapsed)
        desc_label = QLabel(data['description'])
        desc_label.setObjectName(f"button_desc_{key}")
        desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc_label.setVisible(False)  # Hidden by default
        layout.addWidget(desc_label)
        
        # Connect click signal
        button.clicked.connect(lambda: self.on_button_clicked(key))
        
        return button
        
    def on_button_clicked(self, button_key):
        """Handle button click."""
        self.set_active_button(button_key)
        self.button_clicked.emit(button_key)
        
    def set_active_button(self, button_key):
        """Set active button and update styling."""
        # Update active button
        self.active_button = button_key
        
        # Update button states
        for key, button in self.buttons.items():
            is_active = (key == button_key)
            button.setChecked(is_active)
            
            # Update button styling
            if is_active:
                button.setStyleSheet(f"""
                    QPushButton#sidebar_button_{key} {{
                        background-color: {self.buttons_data[key]['color']};
                        color: white;
                        border: 2px solid {self.buttons_data[key]['color']};
                        font-weight: bold;
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton#sidebar_button_{key} {{
                        background-color: #4D4D4D;
                        color: white;
                        border: 1px solid #333333;
                        font-weight: normal;
                    }}
                    QPushButton#sidebar_button_{key}:hover {{
                        background-color: #5A5A5A;
                        border: 1px solid #666666;
                    }}
                """)
                
    def toggle_width(self):
        """Toggle between collapsed and expanded width."""
        if self.current_width == self.collapsed_width:
            self.expand()
        else:
            self.collapse()
            
    def expand(self):
        """Expand sidebar to show descriptions."""
        if self.animation:
            self.animation.stop()
            
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # 200ms animation
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        current_rect = self.geometry()
        target_rect = QRect(current_rect.x(), current_rect.y(), 
                           self.expanded_width, current_rect.height())
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(target_rect)
        
        # Show descriptions when animation starts
        self.animation.finished.connect(self.on_expand_finished)
        self.animation.start()
        
    def collapse(self):
        """Collapse sidebar to show only text."""
        if self.animation:
            self.animation.stop()
            
        # Hide descriptions immediately
        self.hide_descriptions()
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # 200ms animation
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        current_rect = self.geometry()
        target_rect = QRect(current_rect.x(), current_rect.y(), 
                           self.collapsed_width, current_rect.height())
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(target_rect)
        self.animation.start()
        
    def on_expand_finished(self):
        """Called when expand animation finishes."""
        self.show_descriptions()
        self.current_width = self.expanded_width
        
    def show_descriptions(self):
        """Show button descriptions."""
        for key, button in self.buttons.items():
            text_label = button.findChild(QLabel, f"button_text_{key}")
            desc_label = button.findChild(QLabel, f"button_desc_{key}")
            if text_label:
                text_label.setVisible(True)
            if desc_label:
                desc_label.setVisible(True)
                
    def hide_descriptions(self):
        """Hide button descriptions."""
        for key, button in self.buttons.items():
            text_label = button.findChild(QLabel, f"button_text_{key}")
            desc_label = button.findChild(QLabel, f"button_desc_{key}")
            if text_label:
                text_label.setVisible(False)
            if desc_label:
                desc_label.setVisible(False)
                
                
    def apply_styles(self):
        """Apply CSS styles based on SVG design."""
        self.setStyleSheet("""
            /* Main sidebar */
            ModernSidebar {
                background-color: #4D4D4D;
                border-right: 1px solid #333333;
            }
            
            /* Button text styling */
            QLabel {
                color: white;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            
            /* Icon styling */
            QLabel[objectName*="button_icon"] {
                font-size: 16px;
                color: white;
            }
            
            /* Button text styling */
            QLabel[objectName*="button_text"] {
                font-size: 12px;
                color: white;
                font-weight: bold;
            }
            
            /* Button description styling */
            QLabel[objectName*="button_desc"] {
                font-size: 10px;
                color: #CCCCCC;
            }
            
            /* Button hover effects */
            QPushButton:hover {
                background-color: #5A5A5A !important;
            }
            
            /* Button pressed effect */
            QPushButton:pressed {
                background-color: #3A3A3A !important;
            }
        """)
        
    def get_active_button(self):
        """Get currently active button."""
        return self.active_button
        
    def set_button_enabled(self, button_key, enabled):
        """Enable/disable a specific button."""
        if button_key in self.buttons:
            self.buttons[button_key].setEnabled(enabled)
            
    def get_button_count(self):
        """Get total number of buttons."""
        return len(self.buttons)
        
    def set_parent_window(self, window):
        """Set parent window for resize monitoring."""
        self.parent_window = window
        if window:
            # Store original resize event handler
            self.original_resize_event = window.resizeEvent
            
    def on_window_resize(self, event):
        """Handle window resize to adjust sidebar width."""
        if not self.parent_window:
            return
            
        # Get window width
        window_width = self.parent_window.width()
        
        # Determine if we should expand or collapse based on window width
        should_expand = window_width > 1000  # Expand if window is wide enough
        
        if should_expand and self.current_width == self.collapsed_width:
            self.expand()
        elif not should_expand and self.current_width == self.expanded_width:
            self.collapse()
            
        # Call original resize event
        if hasattr(self, 'original_resize_event') and self.original_resize_event:
            self.original_resize_event(event)
