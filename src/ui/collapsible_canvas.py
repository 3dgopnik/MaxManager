"""
Collapsible Canvas Widget for MaxManager.

Provides accordion-style panels with expand/collapse functionality.
Each panel has a header with title and arrow, and collapsible content area.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QMenu, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QPen

from .grid_layout_manager import GridLayoutManager, GridItem
from .layout_storage import LayoutStorage

try:
    import qtawesome as qta
    QTA_AVAILABLE = True
except ImportError:
    QTA_AVAILABLE = False


class CollapsibleCanvas(QWidget):
    """
    Collapsible panel widget with header and content area.
    
    Features:
    - Click on header or arrow to toggle expand/collapse
    - Double-click on header to toggle
    - No animation - instant state change
    - Visual feedback with arrow direction
    """
    
    toggled = Signal(bool)  # Emits True when expanded, False when collapsed
    reset_requested = Signal()  # Emits when reset button clicked
    save_requested = Signal()  # Emits when save button clicked
    
    def __init__(self, title: str, expanded: bool = True, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_expanded = expanded
        self.header = None  # Initialize before init_ui
        self.has_unsaved_changes = False  # Track unsaved changes
        
        self.init_ui()
        self.apply_styles()
        
        # Enable context menu on header
        self.header.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect(self.show_context_menu)
        
    def init_ui(self):
        """Initialize UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create header
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        # Create content area - gray opaque background, with bottom rounding
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #3A3A3A; border-bottom-left-radius: 7.5px; border-bottom-right-radius: 7.5px;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(5)
        
        layout.addWidget(self.content_widget, 0)  # No stretch
        
        # Set size policy: Expanding horizontally (equal width), Maximum vertically (shrink when collapsed)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        # Set initial state
        self.content_widget.setVisible(self.is_expanded)
        self.update_arrow()
        self.update_header_style()
        
    def create_header(self) -> QWidget:
        """Create header with title and arrow."""
        header = QWidget()
        header.setObjectName("canvas_header")
        header.setFixedHeight(30)
        header.setCursor(Qt.PointingHandCursor)
        
        # Enable mouse tracking for click events
        header.installEventFilter(self)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("canvas_title")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Save button (visible when there are unsaved changes)
        self.save_button = QPushButton()
        self.save_button.setObjectName("canvas_save")
        self.save_button.setFixedSize(20, 20)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setToolTip("Apply changes")
        self.save_button.clicked.connect(lambda: self.save_requested.emit())
        self.save_button.setVisible(False)  # Hidden by default
        
        if QTA_AVAILABLE:
            save_icon = qta.icon('fa5.save', color='white')
            self.save_button.setIcon(save_icon)
            self.save_button.setIconSize(self.save_button.size() * 0.8)  # 16x16 icon
        else:
            self.save_button.setText("💾")
            
        layout.addWidget(self.save_button)
        
        # Reset to default button (undo icon) - visible only when there are changes
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("canvas_reset")
        self.reset_button.setFixedSize(20, 20)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setToolTip("Reset to default values")
        self.reset_button.clicked.connect(lambda: self.reset_requested.emit())
        self.reset_button.setVisible(False)  # Hidden by default
        
        if QTA_AVAILABLE:
            reset_icon = qta.icon('fa5s.undo', color='white')
            self.reset_button.setIcon(reset_icon)
            self.reset_button.setIconSize(self.reset_button.size() * 0.6)  # 12x12 icon
        else:
            self.reset_button.setText("⟲")
            
        layout.addWidget(self.reset_button)
        
        # Arrow button with FontAwesome chevron icons
        self.arrow_button = QPushButton()
        self.arrow_button.setObjectName("canvas_arrow")
        self.arrow_button.setFixedSize(20, 20)
        self.arrow_button.setCursor(Qt.PointingHandCursor)
        self.arrow_button.clicked.connect(self.toggle)
        
        # Set initial arrow (icon or text)
        if QTA_AVAILABLE:
            self.update_arrow_icon()
        else:
            self.arrow_button.setText("▼")
        
        layout.addWidget(self.arrow_button)
        
        return header
        
    def update_header_style(self):
        """Update header style based on expand/collapse state."""
        if self.is_expanded:
            # Expanded - only top rounded
            self.header.setStyleSheet("""
                QWidget#canvas_header {
                    background-color: #9C823A;
                    border: none;
                    border-top-left-radius: 7.5px;
                    border-top-right-radius: 7.5px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                }
                QWidget#canvas_header:hover {
                    background-color: #9C823A;
                }
                QLabel#canvas_title {
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    background-color: transparent;
                }
                QPushButton#canvas_arrow {
                    background-color: transparent;
                    color: white;
                    border: none;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton#canvas_arrow:hover {
                    color: white;
                }
                QPushButton#canvas_reset {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 0px;
                }
                QPushButton#canvas_reset:hover {
                    background-color: transparent;
                }
                QPushButton#canvas_save {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 0px;
                }
                QPushButton#canvas_save:hover {
                    background-color: transparent;
                }
            """)
        else:
            # Collapsed - all corners rounded
            self.header.setStyleSheet("""
                QWidget#canvas_header {
                    background-color: #9C823A;
                    border: none;
                    border-radius: 7.5px;
                }
                QWidget#canvas_header:hover {
                    background-color: #9C823A;
                }
                QLabel#canvas_title {
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    background-color: transparent;
                }
                QPushButton#canvas_arrow {
                    background-color: transparent;
                    color: white;
                    border: none;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton#canvas_arrow:hover {
                    color: white;
                }
                QPushButton#canvas_reset {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 0px;
                }
                QPushButton#canvas_reset:hover {
                    background-color: transparent;
                }
                QPushButton#canvas_save {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 0px;
                }
                QPushButton#canvas_save:hover {
                    background-color: transparent;
                }
            """)
    
    def update_arrow(self):
        """Update arrow direction based on expanded state."""
        if QTA_AVAILABLE:
            self.update_arrow_icon()
        else:
            # Fallback to unicode
            if self.is_expanded:
                self.arrow_button.setText("▲")
            else:
                self.arrow_button.setText("▼")
                
    def update_arrow_icon(self):
        """Update arrow icon using FontAwesome 6 icons."""
        try:
            if self.is_expanded:
                # Expanded - chevron up
                icon = qta.icon('fa6s.chevron-up', color='white')
            else:
                # Collapsed - chevron down
                icon = qta.icon('fa6s.chevron-down', color='white')
                
            self.arrow_button.setIcon(icon)
            self.arrow_button.setIconSize(self.arrow_button.size() * 0.8)  # 16x16 icon in 20x20 button
            self.arrow_button.setText("")  # Clear text when using icon
        except Exception as e:
            # Fallback to unicode if icon fails
            print(f"Failed to load chevron icon: {e}")
            if self.is_expanded:
                self.arrow_button.setText("▲")
            else:
                self.arrow_button.setText("▼")
            
    def toggle(self):
        """Toggle expand/collapse state."""
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        self.update_arrow()
        self.update_header_style()
        
        print(f"[CollapsibleCanvas] toggle: '{self.title}', expanded={self.is_expanded}, size={self.width()}x{self.height()}, min_width={self.minimumWidth()}")
        
        # Force layout update to recalculate sizes
        self.updateGeometry()
        if self.parent():
            self.parent().updateGeometry()
        
        self.toggled.emit(self.is_expanded)
        
    def eventFilter(self, obj, event):
        """Handle double-click on header."""
        if self.header and obj == self.header:
            if event.type() == event.Type.MouseButtonDblClick:
                # Double-click only on left button
                if event.button() == Qt.LeftButton:
                    self.toggle()
                    return True
            elif event.type() == event.Type.MouseButtonPress:
                # Single click on header (left button only, not on arrow button)
                if event.button() == Qt.LeftButton:
                    if hasattr(self, 'arrow_button') and not self.arrow_button.geometry().contains(event.pos()):
                        self.toggle()
                    return True
        return super().eventFilter(obj, event)
        
    def add_content(self, widget: QWidget):
        """Add widget to content area."""
        self.content_layout.addWidget(widget)
        
    def clear_content(self):
        """Clear all content widgets."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def reset_all_parameters(self):
        """Reset all parameters in this canvas to original values."""
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'reset_to_original'):
                    widget.reset_to_original()
    
    def show_all_parameters(self):
        """Show all parameter widgets."""
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(True)
    
    def filter_parameters(self, search_text: str) -> bool:
        """Filter parameters by search text. Returns True if any matches found."""
        has_matches = False
        search_lower = search_text.lower()
        
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'param_name'):
                # Search in parameter name, display name, and value
                param_name = widget.param_name.lower()
                
                # Get display name from label
                name_label = widget.findChild(QLabel)
                display_name = name_label.text().lower() if name_label else ""
                
                # Check if matches
                if search_lower in param_name or search_lower in display_name:
                    widget.setVisible(True)
                    has_matches = True
                else:
                    widget.setVisible(False)
        
        return has_matches
                    
    def show_context_menu(self, pos):
        """Show context menu on header right-click."""
        # Get parent CanvasContainer to call expand/collapse all
        container = self.parent()
        while container and not isinstance(container, CanvasContainer):
            container = container.parent()
            
        if not container:
            return
            
        # Create minimal context menu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444444;
                padding: 5px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 20px;
            }
            QMenu::item:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 30);
            }
        """)
        
        # Add actions
        expand_all = menu.addAction("Expand All")
        collapse_all = menu.addAction("Collapse All")
        
        # Execute menu
        action = menu.exec_(self.header.mapToGlobal(pos))
        
        # Handle actions
        if action == expand_all:
            container.expand_all()
        elif action == collapse_all:
            container.collapse_all()
                
    def set_expanded(self, expanded: bool):
        """Programmatically set expanded state."""
        if self.is_expanded != expanded:
            self.toggle()
            
    def mark_as_modified(self):
        """Show save and reset buttons when there are unsaved changes."""
        self.has_unsaved_changes = True
        self.save_button.setVisible(True)
        self.reset_button.setVisible(True)
        
    def mark_as_saved(self):
        """Hide save and reset buttons when all changes are saved."""
        self.has_unsaved_changes = False
        self.save_button.setVisible(False)
        self.reset_button.setVisible(False)
            
    def apply_styles(self):
        """Apply visual styles."""
        # Set border-radius on the entire widget to clip children
        self.setStyleSheet("""
            CollapsibleCanvas {
                background-color: transparent;
                border: none;
                border-radius: 7.5px;
            }
        """)
        
        # Apply header styles separately to ensure proper rendering
        self.header.setStyleSheet("""
            QWidget#canvas_header {
                background-color: #9C823A;
                border: none;
                border-top-left-radius: 7.5px;
                border-top-right-radius: 7.5px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
            QWidget#canvas_header:hover {
                background-color: #9C823A;
            }
            QLabel#canvas_title {
                color: white;
                font-size: 10px;
                font-weight: bold;
                background-color: transparent;
            }
            QPushButton#canvas_arrow {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton#canvas_arrow:hover {
                color: white;
            }
            QPushButton#canvas_reset {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0px;
            }
            QPushButton#canvas_reset:hover {
                background-color: transparent;
            }
            QPushButton#canvas_save {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0px;
            }
            QPushButton#canvas_save:hover {
                background-color: transparent;
            }
            QPushButton#canvas_revert {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0px;
            }
        """)


