"""
Test script for CollapsibleCanvas widget.

Tests the accordion-style collapsible panels with mock INI data.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QSizeGrip, QLineEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPainter, QColor, QPen

try:
    import qtawesome as qta
    QTA_AVAILABLE = True
except ImportError:
    QTA_AVAILABLE = False

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import our UI components
from src.ui.collapsible_canvas import CollapsibleCanvas, CanvasContainer
from src.ui.modern_sidebar import ModernSidebar
from src.ui.modern_header import ModernHeader
from src.ui.ini_parameter_widget import INIParameterWidget

# Import INI manager
from src.modules.ini_manager import INIManager

# Import i18n
from src.i18n import Language, get_translation_manager, t

# Import parameter filter
from src.utils.parameter_filter import filter_parameters

# Import version
from src.__version__ import __version__

# Import database and tab mapper
from src.data.database_loader import get_database
from src.data.tab_mapper import get_tab_for_section, get_dynamic_tabs


class CustomSizeGrip(QSizeGrip):
    """Custom QSizeGrip with visible icon."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load icon
        try:
            self.icon = qta.icon('mdi.resize-bottom-right', color='#666666')
        except:
            self.icon = None
    
    def paintEvent(self, event):
        """Draw icon on top of grip."""
        super().paintEvent(event)
        
        if self.icon:
            painter = QPainter(self)
            pixmap = self.icon.pixmap(QSize(20, 20))
            # Center icon in grip
            x = (self.width() - 20) // 2
            y = (self.height() - 20) // 2
            painter.drawPixmap(x, y, pixmap)
            painter.end()


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


