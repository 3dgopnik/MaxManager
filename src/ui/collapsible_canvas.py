"""
Collapsible Canvas Widget for MaxManager.

Provides accordion-style panels with expand/collapse functionality.
Each panel has a header with title and arrow, and collapsible content area.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QMenu, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QDrag, QPixmap

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
        layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)  # Don't let content dictate canvas size
        
        # Create header
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        # Create content area - gray opaque background, with bottom rounding
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #3A3A3A; border-bottom-left-radius: 7.5px; border-bottom-right-radius: 7.5px;")
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Expand to fill parent
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(5)
        self.content_layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)  # Don't let content dictate size
        
        layout.addWidget(self.content_widget, 0)  # No stretch
        
        # Set size policy: Expanding horizontally (equal width), Maximum vertically (shrink when collapsed)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        # NO minimum width on canvas - let column layout control width
        # Minimum width enforced by window minimum size instead
        
        # Set initial state
        self.content_widget.setVisible(self.is_expanded)
        self.update_arrow()
        self.update_header_style()
    
    def sizeHint(self):
        """Override sizeHint to respect set width constraints."""
        hint = super().sizeHint()
        # If we have explicit width constraints, use them
        if self.minimumWidth() > 0:
            hint.setWidth(self.minimumWidth())
        return hint
    
    def minimumSizeHint(self):
        """Override minimumSizeHint to respect set width constraints."""
        hint = super().minimumSizeHint()
        # If we have explicit width constraints, use them
        if self.minimumWidth() > 0:
            hint.setWidth(self.minimumWidth())
        return hint
        
    def create_header(self) -> QWidget:
        """Create header with title and arrow."""
        header = QWidget()
        header.setObjectName("canvas_header")
        header.setFixedHeight(30)
        header.setCursor(Qt.SizeAllCursor)  # Drag cursor
        # CRITICAL: Header must respect parent canvas width!
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Enable mouse tracking for drag and double-click
        header.installEventFilter(self)
        self._drag_start_pos = None
        self._is_dragging = False
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(5, 0, 10, 0)  # Left 5px for drag icon, right 10px
        layout.setSpacing(5)  # Tight spacing between drag icon and title
        
        # Drag handle icon - in the very left edge
        self.drag_icon = QLabel()
        self.drag_icon.setObjectName("drag_handle")
        self.drag_icon.setFixedSize(16, 16)  # Standard icon size
        self.drag_icon.setAlignment(Qt.AlignCenter)
        
        if QTA_AVAILABLE:
            # FontAwesome grip-vertical icon - white color
            drag_pixmap = qta.icon('fa5s.grip-vertical', color='white').pixmap(16, 16)
            self.drag_icon.setPixmap(drag_pixmap)
        else:
            self.drag_icon.setText("⋮⋮")
            self.drag_icon.setStyleSheet("color: white; font-size: 14px;")
        
        layout.addWidget(self.drag_icon)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("canvas_title")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Allow shrinking!
        layout.addWidget(self.title_label, 1)  # stretch=1 to take available space
        
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
        """Toggle expand/collapse state - NO JERKING."""
        # Find CanvasContainer parent
        container = self.parent()
        while container and not isinstance(container, CanvasContainer):
            container = container.parent()
        
        # Disable updates during toggle to prevent jerking
        if container:
            container.setUpdatesEnabled(False)
        
        try:
            self.is_expanded = not self.is_expanded
            self.content_widget.setVisible(self.is_expanded)
            self.update_arrow()
            self.update_header_style()
            
            print(f"[CollapsibleCanvas] toggle: '{self.title}', expanded={self.is_expanded}")
            
            # Force layout update
            self.updateGeometry()
            if self.parent():
                self.parent().updateGeometry()
            
            self.toggled.emit(self.is_expanded)
        finally:
            # Re-enable updates and force single repaint
            if container:
                container.setUpdatesEnabled(True)
                container.update()
        
    def eventFilter(self, obj, event):
        """Handle drag and double-click on header."""
        if self.header and obj == self.header:
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    # Start potential drag
                    self._drag_start_pos = event.pos()
                    self._is_dragging = False
                    return True
            
            elif event.type() == event.Type.MouseMove:
                if hasattr(self, '_drag_start_pos') and self._drag_start_pos and event.buttons() & Qt.LeftButton:
                    # Check if moved enough to start drag
                    if not self._is_dragging:
                        distance = (event.pos() - self._drag_start_pos).manhattanLength()
                        if distance > 5:  # Drag threshold
                            self._is_dragging = True
                            self.start_drag()
                    return True
            
            elif event.type() == event.Type.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    if hasattr(self, '_is_dragging'):
                        self._is_dragging = False
                    self._drag_start_pos = None
                    return True
            
            elif event.type() == event.Type.MouseButtonDblClick:
                # Toggle on double-click
                if event.button() == Qt.LeftButton:
                    self.toggle()
                    return True
        
        return super().eventFilter(obj, event)
    
    def start_drag(self):
        """Start Qt drag-and-drop operation."""
        print(f"[CollapsibleCanvas] Starting drag: {self.title}")
        
        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.title)  # Store canvas ID
        drag.setMimeData(mime_data)
        
        # Create pixmap of canvas for visual feedback
        pixmap = self.grab()
        # Make semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(255, 255, 255, 128))
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(self._drag_start_pos)
        
        # Execute drag
        result = drag.exec_(Qt.MoveAction)
        print(f"[CollapsibleCanvas] Drag finished: {result}")
        
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
    
    def update_language(self, new_title: str):
        """Update canvas title for language change (without recreating)."""
        self.title = new_title
        self.title_label.setText(new_title)
        print(f"[Canvas] Updated title to: {new_title}")
            
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
        
        # Enable drag-and-drop
        self.setAcceptDrops(True)
        
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
        self.scroll_area.setFrameShape(QFrame.NoFrame)  # Remove frame
        self.scroll_area.setViewportMargins(0, 0, 0, 0)  # Remove viewport margins
        
        # Container widget for canvas panels with dynamic columns
        self.canvas_widget = QWidget()
        # CRITICAL: Expanding to fill FULL viewport width
        self.canvas_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        
        # Horizontal layout for dynamic columns (1-4) - Bootstrap grid approach
        self.columns_layout = QHBoxLayout(self.canvas_widget)
        # CRITICAL: EXACT 10px margins and spacing - never changes!
        self.columns_layout.setContentsMargins(10, 10, 10, 10)  # 10px from ALL edges!
        self.columns_layout.setSpacing(10)  # 10px gutter between columns - ALWAYS 10px
        
        # Create 4 column layouts (will show/hide based on viewport width)
        self.column_layouts = []
        self.column_containers = []  # QWidget containers for each column
        for i in range(4):
            # Create container widget for this column
            col_container = QWidget()
            col_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # Preferred, not Expanding!
            
            col_layout = QVBoxLayout(col_container)
            col_layout.setContentsMargins(0, 0, 0, 0)  # NO extra margins inside column
            # CRITICAL: EXACT 10px spacing between canvases - never changes!
            col_layout.setSpacing(10)  # 10px spacing between canvases - ALWAYS 10px
            col_layout.setAlignment(Qt.AlignTop)
            
            self.column_layouts.append(col_layout)
            self.column_containers.append(col_container)
            self.columns_layout.addWidget(col_container)  # NO stretch parameter!
        
        self.scroll_area.setWidget(self.canvas_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Apply styles
        self.apply_styles()
        
        # Install resize event to handle responsive columns
        self.scroll_area.viewport().installEventFilter(self)
        
        # Defer initial column setup until window is shown (ChatGPT advice!)
        self._initial_layout_done = False
    
    def showEvent(self, event):
        """Handle first show - setup columns after window is visible."""
        super().showEvent(event)
        if not self._initial_layout_done:
            self._initial_layout_done = True
            # Use QTimer to defer until after show is complete
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._update_visible_columns() if hasattr(self, '_update_visible_columns') else None)
    
    def eventFilter(self, obj, event):
        """Handle viewport resize for responsive columns."""
        if obj == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            viewport_width = event.size().width()
            
            # Force canvas_widget to match viewport width exactly
            self.canvas_widget.setMaximumWidth(viewport_width)
            
            # Update columns (may or may not change count)
            column_count_changed = self.grid_manager.update_columns(viewport_width)
            
            # ALWAYS update layout on resize to recalculate column widths
            # This ensures spacing stays exactly 10px while canvas width adjusts
            self._update_visible_columns()
        return super().eventFilter(obj, event)
    
    def _update_visible_columns(self):
        """Redistribute all canvases when column count changes.
        
        CRITICAL: Spacing is ALWAYS 10px:
        - 10px from left edge of viewport
        - 10px between columns (horizontal spacing)
        - 10px between canvases in column (vertical spacing)
        - 10px to right edge of viewport
        
        Only canvas width changes on resize!
        """
        cols = self.grid_manager.current_columns
        print(f"[CanvasContainer] Redistributing to {cols} visible columns")
        
        # Collect all canvases in order
        all_canvases = []
        for col_layout in self.column_layouts:
            for i in range(col_layout.count()):
                item = col_layout.itemAt(i)
                if item and item.widget():
                    all_canvases.append(item.widget())
        
        # Remove all canvases from layouts
        for col_layout in self.column_layouts:
            while col_layout.count() > 0:
                col_layout.takeAt(0)
        
        # CRITICAL: Calculate column width with EXACT 10px spacing
        # canvas_widget.width() = margins(20) + cols*col_width + spacing*(cols-1)*10
        # Therefore: col_width = (canvas_widget - 20 - (cols-1)*10) / cols
        viewport_width = self.scroll_area.viewport().width() if hasattr(self, 'scroll_area') else self.canvas_widget.width()
        
        # Fixed spacing: margins and gutters INSIDE canvas_widget
        left_margin = 10  # from setContentsMargins
        right_margin = 10  # from setContentsMargins
        spacing_between_cols = 10  # from setSpacing
        
        # Calculate available width for columns (AFTER subtracting margins and spacing)
        available_for_cols = viewport_width - left_margin - right_margin - (cols - 1) * spacing_between_cols
        
        # Column width: divide available space equally
        col_width = available_for_cols // cols
        
        # Calculate actual space used
        total_cols_width = col_width * cols
        total_gutters = (cols - 1) * spacing_between_cols
        total_used = left_margin + total_cols_width + total_gutters + right_margin
        leftover = viewport_width - total_used
        
        print(f"[CanvasContainer] Width calculation (EXACT 10px spacing):")
        print(f"  Viewport: {viewport_width}px")
        print(f"  Left margin: {left_margin}px")
        print(f"  Columns: {cols} x {col_width}px = {total_cols_width}px")
        print(f"  Gutters: {cols-1} x {spacing_between_cols}px = {total_gutters}px")
        print(f"  Right margin: {right_margin}px")
        print(f"  Total used: {total_used}px")
        print(f"  Leftover: {leftover}px")
        print(f"  Layout: |{left_margin}px| [col] |{spacing_between_cols}px| [col] |{spacing_between_cols}px| [col] |{right_margin}px|")
        
        # CRITICAL: Use setFixedWidth() to enforce exact widths
        # Spacing is handled by layout.setSpacing(10), so columns must have exact width
        print(f"[DEBUG] Setting column widths (EXACT spacing):")
        for i, col_container in enumerate(self.column_containers):
            if i < cols:
                # Visible column - setFixedWidth to enforce exact spacing!
                col_container.setVisible(True)
                col_container.setFixedWidth(col_width)
                print(f"  Column {i}: visible=True, fixedWidth={col_width}px")
            else:
                # Hidden column - just hide it!
                col_container.setVisible(False)
                print(f"  Column {i}: visible=False (hidden)")
        
        # Force layout recalculation
        self.columns_layout.invalidate()
        self.columns_layout.activate()
        
        # Redistribute across visible columns
        for idx, canvas in enumerate(all_canvases):
            target_col = idx % cols  # Round-robin distribution
        
            # CRITICAL: Force EXACT canvas width - setFixedWidth!
            # This ensures spacing stays exactly 10px while canvas width adjusts
            canvas.setFixedWidth(col_width)
        
            self.column_layouts[target_col].addWidget(canvas)
        
        # Force complete layout update
        self.canvas_widget.updateGeometry()
        QApplication.processEvents()  # Single process is sufficient
        
        # REAL MEASUREMENTS: Log column container widths and positions
        print(f"\n[COLUMN CONTAINERS] Total: {len(self.column_containers)}, Active: {cols}")
        for i, col_container in enumerate(self.column_containers):
            if col_container.width() > 0:  # Only log non-zero width columns
                geom = col_container.geometry()
                print(f"  Column {i}: width={col_container.width()}px, geometry={geom.x()},{geom.y()} {geom.width()}x{geom.height()}")
        
        # REAL MEASUREMENTS: Log actual positions and spacing after layout
        print(f"\n[REAL MEASUREMENTS] After layout update:")
        for idx, canvas in enumerate(all_canvases):
            # Get global position
            global_pos = canvas.mapToGlobal(canvas.rect().topLeft())
            canvas_pos = self.canvas_widget.mapFromGlobal(global_pos)
            
            print(f"  Canvas '{canvas.title}':")
            print(f"    Position: x={canvas_pos.x()}px, y={canvas_pos.y()}px")
            print(f"    Size: {canvas.width()}x{canvas.height()}px")
            
            # Check header width inside canvas
            if hasattr(canvas, 'header') and canvas.header:
                header_geom = canvas.header.geometry()
                print(f"    Header: x={header_geom.x()}, width={header_geom.width()}px (inside canvas)")
            
            # Check canvas layout margins
            canvas_layout = canvas.layout()
            if canvas_layout:
                margins = canvas_layout.contentsMargins()
                print(f"    Canvas margins: L={margins.left()}, R={margins.right()}px")
            
            # Calculate spacing to next canvas (if exists)
            if idx < len(all_canvases) - 1:
                next_canvas = all_canvases[idx + 1]
                next_global = next_canvas.mapToGlobal(next_canvas.rect().topLeft())
                next_pos = self.canvas_widget.mapFromGlobal(next_global)
                
                # Horizontal spacing (if in same row)
                h_spacing = next_pos.x() - (canvas_pos.x() + canvas.width())
                # Vertical spacing (if in same column)
                v_spacing = next_pos.y() - (canvas_pos.y() + canvas.height())
                
                if abs(canvas_pos.y() - next_pos.y()) < 50:  # Same row
                    print(f"    → Horizontal spacing to '{next_canvas.title}': {h_spacing}px")
                elif abs(canvas_pos.x() - next_pos.x()) < 50:  # Same column
                    print(f"    ↓ Vertical spacing to '{next_canvas.title}': {v_spacing}px")
        
        # Left/right margins
        if all_canvases:
            first_canvas = all_canvases[0]
            first_global = first_canvas.mapToGlobal(first_canvas.rect().topLeft())
            first_pos = self.canvas_widget.mapFromGlobal(first_global)
            print(f"\n  Left margin: {first_pos.x()}px")
            print(f"  Canvas_widget width: {self.canvas_widget.width()}px")
        print()
        
        # Check canvas widths after redistribution
        canvas_widget_width = self.canvas_widget.width()
        if len(all_canvases) > 0:
            first_canvas = all_canvases[0]
            print(f"[CanvasContainer] Redistributed {len(all_canvases)} canvases to {cols} columns")
            print(f"  canvas_widget width: {canvas_widget_width}px")
            print(f"  First canvas actual width: {first_canvas.width()}px")
            # Verify calculation: (width - 20 margins - (cols-1)*10 spacing) / cols
            expected_col_width = (canvas_widget_width - 20 - (cols - 1) * 10) // cols
            print(f"  Expected column width: {expected_col_width}px")
    
    def dragEnterEvent(self, event):
        """Accept drag events with canvas data."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            print(f"[CanvasContainer] Drag entered")
    
    def dragMoveEvent(self, event):
        """Track drag position for visual feedback."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # TODO: Show drop zone indicator
    
    def dropEvent(self, event):
        """Handle canvas drop - reposition in grid."""
        if not event.mimeData().hasText():
            return
        
        canvas_id = event.mimeData().text()
        drop_pos = event.pos()
        
        # Convert to scroll area coordinates
        scroll_pos = self.scroll_area.mapFrom(self, drop_pos)
        canvas_pos = self.canvas_widget.mapFrom(self.scroll_area.viewport(), scroll_pos)
        
        print(f"[CanvasContainer] Drop '{canvas_id}' at canvas_pos ({canvas_pos.x()}, {canvas_pos.y()})")
        
        # Calculate which column was dropped into
        # CRITICAL: Use same calculation as _update_visible_columns() for consistency
        canvas_width = self.canvas_widget.width()
        cols = self.grid_manager.current_columns
        # Same formula: (width - 20 margins - (cols-1)*10 spacing) / cols
        col_width = (canvas_width - 20 - (cols - 1) * 10) // cols
        
        # Calculate column based on position (accounting for left margin)
        # Position relative to canvas_widget: subtract left margin (10px)
        relative_x = canvas_pos.x() - 10  # Subtract left margin
        target_col = max(0, min(relative_x // (col_width + 10), cols - 1))  # +10 for spacing
        
        print(f"[CanvasContainer] canvas_width={canvas_width}, col_width={col_width}, target_col={target_col}")
        
        # Calculate target position WITHIN column (row index)
        col_layout = self.column_layouts[target_col]
        target_row_index = 0
        cumulative_y = 0
        
        for i in range(col_layout.count()):
            item = col_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget_height = widget.height()
                if canvas_pos.y() > cumulative_y + widget_height // 2:
                    target_row_index = i + 1
                cumulative_y += widget_height + 10  # +10 for spacing
        
        print(f"[CanvasContainer] target_row_index={target_row_index} in column {target_col}")
        
        # Move canvas in grid manager
        if canvas_id in self.canvas_items:
            canvas = self.canvas_items[canvas_id]
            
            # Remove from current column
            old_col_index = None
            old_row_index = None
            for col_idx, col_layout_check in enumerate(self.column_layouts):
                for i in range(col_layout_check.count()):
                    item = col_layout_check.itemAt(i)
                    if item and item.widget() == canvas:
                        old_col_index = col_idx
                        old_row_index = i
                        col_layout_check.takeAt(i)
                        break
                if old_col_index is not None:
                    break
            
            # Insert at new position
            col_layout.insertWidget(target_row_index, canvas)
            
            print(f"[CanvasContainer] Moved '{canvas_id}': col{old_col_index}[{old_row_index}] → col{target_col}[{target_row_index}]")
        
        event.acceptProposedAction()
        
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
        
        # Add to grid manager with smart auto-positioning
        if row is None or col is None:
            # Smart balancing: distribute across columns like Trello
            num_items = len(self.canvas_items)
            cols = self.grid_manager.current_columns
            
            # Calculate which column has least items
            column_counts = [0] * cols
            for item in self.grid_manager.get_all_items():
                if item.col < cols:
                    column_counts[item.col] += 1
            
            # Find column with minimum items
            min_col = column_counts.index(min(column_counts))
            
            # Find next row in that column
            row = column_counts[min_col]
            col = min_col
        
        grid_item = self.grid_manager.add_item(canvas_id, row, col, span)
        
        # Store canvas
        self.canvas_items[canvas_id] = canvas
        
        # Add to appropriate column layout
        target_col = grid_item.col
        if target_col < len(self.column_layouts):
            self.column_layouts[target_col].addWidget(canvas)
            print(f"[CanvasContainer] Added '{canvas_id}' to column {target_col}, span={grid_item.span}")
        else:
            print(f"[CanvasContainer] ERROR: Column {target_col} out of range")
    
    def clear_canvases(self):
        """Remove all canvas panels from columns."""
        # Remove all widgets from all columns
        for col_layout in self.column_layouts:
            while col_layout.count() > 0:
                item = col_layout.takeAt(0)
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
    
    def _rebuild_layout(self):
        """Rebuild column layout when column count changes."""
        print(f"[CanvasContainer] Rebuilding layout for {self.grid_manager.current_columns} columns")
        
        # Remove all widgets from columns (but don't delete)
        all_canvases = []
        for col_layout in self.column_layouts:
            while col_layout.count() > 0:
                item = col_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    all_canvases.append(widget)
        
        # Re-add all widgets to correct columns
        for canvas_id, canvas in self.canvas_items.items():
            grid_item = self.grid_manager.get_item(canvas_id)
            if grid_item and grid_item.col < len(self.column_layouts):
                self.column_layouts[grid_item.col].addWidget(canvas)
        
        # Update visible columns
        self._update_visible_columns()
        
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