class CanvasContainer(QWidget):
    """
    Container for multiple CollapsibleCanvas widgets with grid-based layout.
    
    Features:
    - Adaptive 1-4 column grid layout
    - Automatic positioning with collision detection
    - Save/load layout configurations
    - Scroll support with always-visible scrollbar
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas_items = {}  # canvas_id -> CollapsibleCanvas
        self.grid_manager = GridLayoutManager(max_columns=4)
        self.layout_storage = LayoutStorage()
        self.init_ui()
        
        # Enable context menu on canvas container
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def init_ui(self):
        """Initialize UI components with grid layout."""
        # Main layout with standard padding (NO right padding - scrollbar goes to edge)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 0, 10)  # Right margin 0 - scrollbar at edge
        main_layout.setSpacing(10)
        
        # Scroll area for multiple canvas panels
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Always visible
        
        # Container widget for canvas panels with grid layout
        self.canvas_widget = QWidget()
        self.canvas_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # QGridLayout for flexible positioning
        self.grid_layout = QGridLayout(self.canvas_widget)
        self.grid_layout.setContentsMargins(0, 0, 15, 0)  # Right margin for scrollbar
        self.grid_layout.setSpacing(10)  # 10px spacing as specified
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Set column stretch - all columns equal width
        for col in range(4):
            self.grid_layout.setColumnStretch(col, 1)
        
        self.scroll_area.setWidget(self.canvas_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Apply styles
        self.apply_styles()
        
        # Install resize event to handle responsive columns
        self.scroll_area.viewport().installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle viewport resize for responsive columns."""
        if obj == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            viewport_width = event.size().width()
            if self.grid_manager.update_columns(viewport_width):
                # Column count changed - rebuild layout
                self._rebuild_grid_layout()
        return super().eventFilter(obj, event)
        
    def add_canvas(self, canvas: CollapsibleCanvas, span: int = 1, row: int = None, col: int = None):
        """
        Add canvas panel to grid with automatic positioning.
        
        Args:
            canvas: CollapsibleCanvas widget to add
            span: Number of columns to span (1-4)
            row: Optional target row (None = auto)
            col: Optional target column (None = auto)
        """
        canvas_id = canvas.title
        
        # Add to grid manager
        if row is None or col is None:
            # Auto-position: find first free spot
            row = len(self.canvas_items)  # Start at next row
            col = 0
        
        grid_item = self.grid_manager.add_item(canvas_id, row, col, span)
        
        # Store canvas
        self.canvas_items[canvas_id] = canvas
        
        # Add to QGridLayout
        self.grid_layout.addWidget(
            canvas,
            grid_item.row,
            grid_item.col,
            1,  # rowSpan (always 1)
            grid_item.span  # colSpan
        )
        
        print(f"[CanvasContainer] Added '{canvas_id}' at row={grid_item.row}, col={grid_item.col}, span={grid_item.span}")
    
    def clear_canvases(self):
        """Remove all canvas panels from grid."""
        # Remove all widgets from grid layout
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # Clear tracking
        self.canvas_items.clear()
        self.grid_manager.clear()
        print("[CanvasContainer] Cleared all canvases")
                
    def expand_all(self):
        """Expand all canvas panels."""
        for canvas in self.canvas_items.values():
            if not canvas.is_expanded:
                canvas.toggle()
                    
    def collapse_all(self):
        """Collapse all canvas panels."""
        for canvas in self.canvas_items.values():
            if canvas.is_expanded:
                canvas.toggle()
    
    def _rebuild_grid_layout(self):
        """Rebuild grid layout when column count changes."""
        print(f"[CanvasContainer] Rebuilding layout for {self.grid_manager.current_columns} columns")
        
        # Remove all widgets from layout (but don't delete)
        widgets_to_restore = []
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widgets_to_restore.append(widget)
        
        # Re-add all widgets with updated positions
        for canvas_id, canvas in self.canvas_items.items():
            grid_item = self.grid_manager.get_item(canvas_id)
            if grid_item:
                self.grid_layout.addWidget(
                    canvas,
                    grid_item.row,
                    grid_item.col,
                    1,  # rowSpan
                    grid_item.span  # colSpan
                )
        
        print("[CanvasContainer] Layout rebuilt")
    
    def save_layout(self, layout_name: str = "default") -> bool:
        """Save current grid layout to storage."""
        layout_data = self.grid_manager.to_dict()
        return self.layout_storage.save_layout(layout_data, layout_name)
    
    def load_layout(self, layout_name: str = "default") -> bool:
        """Load grid layout from storage."""
        layout_data = self.layout_storage.load_layout(layout_name)
        if layout_data is None:
            return False
        
        # Clear current layout
        self.clear_canvases()
        
        # Load layout into grid manager
        self.grid_manager.from_dict(layout_data)
        
        print(f"[CanvasContainer] Loaded layout '{layout_name}'")
        return True
                    
    def show_context_menu(self, pos):
        """Show context menu on canvas right-click."""
        # Create minimal context menu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444444;
                padding: 5px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 20px;
            }
            QMenu::item:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 30);
            }
        """)
        
        # Add actions
        expand_all = menu.addAction("Expand All")
        collapse_all = menu.addAction("Collapse All")
        
        # Execute menu
        action = menu.exec_(self.mapToGlobal(pos))
        
        # Handle actions
        if action == expand_all:
            self.expand_all()
        elif action == collapse_all:
            self.collapse_all()
                
    def apply_styles(self):
        """Apply visual styles."""
        self.setStyleSheet("""
            CanvasContainer {
                background-color: transparent;
                border: none;
            }
            QWidget {
                background-color: transparent;
                border: none;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(51, 51, 51, 100);
                width: 5px;
                border: none;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #353535;
                border-radius: 2.5px;
                min-height: 30px;
                margin: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #404040;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