class CanvasMainWindow(QMainWindow):
    """Main window for MaxManager canvas-based UI."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaxManager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set minimum window size: 5 tabs × 160px + sidebar 80px + margins
        self.setMinimumWidth(880)  # 800 (tabs) + 80 (sidebar)
        self.setMinimumHeight(400)
        
        # Get translation manager
        self.translation_manager = get_translation_manager()
        self.translation_manager.register_callback(self.on_language_changed)
        
        # Initialize INI manager - use real 3dsMax.ini
        real_ini_path = Path(r"C:\Users\acherednikov\AppData\Local\Autodesk\3dsMax\2025 - 64bit\ENU\3dsMax.ini")
        test_ini_path = Path("test_simple.ini")
        
        # Try real file first, fallback to test file
        ini_path = real_ini_path if real_ini_path.exists() else test_ini_path
        
        self.ini_manager = None
        if ini_path.exists():
            self.ini_manager = INIManager(ini_path)
            if self.ini_manager.load_ini():
                print(f"OK INI loaded from: {ini_path}")
                print(f"   Sections: {len(self.ini_manager.original_sections)}")
                print(f"   Parameters: {len(self.ini_manager.original_parameters)}")
            else:
                print(f"FAIL Failed to load INI from {ini_path}, using mock data")
                self.ini_manager = None
        else:
            print("WARN No INI file found, using mock data")
        
        # Track current state
        self.current_category = None
        self.current_tab = None
        
        # Load parameter database
        self.db = get_database()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI."""
        print(f"[CanvasMainWindow] init_ui: starting, window size={self.width()}x{self.height()}")
        
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
        
        # Header with version and language controls
        header_container = QWidget()
        header_container.setFixedHeight(80)  # Same as ModernHeader
        header_container.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        # Header tabs (NO STRETCH - fixed width)
        self.header = ModernHeader()
        self.header.tab_changed.connect(self.on_header_tab_changed)
        header_layout.addWidget(self.header, 0)  # Stretch factor 0 - NO EXPANSION
        
        # Spacer to push controls to the right
        header_layout.addStretch()
        
        # Top-right controls (version + language + search icon)
        top_controls = self.create_top_controls()
        header_layout.addWidget(top_controls, 0, Qt.AlignTop | Qt.AlignRight)
        
        right_layout.addWidget(header_container)
        
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
        
    
    def toggle_floating_search(self):
        """Toggle floating search bar visibility."""
        # Create floating search widget if not exists
        if not hasattr(self, 'floating_search'):
            self.create_floating_search()
        
        # Toggle visibility
        if self.floating_search.isVisible():
            self.hide_floating_search()
        else:
            self.show_floating_search()
    
    def show_floating_search(self):
        """Show floating search bar in center of window."""
        # Create floating search widget if not exists
        if not hasattr(self, 'floating_search'):
            self.create_floating_search()
        
        # Show and focus
        self.floating_search.setVisible(True)
        self.floating_search.raise_()
        self.search_field.setFocus()
        self.search_field.clear()
        
        # Position in center
        self.position_floating_search()
    
    def create_floating_search(self):
        """Create floating search bar widget."""
        # Container
        self.floating_search = QWidget(self.centralWidget())
        self.floating_search.setFixedSize(400, 40)
        
        layout = QHBoxLayout(self.floating_search)
        layout.setContentsMargins(10, 0, 0, 0)  # Left padding for text
        layout.setSpacing(0)
        
        # Search field (no icon - already in header)
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search...")
        self.search_field.textChanged.connect(self.on_floating_search_changed)
        layout.addWidget(self.search_field, 1)
        
        # Close button
        close_btn = QPushButton()
        close_btn.setFixedSize(40, 40)
        close_btn.setCursor(Qt.PointingHandCursor)
        if QTA_AVAILABLE:
            try:
                close_btn.setIcon(qta.icon('fa5s.times', color='#888888'))
                close_btn.setIconSize(QSize(16, 16))
            except:
                close_btn.setText("✕")
        else:
            close_btn.setText("✕")
        
        close_btn.clicked.connect(self.hide_floating_search)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888888;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        layout.addWidget(close_btn)
        
        # Style floating search
        self.floating_search.setStyleSheet("""
            QWidget {
                background-color: rgba(42, 42, 42, 230);
                border: 1px solid #555555;
                border-radius: 7.5px;
            }
            QLineEdit {
                background-color: transparent;
                color: white;
                border: none;
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 0px 5px;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        
        # Initially hidden
        self.floating_search.setVisible(False)
    
    def position_floating_search(self):
        """Position floating search in center of window."""
        if hasattr(self, 'floating_search'):
            x = (self.width() - 400) // 2
            y = (self.height() - 40) // 2
            self.floating_search.move(x, y)
    
    def hide_floating_search(self):
        """Hide floating search and restore view."""
        if hasattr(self, 'floating_search'):
            self.floating_search.setVisible(False)
            self.search_field.clear()
            # Restore original view
            if self.current_category and self.current_tab:
                self.load_canvas_panels(self.current_category, self.current_tab)
    
    def on_floating_search_changed(self, text: str):
        """Handle floating search text change."""
        search_text = text.lower().strip()
        
        if not search_text:
            # Restore original view
            if self.current_category and self.current_tab:
                self.load_canvas_panels(self.current_category, self.current_tab)
            return
        
        # Perform global search and update main canvas
        self.perform_global_search(search_text)
    
    def perform_global_search(self, search_text: str):
        """Search across ALL INI sections and update main canvas."""
        if not self.ini_manager:
            return
        
        # Clear current canvas
        self.canvas_container.setUpdatesEnabled(False)
        self.canvas_container.clear_canvases()
        QApplication.processEvents()
        
        search_lower = search_text.lower()
        found_sections = {}
        
        # Search through ALL sections
        for section_name, section in self.ini_manager.current_sections.items():
            filtered_params = {}
            for param_name, param_value in section.parameters.items():
                # Search in parameter name
                if search_lower in param_name.lower():
                    filtered_params[param_name] = param_value
                    continue
                
                # Search in display name
                from src.modules.parameter_info_loader import ParameterInfoLoader
                param_info = ParameterInfoLoader()
                display_name = param_info.get_display_name(param_name, 'en')
                if display_name and search_lower in display_name.lower():
                    filtered_params[param_name] = param_value
            
            if filtered_params:
                found_sections[section_name] = filtered_params
        
        # Display results in main canvas
        if found_sections:
            print(f"Found {len(found_sections)} sections with matches")
            for section_name, parameters in found_sections.items():
                canvas = CollapsibleCanvas(section_name, expanded=True)
                canvas.reset_requested.connect(lambda c=canvas, title=section_name: self.revert_canvas_section(c, title))
                canvas.save_requested.connect(lambda c=canvas, title=section_name: self.save_canvas_section(c, title))
                
                # Add parameters
                for param_name, param_value in parameters.items():
                    param_widget = self.create_parameter_widget(param_name, param_value)
                    param_widget.modified_state_changed.connect(lambda modified, c=canvas: self.on_param_modified(c, modified))
                    canvas.add_content(param_widget)
                
                self.canvas_container.add_canvas(canvas)
        
        self.canvas_container.setUpdatesEnabled(True)
        self.canvas_container.update()
    
    def showEvent(self, event):
        """Handle window show - initial positioning."""
        super().showEvent(event)
        # Position size grip in bottom-right corner on first show
        self.position_size_grip()
    
    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        
        print(f"[ResizeEvent] Window size: {self.width()}x{self.height()}")
        
        # Debug header size
        if hasattr(self, 'header'):
            print(f"[ResizeEvent] Header size: {self.header.width()}x{self.header.height()}")
            print(f"[ResizeEvent] Header margins: {self.header.contentsMargins()}")
        
        # Reposition floating search if visible
        if hasattr(self, 'floating_search') and self.floating_search.isVisible():
            self.position_floating_search()
        
        # Reposition size grip in bottom-right corner
        self.position_size_grip()
    
    def position_size_grip(self):
        """Position size grip in bottom-right corner."""
        if hasattr(self, 'size_grip') and hasattr(self, 'footer_widget'):
            self.size_grip.move(self.footer_widget.width() - 24, self.footer_widget.height() - 24)
    
    
    def create_top_controls(self) -> QWidget:
        """Create top-right controls (search + version + language switcher)."""
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 0)  # Reduced top from 20 to 10, standard right margin
        layout.setSpacing(10)
        
        # FREE/ADVANCED mode toggle
        self.mode_toggle_btn = QPushButton("FREE")
        self.mode_toggle_btn.setFixedSize(100, 25)
        self.mode_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.mode_toggle_btn.setCheckable(True)
        self.mode_toggle_btn.clicked.connect(self.toggle_mode)
        self.mode_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #569cd6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:checked {
                background-color: #4ec9b0;
            }
        """)
        layout.addWidget(self.mode_toggle_btn)
        self.is_advanced_mode = False
        
        # Search button (icon only, no hover)
        search_btn = QPushButton()
        search_btn.setObjectName("search_icon")
        search_btn.setFixedSize(20, 20)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setToolTip("Search parameters")
        
        # Add search icon (16x16)
        if QTA_AVAILABLE:
            try:
                search_btn.setIcon(qta.icon('fa5s.search', color='white'))
                search_btn.setIconSize(QSize(16, 16))
            except:
                search_btn.setText("🔍")
        else:
            search_btn.setText("🔍")
        
        # Connect to toggle floating search
        search_btn.clicked.connect(self.toggle_floating_search)
        
        # Style - no hover
        search_btn.setStyleSheet("""
            QPushButton#search_icon {
                background-color: transparent;
                border: none;
            }
            QPushButton#search_icon:hover {
                background-color: transparent;
            }
        """)
        layout.addWidget(search_btn)
        
        # Version label (from centralized __version__)
        self.version_label = QLabel(f"v.{__version__}")
        self.version_label.setFont(QFont("Segoe UI", 9))
        self.version_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 5px 10px;
            }
        """)
        layout.addWidget(self.version_label)
        
        # Language switcher button (toggle) - show current active language
        current_lang = self.translation_manager.current_language
        lang_text = "RU" if current_lang == Language.RUSSIAN else "EN"
        self.lang_toggle_btn = QPushButton(lang_text)
        self.lang_toggle_btn.setFixedSize(40, 25)
        self.lang_toggle_btn.setFont(QFont("Segoe UI", 9))
        self.lang_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.lang_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: transparent;
            }
        """)
        
        # Connect toggle button
        self.lang_toggle_btn.clicked.connect(self.toggle_language)
        
        layout.addWidget(self.lang_toggle_btn)
        
        return container
    
    def toggle_mode(self):
        """Toggle between FREE and ADVANCED mode."""
        self.is_advanced_mode = not self.is_advanced_mode
        self.mode_toggle_btn.setText("ADVANCED" if self.is_advanced_mode else "FREE")
        
        # Reload current view with new mode
        print(f"[Mode] Switched to: {'ADVANCED' if self.is_advanced_mode else 'FREE'}")
        self.reload_current_view()
    
    def toggle_language(self):
        """Toggle between RU and EN."""
        current_lang = self.translation_manager.current_language
        
        # Toggle language
        if current_lang == Language.ENGLISH:
            new_lang = Language.RUSSIAN
        else:
            new_lang = Language.ENGLISH
        
        # Set language first
        self.translation_manager.set_language(new_lang)
        
        # Update button text to show CURRENT active language
        if new_lang == Language.RUSSIAN:
            self.lang_toggle_btn.setText("RU")
        else:
            self.lang_toggle_btn.setText("EN")
        
        # Reload view with new language
        self.reload_current_view()
    
    def reload_current_view(self):
        """Reload current canvas view (for language change)."""
        current_category = self.sidebar.active_button if hasattr(self.sidebar, 'active_button') else 'ini'
        current_tab = self.header.active_tab if hasattr(self.header, 'active_tab') else 'Security'
        
        # Just reload - processEvents is now inside load_canvas_panels
        self.load_canvas_panels(current_category, current_tab)
    
    def on_language_changed(self):
        """Handle language change callback (not used - reload triggered directly)."""
        pass
    
    def create_footer(self) -> QWidget:
        """Create footer with action buttons and resize grip."""
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(40)
        
        # Store footer reference for resize grip repositioning
        self.footer = footer
        
        layout = QHBoxLayout(footer)
        # Align with canvas content: left=10 (canvas start), right=20 (canvas end + scrollbar)
        layout.setContentsMargins(10, 0, 20, 0)
        layout.setSpacing(0)
        
        # Create buttons
        refresh_btn = self.create_footer_button("Refresh")
        revert_btn = self.create_footer_button("Revert")
        apply_btn = self.create_footer_button("Apply")
        
        # Connect buttons
        refresh_btn.clicked.connect(self.on_refresh_clicked)
        revert_btn.clicked.connect(self.on_revert_clicked)
        apply_btn.clicked.connect(self.on_apply_clicked)
        
        layout.addWidget(refresh_btn)
        layout.addStretch()
        layout.addWidget(revert_btn)
        layout.addWidget(apply_btn)
        
        # Store footer for later size grip positioning
        self.footer_widget = footer
        
        # Add custom QSizeGrip in bottom-right corner (created after footer added to layout)
        self.size_grip = CustomSizeGrip(footer)
        self.size_grip.setFixedSize(24, 24)
        # Will be positioned in showEvent when window size is known
        
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
                border-top-left-radius: 7.5px;
                border-top-right-radius: 7.5px;
            }
            QPushButton:pressed {
                background-color: transparent;
            }
            QSizeGrip {
                background-color: transparent;
                border: none;
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
        
        # Dynamic tabs for 'ini' category
        if button_name == 'ini':
            tabs = self.get_dynamic_ini_tabs()
        else:
            # Static tabs for other categories
            tabs_map = {
                'ui': ['Interface', 'Colors', 'Layout', 'Themes', 'Fonts'],
                'script': ['Startup', 'Hotkeys', 'Macros', 'Libraries', 'Debug'],
                'cuix': ['Menus', 'Toolbars', 'Quads', 'Shortcuts', 'Panels'],
                'projects': ['Templates', 'Paths', 'Structure', 'Presets', 'Export']
            }
            tabs = tabs_map.get(button_name, [])
        
        self.header.set_context(button_name, tabs)
        
        # Update window minimum width based on tab count
        SIDEBAR_WIDTH = 80
        TAB_WIDTH = 160
        MARGIN = 20
        min_width = SIDEBAR_WIDTH + (len(tabs) * TAB_WIDTH) + MARGIN
        self.setMinimumWidth(min_width)
        
        # Load canvas panels for this category
        self.load_canvas_panels(button_name, tabs[0] if tabs else '')
    
    def get_dynamic_ini_tabs(self) -> list[str]:
        """Get dynamic tabs based on real INI sections."""
        if not self.ini_manager:
            # Fallback if no INI loaded
            return ['Security', 'Performance', 'Renderer', 'Viewport', 'Settings']
        
        # Get all sections from real INI
        sections_by_ini = {'3dsmax.ini': list(self.ini_manager.current_sections.keys())}
        
        # Check for plugin ini files (TODO: implement plugin ini detection)
        # For now, plugins will be detected from database
        
        # Get dynamic tabs
        tabs = get_dynamic_tabs(sections_by_ini)
        
        print(f"[Dynamic Tabs] Generated: {tabs}")
        return tabs
        
    def on_header_tab_changed(self, category: str, tab_name: str):
        """Handle header tab change."""
        print(f"Header tab: {category} / {tab_name}")
        self.load_canvas_panels(category, tab_name)
        
    def load_canvas_panels(self, category: str, tab_name: str):
        """Load canvas panels with mock INI data."""
        print(f"Loading canvas panels: {category} / {tab_name}")
        
        # Store current state
        self.current_category = category
        self.current_tab = tab_name
        
        # Disable updates to prevent flickering during rebuild
        self.canvas_container.setUpdatesEnabled(False)
        
        # Clear existing panels
        self.canvas_container.clear_canvases()
        QApplication.processEvents()  # Wait for deleteLater to complete
        
        # Create mock canvas panels based on category/tab
        mock_data = self.get_mock_data(category, tab_name)
        
        for section_title, parameters in mock_data.items():
            # Skip empty sections (all parameters filtered out)
            if not parameters:
                print(f"Skipping empty section: {section_title}")
                continue
            
            canvas = CollapsibleCanvas(section_title, expanded=True)
            canvas.reset_requested.connect(lambda c=canvas, title=section_title: self.revert_canvas_section(c, title))
            canvas.save_requested.connect(lambda c=canvas, title=section_title: self.save_canvas_section(c, title))
            
            # Add parameters
            for param_name, param_value in parameters.items():
                # Check if this is an available parameter from database
                is_available = isinstance(param_value, dict) and param_value.get('available', False)
                param_data = param_value.get('data') if is_available else None
                actual_value = param_value.get('value', param_value) if is_available else param_value
                
                param_widget = self.create_parameter_widget(
                    param_name, 
                    actual_value,
                    is_available=is_available,
                    param_data=param_data,
                    can_add=self.is_advanced_mode
                )
                # Track modifications
                param_widget.modified_state_changed.connect(lambda modified, c=canvas: self.on_param_modified(c, modified))
                canvas.add_content(param_widget)
                
            self.canvas_container.add_canvas(canvas)
        
        # Re-enable updates and force single repaint (prevents flickering)
        self.canvas_container.setUpdatesEnabled(True)
        self.canvas_container.update()  # Single repaint
        
        # DEBUG: Print canvas_widget and scroll area info
        QApplication.processEvents()
        print(f"[DEBUG MainWindow] After loading panels:")
        print(f"  canvas_widget size: {self.canvas_container.canvas_widget.size()}")
        print(f"  scroll_area viewport size: {self.canvas_container.scroll_area.viewport().size()}")
        print(f"  scroll_area size: {self.canvas_container.scroll_area.size()}")
            
    def get_mock_data(self, category: str, tab_name: str) -> dict:
        """Get INI data - from file + database if available, otherwise mock data."""
        if category != 'ini':
            # Fallback for non-INI categories
            return self._get_fallback_mock_data(category, tab_name)
        
        # Get real data from INI manager + database
        if self.ini_manager:
            real_data = {}
            
            # Find sections that belong to this tab
            for section_name, section in self.ini_manager.current_sections.items():
                # Check if section belongs to this tab
                tab = get_tab_for_section(section_name, '3dsmax.ini')
                if tab == tab_name:
                    # Get real parameters from INI
                    section_params = {}
                    for param_name, param_value in section.parameters.items():
                        section_params[param_name] = param_value
                    
                    # Get available parameters from database (not in real INI)
                    db_params = self.db.get_parameters_for_section(section_name)
                    for param_name, param_data in db_params.items():
                        if param_name not in section_params:
                            # Add as available (dimmed) parameter
                            default_value = param_data.get('default', '')
                            section_params[param_name] = {
                                'value': default_value,
                                'available': True,  # Mark as available from database
                                'data': param_data
                            }
                    
                    if section_params:
                        real_data[section_name] = section_params
            
            if real_data:
                print(f"[Dynamic] Loaded {len(real_data)} sections for {tab_name}: {list(real_data.keys())}")
                return real_data
        
        # Fallback to mock data
        return self._get_fallback_mock_data(category, tab_name)
    
    def _get_fallback_mock_data(self, category: str, tab_name: str) -> dict:
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
            
    def create_parameter_widget(self, name: str, value: str, is_available: bool = False, param_data: dict = None, can_add: bool = False) -> QWidget:
        """Create parameter widget - supports available (dimmed) parameters."""
        # Get help text for this parameter
        help_text = self.get_help_text(name)
        
        # Get default value if available
        if is_available and param_data:
            default_value = param_data.get('default', value)
            if 'en' in param_data and 'description' in param_data['en']:
                help_text = param_data['en']['description']
        else:
            default_value = value
        
        param_widget = INIParameterWidget(name, default_value, param_type='auto', help_text=help_text)
        
        # Set available state if needed
        if is_available:
            param_widget.set_available_state(True, can_add=can_add)
            if param_data and 'en' in param_data and 'description' in param_data['en']:
                param_widget.set_tooltip(param_data['en']['description'])
            # Connect add button
            if can_add:
                param_widget.parameter_added.connect(lambda pname=name: self.on_parameter_added(pname, param_data))
                print(f">>> Signal connected for {name}, can_add={can_add}")
        
        param_widget.value_changed.connect(self.on_parameter_changed)
        return param_widget
    
    def on_parameter_added(self, param_name: str, param_data: dict):
        """Handle parameter addition from database to INI."""
        print(f">>> on_parameter_added HANDLER called for {param_name}")
        print(f">>> param_data: {param_data is not None}")
        # TODO: Add to INI with backup
        # DON'T reload view - widget already activated itself!
        # Just mark canvas as modified
        print(f">>> Parameter added successfully, widget self-activated")
        
    def get_help_text(self, param_name: str) -> str:
        """Get help text for parameter."""
        help_texts = {
            'SafeSceneScriptExecutionEnabled': 
                'SafeSceneScriptExecutionEnabled\n\n'
                'Enables safe script execution in 3ds Max.\n'
                'Prevents malicious scripts from running.\n\n'
                '💡 Recommended: ON for production\n'
                '⚠️  Turn OFF only for debugging',
            
            'MaxScriptDebuggerEnabled':
                'MaxScriptDebuggerEnabled\n\n'
                'Enables the MaxScript debugger.\n'
                'Allows step-by-step script debugging.\n\n'
                '💡 Recommended: OFF (performance impact)\n'
                '✅ Turn ON when developing scripts',
            
            'AllowUnsafeEval':
                'AllowUnsafeEval\n\n'
                'Allows execution of potentially unsafe code.\n'
                'Can expose security vulnerabilities.\n\n'
                '⚠️  Recommended: OFF (security risk)\n'
                '🔒 Only enable for trusted scripts',
            
            'RestrictFileAccess':
                'RestrictFileAccess\n\n'
                'Restricts file system access to allowed paths.\n'
                'Protects sensitive system files.\n\n'
                '💡 Recommended: ON for security\n'
                '📁 Configure AllowedPaths below',
            
            'AllowedPaths':
                'AllowedPaths\n\n'
                'Semicolon-separated list of allowed paths.\n'
                'Scripts can only access these locations.\n\n'
                '💡 Example: C:\\Projects;D:\\Assets\n'
                '📌 Use full absolute paths',
            
            'BlockNetworkAccess':
                'BlockNetworkAccess\n\n'
                'Blocks network access from scripts.\n'
                'Prevents data exfiltration.\n\n'
                '💡 Recommended: ON for security\n'
                '🌐 Turn OFF if scripts need internet',
            
            'VerifyPluginSignatures':
                'VerifyPluginSignatures\n\n'
                'Verifies digital signatures of plugins.\n'
                'Ensures plugins are from trusted sources.\n\n'
                '✅ Recommended: ON\n'
                '🔐 Protects against malicious plugins',
            
            'AllowUnsignedPlugins':
                'AllowUnsignedPlugins\n\n'
                'Allows loading unsigned plugins.\n'
                'May pose security risks.\n\n'
                '⚠️  Recommended: OFF\n'
                '🛠️  Enable only for development',
            
            'TrustedPublishers':
                'TrustedPublishers\n\n'
                'Semicolon-separated list of trusted publishers.\n'
                'Plugins from these publishers are allowed.\n\n'
                '💡 Example: Autodesk;Chaos;V-Ray\n'
                '✅ Add only verified publishers'
        }
        
        return help_texts.get(param_name, f'{param_name}\n\nNo help available for this parameter.')
        
    def on_parameter_changed(self, param_name: str, new_value: str):
        """Handle parameter value change."""
        print(f"Parameter changed: {param_name} = {new_value}")
        
        # Update in INI manager if available
        if self.ini_manager:
            # Find which section this parameter belongs to
            for section_name, section in self.ini_manager.current_sections.items():
                if param_name in section.parameters:
                    self.ini_manager.update_parameter(section_name, param_name, new_value)
                    print(f"Updated in INI manager: [{section_name}] {param_name} = {new_value}")
                    break
        
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
        
        # Revert in INI manager if available
        if self.ini_manager:
            self.ini_manager.revert_section(section_title)
            print(f"Reverted section in INI manager: {section_title}")
        
        canvas.mark_as_saved()
        
    def on_refresh_clicked(self):
        """Reload INI file from disk."""
        print("Refresh clicked - reloading INI...")
        if self.ini_manager and self.ini_manager.load_ini():
            # Reload current view
            print("✅ INI reloaded successfully")
            # TODO: Refresh canvas panels
        else:
            print("❌ Failed to reload INI")
    
    def on_revert_clicked(self):
        """Revert all changes."""
        print("Revert clicked - reverting all changes...")
        if self.ini_manager:
            self.ini_manager.revert_all()
            print(f"✅ Reverted all changes")
            # TODO: Refresh canvas panels to show original values
        else:
            print("No INI manager available")
    
    def on_apply_clicked(self):
        """Apply all changes and save to file."""
        print("Apply clicked - saving changes...")
        if self.ini_manager:
            if self.ini_manager.has_unsaved_changes():
                success, error = self.ini_manager.save_ini(create_backup=True)
                if success:
                    print(f"✅ Changes saved to {self.ini_manager.ini_path}")
                    print(f"Saved {self.ini_manager.get_modified_count()} parameters")
                    
                    # Mark all canvases as saved
                    for canvas in self.ini_manager.canvas_items if hasattr(self.ini_manager, 'canvas_items') else []:
                        canvas.mark_as_saved()
                else:
                    print(f"❌ Failed to save: {error}")
            else:
                print("No changes to save")
        else:
            print("No INI manager available")


def main():
    """Run the application standalone."""
    # Set UTF-8 encoding for console output
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    app = QApplication(sys.argv)
    
    # Set UTF-8 for Qt text rendering
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
    
    # Set application-wide style
    app.setStyle("Fusion")
    
    window = CanvasMainWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

