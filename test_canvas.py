"""
Test script for CollapsibleCanvas widget.

Tests the accordion-style collapsible panels with mock INI data.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QColor

# Import our UI components
from src.ui.collapsible_canvas import CollapsibleCanvas, CanvasContainer
from src.ui.modern_sidebar import ModernSidebar
from src.ui.modern_header import ModernHeader
from src.ui.ini_parameter_widget import INIParameterWidget


class DotGridWidget(QWidget):
    """Widget with dot grid background pattern."""
    
    def paintEvent(self, event):
        """Draw dot grid pattern on background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        # Background color
        painter.fillRect(self.rect(), QColor("#1A1A1A"))
        
        # Dot grid pattern: 2x2 pixel squares every 40 pixels
        dot_size = 2
        dot_spacing = 40
        dot_color = QColor("#2A2A2A")  # Slightly lighter than background
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(dot_color)
        
        # Draw dots in a grid
        width = self.width()
        height = self.height()
        
        for x in range(0, width, dot_spacing):
            for y in range(0, height, dot_spacing):
                painter.drawRect(x, y, dot_size, dot_size)
        
        painter.end()
        super().paintEvent(event)


class TestCanvasWindow(QMainWindow):
    """Test window for canvas widgets."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaxManager - Canvas Test")
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI."""
        # Central widget with dot grid background
        central = DotGridWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = ModernSidebar()
        self.sidebar.button_clicked.connect(self.on_sidebar_clicked)
        main_layout.addWidget(self.sidebar)
        
        # Right side: Header + Canvas + Footer
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Header
        self.header = ModernHeader()
        self.header.tab_changed.connect(self.on_header_tab_changed)
        right_layout.addWidget(self.header)
        
        # Canvas container
        self.canvas_container = CanvasContainer()
        right_layout.addWidget(self.canvas_container)
        
        # Footer with action buttons
        footer = self.create_footer()
        right_layout.addWidget(footer)
        
        main_layout.addLayout(right_layout)
        
        # Set stretch factors
        main_layout.setStretch(0, 0)  # Sidebar fixed
        main_layout.setStretch(1, 1)  # Right side stretches
        
        # Initialize with INI category
        self.sidebar.set_active_button('ini')
        self.on_sidebar_clicked('ini')
        
    def create_footer(self) -> QWidget:
        """Create footer with action buttons."""
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(40)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create buttons
        refresh_btn = self.create_footer_button("Refresh")
        revert_btn = self.create_footer_button("Revert")
        apply_btn = self.create_footer_button("Apply")
        
        layout.addWidget(refresh_btn)
        layout.addStretch()
        layout.addWidget(revert_btn)
        layout.addWidget(apply_btn)
        
        # Apply styles
        footer.setStyleSheet("""
            QWidget#footer {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-family: 'Segoe UI';
                font-size: 18px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QPushButton:pressed {
                background-color: transparent;
            }
        """)
        
        return footer
        
    def create_footer_button(self, text: str) -> QPushButton:
        """Create a footer button."""
        btn = QPushButton(text)
        btn.setFixedSize(160, 40)
        btn.setCursor(Qt.PointingHandCursor)
        return btn
        
    def on_sidebar_clicked(self, button_name: str):
        """Handle sidebar button click."""
        print(f"Sidebar clicked: {button_name}")
        
        # Update header context
        tabs_map = {
            'ini': ['Security', 'Performance', 'Renderer', 'Viewport', 'Settings'],
            'ui': ['Interface', 'Colors', 'Layout', 'Themes', 'Fonts'],
            'script': ['Startup', 'Hotkeys', 'Macros', 'Libraries', 'Debug'],
            'cuix': ['Menus', 'Toolbars', 'Quads', 'Shortcuts', 'Panels'],
            'projects': ['Templates', 'Paths', 'Structure', 'Presets', 'Export']
        }
        
        tabs = tabs_map.get(button_name, [])
        self.header.set_context(button_name, tabs)
        
        # Load canvas panels for this category
        self.load_canvas_panels(button_name, tabs[0] if tabs else '')
        
    def on_header_tab_changed(self, category: str, tab_name: str):
        """Handle header tab change."""
        print(f"Header tab: {category} / {tab_name}")
        self.load_canvas_panels(category, tab_name)
        
    def load_canvas_panels(self, category: str, tab_name: str):
        """Load canvas panels with mock INI data."""
        print(f"Loading canvas panels: {category} / {tab_name}")
        
        # Clear existing panels
        self.canvas_container.clear_canvases()
        
        # Create mock canvas panels based on category/tab
        mock_data = self.get_mock_data(category, tab_name)
        
        for section_title, parameters in mock_data.items():
            canvas = CollapsibleCanvas(section_title, expanded=True)
            canvas.reset_requested.connect(lambda c=canvas, title=section_title: self.revert_canvas_section(c, title))
            canvas.save_requested.connect(lambda c=canvas, title=section_title: self.save_canvas_section(c, title))
            
            # Add mock parameters
            for param_name, param_value in parameters.items():
                param_widget = self.create_parameter_widget(param_name, param_value)
                # Track modifications
                param_widget.modified_state_changed.connect(lambda modified, c=canvas: self.on_param_modified(c, modified))
                canvas.add_content(param_widget)
                
            self.canvas_container.add_canvas(canvas)
            
    def get_mock_data(self, category: str, tab_name: str) -> dict:
        """Get mock INI data for testing with real types."""
        if category == 'ini' and tab_name == 'Security':
            return {
                'Script Execution': {
                    'SafeSceneScriptExecutionEnabled': '1',  # boolean
                    'MaxScriptDebuggerEnabled': '0',          # boolean
                    'AllowUnsafeEval': '0'                   # boolean
                },
                'File Access': {
                    'RestrictFileAccess': '1',                            # boolean
                    'AllowedPaths': 'C:\\Projects;D:\\Assets',           # path
                    'BlockNetworkAccess': '0'                            # boolean
                },
                'Plugin Security': {
                    'VerifyPluginSignatures': '1',           # boolean
                    'AllowUnsignedPlugins': '0',             # boolean
                    'TrustedPublishers': 'Autodesk;Chaos'    # string
                }
            }
        elif category == 'ini' and tab_name == 'Performance':
            return {
                'Rendering': {
                    'ThreadCount': '8',                      # integer
                    'UseGPU': '1',                           # boolean
                    'MaxSampleRate': '4096'                  # integer
                },
                'Memory': {
                    'MaxHeapSize': '8192',                   # integer
                    'EnableMemoryCompression': '1',          # boolean
                    'CacheSize': '2048'                      # integer
                },
                'Quality': {
                    'ZoomExtScaleParallel': '0.850000',      # float
                    'HighlightOpacity': '0.150000',          # float
                    'OutlineThickness': '1.000000'           # float
                }
            }
        else:
            return {
                f'{tab_name} Settings': {
                    'BooleanParam': '1',
                    'IntegerParam': '42',
                    'StringParam': 'Test Value'
                }
            }
            
    def create_parameter_widget(self, name: str, value: str) -> QWidget:
        """Create smart INI parameter widget with auto-type detection."""
        param_widget = INIParameterWidget(name, value, param_type='auto')
        param_widget.value_changed.connect(self.on_parameter_changed)
        return param_widget
        
    def on_parameter_changed(self, param_name: str, new_value: str):
        """Handle parameter value change."""
        print(f"Parameter changed: {param_name} = {new_value}")
        
    def on_param_modified(self, canvas, modified: bool):
        """Handle parameter modification state change."""
        if modified:
            canvas.mark_as_modified()
            print(f"Canvas '{canvas.title}' has unsaved changes")
        else:
            # Check if any other params in canvas are still modified
            # For now, just mark as saved
            canvas.mark_as_saved()
            print(f"Canvas '{canvas.title}' all changes saved")
        
    def save_canvas_section(self, canvas, section_title: str):
        """Save all parameters in a canvas section."""
        print(f"Save requested for section: {section_title}")
        canvas.mark_as_saved()
        
    def revert_canvas_section(self, canvas, section_title: str):
        """Reset all parameters in a canvas section to default values."""
        print(f"Reset to default requested for section: {section_title}")
        canvas.reset_all_parameters()
        canvas.mark_as_saved()


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle("Fusion")
    
    window = TestCanvasWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

