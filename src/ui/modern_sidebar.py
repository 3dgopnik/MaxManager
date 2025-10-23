"""
Modern Sidebar for MaxManager
Based on SVG design with 5 buttons and expandable width
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, Signal, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QIcon
import os

# Import QtAwesome for beautiful icons
try:
    import qtawesome as qta
    QTAWESOME_AVAILABLE = True
    print("QtAwesome available - using professional icons")
except ImportError:
    QTAWESOME_AVAILABLE = False
    print("QtAwesome not available - using fallback emojis")


class ModernSidebar(QWidget):
    """Modern sidebar with expandable width and 5 main buttons."""
    
    # Signals
    button_clicked = Signal(str)  # Emits button name when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Dimensions
        self.collapsed_width = 80   # Only icons
        self.expanded_width = 160   # Icons + text + description
        self.current_width = self.collapsed_width
        self.button_height = 80     # Square buttons (80x80)
        self.button_width = 80      # Button width
        self.indicator_width = 10   # Indicator width
        self.is_animating = False
        
        # Timer for preventing rapid clicks
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._allow_clicks)
        self.clicks_allowed = True
        
        # Button data with FontAwesome icons (correct prefixes)
        self.buttons_data = {
            'ini': {
                'text': '.ini', 
                'color': '#9C823A',  # Golden
                'icon': 'fa5s.file-alt',  # FontAwesome 5 Solid
                'tabs': ['Security', 'Performance', 'Renderer', 'Viewport', 'Settings']
            },
            'ui': {
                'text': 'ui', 
                'color': '#4CAF50',  # Green
                'icon': 'fa5s.palette',  # FontAwesome 5 Solid
                'tabs': ['Interface', 'Colors', 'Layout', 'Themes', 'Fonts']
            },
            'script': {
                'text': 'script', 
                'color': '#2196F3',  # Blue
                'icon': 'fa5s.code',  # FontAwesome 5 Solid
                'tabs': ['Startup', 'Hotkeys', 'Macros', 'Libraries', 'Debug']
            },
            'cuix': {
                'text': 'cuix', 
                'color': '#FF9800',  # Orange
                'icon': 'fa5s.window-maximize',  # FontAwesome 5 Solid
                'tabs': ['Menus', 'Toolbars', 'Quads', 'Shortcuts', 'Panels']
            },
            'projects': {
                'text': 'projects', 
                'color': '#9C27B0',  # Purple
                'icon': 'fa5s.folder',  # FontAwesome 5 Solid
                'tabs': ['Templates', 'Paths', 'Structure', 'Presets', 'Export']
            },
        }
        
        self.active_button = 'ini'  # Default active button
        self.buttons = {}
        self.animation = None
        self.parent_window = None  # Will be set by parent
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        """Initialize the sidebar UI."""
        self.setFixedWidth(self.current_width)
        self.setMinimumHeight(560)  # Minimum height for current buttons
        self.setMaximumHeight(2000)  # Allow expansion for more buttons
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add logo button at the top (40x40)
        self.logo_button = self.create_logo_button()
        layout.addWidget(self.logo_button)
        
        # Add thin separator after logo
        separator_logo = QWidget()
        separator_logo.setFixedHeight(1)
        separator_logo.setStyleSheet("background-color: #222222;")
        layout.addWidget(separator_logo)
        
        # Create category buttons below logo
        for key, data in self.buttons_data.items():
            if key == 'logo':  # Skip logo if present (should not be)
                continue
            button = self.create_button(key, data)
            self.buttons[key] = button
            layout.addWidget(button)
            
            # Add thin separator between buttons
            separator = QWidget()
            separator.setFixedHeight(1)
            separator.setStyleSheet("background-color: #222222;")
            layout.addWidget(separator)
        
        # Add spacer to push buttons to top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        # Set initial active button
        self.set_active_button(self.active_button)
        
        # Apply styles
        self.apply_styles()
        
        # Ensure buttons start in collapsed state
        self.hide_descriptions()
        
    def create_button(self, key, data):
        """Create adaptive sidebar button - square by default, horizontal when expanded."""
        button = QPushButton()
        button.setObjectName(f"sidebar_button_{key}")
        button.setFixedHeight(self.button_height)  # Fixed height, width will expand with sidebar
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        
        # Button layout - absolute positioning for icon, text appears to the right
        layout = QHBoxLayout(button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Icon container - absolutely fixed 80px width to keep icon centered at 40px
        icon_container = QWidget()
        icon_container.setFixedSize(80, 80)
        icon_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        # Icon label (always visible) - use QtAwesome
        try:
            # Create QtAwesome icon
            icon = qta.icon(data['icon'], color='white')
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(24, 24))
            icon_label.setObjectName(f"button_icon_{key}")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(24, 24)  # Icon always same size
            icon_layout.addWidget(icon_label)
        except Exception as e:
            # Fallback to text if icon fails
            print(f"Failed to load icon {data['icon']}: {e}")
            icon_label = QLabel(data['icon'])
            icon_label.setObjectName(f"button_icon_{key}")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(24, 24)
            icon_label.setStyleSheet(f"color: {data['color']}; font-size: 20px;")
            icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_container)
        
        # Text label (hidden when collapsed)
        text_label = QLabel(data['text'])
        text_label.setObjectName(f"button_text_{key}")
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_label.setVisible(False)  # Hidden when collapsed
        text_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(text_label)
        
        # Connect click signal
        button.clicked.connect(lambda: self.on_button_clicked(key))
        
        # Add tooltip with tabs preview
        if 'tabs' in data:
            tabs_preview = ', '.join(data['tabs'][:3])  # First 3 tabs
            if len(data['tabs']) > 3:
                tabs_preview += '...'
            button.setToolTip(f"{data['text']} - {tabs_preview}")
        
        return button
        
    def create_logo_button(self):
        """Create adaptive logo button - 80x80 collapsed, 160x80 expanded."""
        logo_button = QPushButton()
        logo_button.setObjectName("logo_button")
        logo_button.setFixedHeight(80)  # Fixed height, width will expand with sidebar
        logo_button.setCursor(Qt.PointingHandCursor)
        
        # Button layout - absolute positioning for logo, text appears to the right
        layout = QHBoxLayout(logo_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo container - absolutely fixed 80px width to keep logo centered at 40px
        logo_container = QWidget()
        logo_container.setFixedSize(80, 80)
        logo_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Icon label with SVG fallback
        icon_label = QLabel()
        icon_label.setObjectName("logo_icon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(40, 40)  # Logo size
        
        try:
            # Try multiple paths for SVG
            import sys
            import os
            
            # Get the directory where the script is running from
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up from src/ui to project root
            
            svg_paths = [
                "icons/MaxManager.svg",
                "../icons/MaxManager.svg", 
                "../../icons/MaxManager.svg",
                os.path.join(project_root, "icons", "MaxManager.svg"),
                os.path.join(script_dir, "..", "..", "icons", "MaxManager.svg")
            ]
            
            icon_loaded = False
            for svg_path in svg_paths:
                try:
                    print(f"Trying to load logo from: {svg_path}")
                    if os.path.exists(svg_path):
                        print(f"OK File exists: {svg_path}")
                        icon = QIcon(svg_path)
                        print(f"Icon is null: {icon.isNull()}")
                        if not icon.isNull():
                            pixmap = icon.pixmap(40, 40)
                            print(f"Pixmap is null: {pixmap.isNull()}")
                            if not pixmap.isNull():
                                icon_label.setPixmap(pixmap)
                                icon_loaded = True
                                print(f"SUCCESS Logo loaded from: {svg_path}")
                                break
                    else:
                        print(f"FAIL File not found: {svg_path}")
                except Exception as e:
                    print(f"ERROR loading {svg_path}: {e}")
                    continue
            
            if not icon_loaded:
                raise Exception("SVG not found in any path")
                
        except Exception as e:
            # Fallback to text
            print(f"WARNING SVG logo failed to load: {e}")
            icon_label.setText("MM")
            icon_label.setStyleSheet("color: lime; font-size: 16px; font-weight: bold;")
        
        logo_layout.addWidget(icon_label)
        layout.addWidget(logo_container)
        
        # Text label (hidden when collapsed)
        text_label = QLabel("MaxManager")
        text_label.setObjectName("logo_text")
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_label.setVisible(False)  # Hidden when collapsed
        text_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        layout.addWidget(text_label)
        
        # Dark background styling
        logo_button.setStyleSheet(
            """
            QPushButton#logo_button {
                background-color: #1A1A1A; /* dark */
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
                outline: none;
            }
            QPushButton#logo_button:hover {
                background-color: #262626;
            }
            QPushButton#logo_button:pressed {
                background-color: #0D0D0D;
            }
            QPushButton#logo_button:focus {
                outline: none;
                border: none;
            }
            QPushButton#logo_button:focus-visible {
                outline: none;
                border: none;
            }
            """
        )
        
        # Connect toggle functionality
        logo_button.clicked.connect(self.toggle_width)
        
        # Tooltip
        logo_button.setToolTip("Expand/Collapse sidebar")
        
        return logo_button
        
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
            
            # Update button styling - only left indicator, not full button
            if is_active:
                color = self.buttons_data[key]['color']
                button.setStyleSheet(f"""
                    QPushButton#sidebar_button_{key} {{
                        background-color: #333333;
                        color: white;
                        border: none;
                        border-left: 10px solid {color};
                        font-weight: bold;
                        outline: none;
                    }}
                    QPushButton#sidebar_button_{key}:focus {{
                        outline: none;
                        border: none;
                        border-left: 10px solid {color};
                    }}
                    QPushButton#sidebar_button_{key}:focus-visible {{
                        outline: none;
                        border: none;
                        border-left: 10px solid {color};
                    }}
                    QPushButton#sidebar_button_{key} QLabel {{
                        color: white;
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton#sidebar_button_{key} {{
                        background-color: #333333;
                        color: white;
                        border: none;
                        border-left: 0px;
                        font-weight: normal;
                        outline: none;
                    }}
                    QPushButton#sidebar_button_{key}:focus {{
                        outline: none;
                        border: none;
                        border-left: 0px;
                    }}
                    QPushButton#sidebar_button_{key}:focus-visible {{
                        outline: none;
                        border: none;
                        border-left: 0px;
                    }}
                    QPushButton#sidebar_button_{key} QLabel {{
                        color: white;
                    }}
                """)
                
    def _allow_clicks(self):
        """Allow clicks again after timer expires."""
        self.clicks_allowed = True
        
    def toggle_width(self):
        """Toggle between collapsed and expanded width."""
        # Prevent rapid clicks
        if not self.clicks_allowed:
            return
            
        # Protect against double-clicks during animation
        if self.is_animating or (self.animation and self.animation.state() == QPropertyAnimation.Running):
            return
        
        # Block clicks for 300ms
        self.clicks_allowed = False
        self.click_timer.start(300)
        
        # Use stored state for more reliable detection
        if self.current_width == self.collapsed_width:
            self.expand()
        else:
            self.collapse()
            
    def expand(self):
        """Expand sidebar to show descriptions."""
        if self.animation:
            self.animation.stop()
        
        self.is_animating = True
        
        # Update state immediately to prevent double-clicks
        self.current_width = self.expanded_width
        
        # Show text labels immediately
        self.show_descriptions()
        
        # Set fixed width immediately to prevent layout changes
        self.setFixedWidth(self.expanded_width)
        self.is_animating = False
        
    def collapse(self):
        """Collapse sidebar to show only icons."""
        if self.animation:
            self.animation.stop()
        
        self.is_animating = True
        
        # Update state immediately to prevent double-clicks
        self.current_width = self.collapsed_width
        
        # Hide text labels immediately
        self.hide_descriptions()
        
        # Set fixed width immediately to prevent layout changes
        self.setFixedWidth(self.collapsed_width)
        self.is_animating = False
        
    def show_descriptions(self):
        """Show button descriptions and logo text."""
        # Show logo text
        logo_text = self.logo_button.findChild(QLabel, "logo_text")
        if logo_text:
            logo_text.setVisible(True)
        
        # Show button text - icon stays in center, text appears to the right
        for key, button in self.buttons.items():
            text_label = button.findChild(QLabel, f"button_text_{key}")
            if text_label:
                text_label.setVisible(True)
                
    def hide_descriptions(self):
        """Hide button descriptions and logo text."""
        # Hide logo text
        logo_text = self.logo_button.findChild(QLabel, "logo_text")
        if logo_text:
            logo_text.setVisible(False)
        
        # Hide button text
        for key, button in self.buttons.items():
            text_label = button.findChild(QLabel, f"button_text_{key}")
            if text_label:
                text_label.setVisible(False)
                
                
    def apply_styles(self):
        """Apply CSS styles based on SVG design."""
        self.setStyleSheet("""
            /* Main sidebar */
            ModernSidebar {
                background-color: #333333;
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
            
            /* Remove focus outline from all buttons */
            QPushButton {
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
            
            /* Base button styling - removed to avoid conflicts */
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
