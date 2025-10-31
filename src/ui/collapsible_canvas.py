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
        
        # Resize grip in bottom-right corner
        self.resize_grip = self.create_resize_grip()
        
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
    
    def create_resize_grip(self) -> QWidget:
        """Create resize grip widget in bottom-right corner."""
        grip = QWidget(self)
        grip.setObjectName("resize_grip")
        grip.setFixedSize(20, 20)
        grip.setCursor(Qt.SizeFDiagCursor)  # Diagonal resize cursor
        
        # Icon for grip - resize bottom-right icon
        if QTA_AVAILABLE:
            grip_label = QLabel(grip)
            grip_label.setFixedSize(20, 20)
            grip_label.setAlignment(Qt.AlignCenter)
            grip_pixmap = qta.icon('mdi.resize-bottom-right', color='#666666').pixmap(16, 16)
            grip_label.setPixmap(grip_pixmap)
        else:
            grip.setStyleSheet("color: #666666; font-size: 16px;")
            grip_text = QLabel("⋰", grip)  # Diagonal resize symbol
            grip_text.setAlignment(Qt.AlignCenter)
        
        # Install event filter for drag
        grip.installEventFilter(self)
        self._resize_start_pos = None
        self._resize_start_width = 0
        
        # Position in bottom-right corner (will be updated in resizeEvent)
        self._position_resize_grip()
        
        return grip
    
    def _position_resize_grip(self):
        """Position resize grip in bottom-right corner."""
        if hasattr(self, 'resize_grip'):
            x = self.width() - self.resize_grip.width() - 5
            y = self.height() - self.resize_grip.height() - 5
            self.resize_grip.move(x, y)
            self.resize_grip.raise_()  # Always on top
    
    def resizeEvent(self, event):
        """Update resize grip position on canvas resize."""
        super().resizeEvent(event)
        self._position_resize_grip()
        
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
        """Handle drag on header and resize on grip."""
        # Handle resize grip events
        if hasattr(self, 'resize_grip') and obj == self.resize_grip:
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._resize_start_pos = event.globalPos()
                    self._resize_start_width = self.width()
                    print(f"[ResizeGrip] Start resize: {self.title}, width={self._resize_start_width}px")
                    return True
            
            elif event.type() == event.Type.MouseMove:
                if self._resize_start_pos:
                    # Calculate new width based on mouse movement
                    delta = event.globalPos().x() - self._resize_start_pos.x()
                    new_width = self._resize_start_width + delta
                    
                    # Calculate span based on width thresholds
                    # Use actual column width from parent
                    base_width = self._resize_start_width
                    
                    # Thresholds: 1.3x, 2.2x, 3.2x (more responsive)
                    # Each span adds base_width + 10px spacing
                    if new_width >= base_width * 3.2:
                        new_span = 4
                    elif new_width >= base_width * 2.2:
                        new_span = 3
                    elif new_width >= base_width * 1.3:
                        new_span = 2
                    else:
                        new_span = 1
                    
                    new_span = max(1, min(4, new_span))
                    
                    # Only log every 10th event to reduce spam
                    if not hasattr(self, '_resize_log_counter'):
                        self._resize_log_counter = 0
                    self._resize_log_counter += 1
                    
                    if self._resize_log_counter % 10 == 0:
                        print(f"[ResizeGrip] Dragging: delta={delta}px, new_width={new_width}px, span={new_span}x")
                    return True
            
            elif event.type() == event.Type.MouseButtonRelease:
                if event.button() == Qt.LeftButton and self._resize_start_pos:
                    # Calculate final span (same logic as MouseMove)
                    delta = event.globalPos().x() - self._resize_start_pos.x()
                    new_width = self._resize_start_width + delta
                    
                    base_width = self._resize_start_width
                    
                    # Same thresholds as MouseMove
                    if new_width >= base_width * 3.2:
                        new_span = 4
                    elif new_width >= base_width * 2.2:
                        new_span = 3
                    elif new_width >= base_width * 1.3:
                        new_span = 2
                    else:
                        new_span = 1
                    
                    print(f"[ResizeGrip] End resize: {self.title}, new_span={new_span}x (delta={delta}px, new_width={new_width}px)")
                    
                    # Request resize from container
                    self.request_resize(new_span)
                    
                    self._resize_start_pos = None
                    return True
        
        # Handle header drag events
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
    
    def request_resize(self, new_span: int):
        """Request resize from CanvasContainer."""
        print(f"[Canvas.request_resize] START for '{self.title}' → {new_span}x")
        
        # Find CanvasContainer parent
        container = self.parent()
        print(f"[Canvas.request_resize] Direct parent: {type(container).__name__}")
        
        search_depth = 0
        while container and not isinstance(container, CanvasContainer):
            container = container.parent()
            search_depth += 1
            if search_depth > 10:
                print(f"[Canvas.request_resize] ERROR: Search depth exceeded (10 levels)")
                break
            if container:
                print(f"[Canvas.request_resize] Level {search_depth}: {type(container).__name__}")
        
        print(f"[Canvas.request_resize] Found container: {type(container).__name__ if container else 'None'}")
        print(f"[Canvas.request_resize] Has resize_canvas: {hasattr(container, 'resize_canvas') if container else False}")
        
        if container and hasattr(container, 'resize_canvas'):
            print(f"[Canvas.request_resize] CALLING container.resize_canvas('{self.title}', {new_span})")
            container.resize_canvas(self.title, new_span)
        else:
            print(f"[Canvas.request_resize] ERROR: CanvasContainer not found or no resize_canvas method")
            
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
        """Initialize UI components with TRUE grid layout (QGridLayout)."""
        # Main layout with standard padding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 0, 10)
        main_layout.setSpacing(10)
        
        # Scroll area for canvas panels
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setViewportMargins(0, 0, 0, 0)
        
        # Container widget with QGridLayout (supports colspan!)
        self.canvas_widget = QWidget()
        self.canvas_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        
        # CRITICAL: QGridLayout - supports multi-column spanning!
        from PySide6.QtWidgets import QGridLayout
        self.grid_layout = QGridLayout(self.canvas_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)  # 10px margins
        self.grid_layout.setSpacing(10)  # 10px spacing
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll_area.setWidget(self.canvas_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Apply styles
        self.apply_styles()
        
        # Install resize event
        self.scroll_area.viewport().installEventFilter(self)
        
        self._initial_layout_done = False
    
    def showEvent(self, event):
        """Handle first show - setup columns after window is visible."""
        super().showEvent(event)
        if not self._initial_layout_done:
            self._initial_layout_done = True
            # Use QTimer to defer until after show is complete
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._rebuild_grid_layout() if hasattr(self, '_rebuild_grid_layout') else None)
    
    def eventFilter(self, obj, event):
        """Handle viewport resize for responsive columns."""
        if obj == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            viewport_width = event.size().width()
            
            # Force canvas_widget to match viewport width exactly
            self.canvas_widget.setMaximumWidth(viewport_width)
            
            # Update columns (may or may not change count)
            column_count_changed = self.grid_manager.update_columns(viewport_width)
            
            # ALWAYS rebuild grid on resize
            self._rebuild_grid_layout()
        return super().eventFilter(obj, event)
    
    def _rebuild_grid_layout(self):
        """Rebuild QGridLayout based on grid_manager positions and spans.
        
        CRITICAL: Spacing is ALWAYS 10px:
        - 10px from left edge of viewport
        - 10px between columns (horizontal spacing)
        - 10px between canvases in column (vertical spacing)
        - 10px to right edge of viewport
        
        Only canvas width changes on resize!
        """
        cols = self.grid_manager.current_columns
        print(f"[GridRebuild] Rebuilding for {cols} columns")
        
        # CRITICAL: Disable updates
        self.setUpdatesEnabled(False)
        
        # Remove all widgets from QGridLayout
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            # Don't delete widget, just remove from layout
        
        # Calculate column width
        viewport_width = self.scroll_area.viewport().width()
        
        # Calculate base column width (same formula as before)
        left_margin = 10
        right_margin = 10
        spacing = 10
        available_for_cols = viewport_width - left_margin - right_margin - (cols - 1) * spacing
        col_width = available_for_cols // cols
        
        print(f"[GridRebuild] Viewport: {viewport_width}px, col_width: {col_width}px, columns: {cols}")
        
        # Place canvases using QGridLayout with row, col, rowspan, colspan
        for canvas_id, canvas in self.canvas_items.items():
            if canvas_id in self.grid_manager.items:
                grid_item = self.grid_manager.items[canvas_id]
                row = grid_item.row
                col = grid_item.col
                span = grid_item.span
                
                # Calculate canvas width based on span
                canvas_width = span * col_width + (span - 1) * spacing
                canvas.setFixedWidth(canvas_width)
                
                # Add to QGridLayout: row, col, rowspan, colspan
                self.grid_layout.addWidget(canvas, row, col, 1, span)
                
                print(f"[GridRebuild] Placed '{canvas_id}' at ({row}, {col}), span={span}, width={canvas_width}px")
            else:
                print(f"[GridRebuild] WARNING: '{canvas_id}' not in grid_manager")
        
        # Re-enable updates
        self.setUpdatesEnabled(True)
        self.update()
        
        print(f"[GridRebuild] Complete!")
    
    def _update_visible_columns(self):
        """Alias for backwards compatibility - calls _rebuild_grid_layout."""
        self._rebuild_grid_layout()
    
    def add_canvas(self, canvas: CollapsibleCanvas, span: int = 1):
        """Add canvas to grid layout."""
        canvas_id = canvas.title
        
        # Add to grid_manager (auto-position)
        grid_item = self.grid_manager.add_item(canvas_id, row=0, col=0, span=span)
        
        # Store reference
        self.canvas_items[canvas_id] = canvas
        
        # Will be placed in grid during next _rebuild_grid_layout
        print(f"[CanvasContainer] Added '{canvas_id}' (will be placed in grid)")
    
    def resize_canvas(self, canvas_id: str, new_span: int):
        """
        Resize canvas to new span and redistribute layout.
        
        Args:
            canvas_id: Canvas title/ID
            new_span: New span (1-4 columns)
        """
        print(f"[CanvasContainer] Resize request: '{canvas_id}' to {new_span}x")
        
        # Update grid manager
        if self.grid_manager.resize_item(canvas_id, new_span):
            # Disable updates during redistribution
            self.setUpdatesEnabled(False)
            
            try:
                # Redistribute layout with new spans
                self._update_visible_columns()
                
                # Save layout
                if hasattr(self, 'layout_storage'):
                    self.layout_storage.save_layout(self.grid_manager)
            finally:
                self.setUpdatesEnabled(True)
                self.update()
                
            print(f"[CanvasContainer] Resize complete: '{canvas_id}' is now {new_span}x")
        else:
            print(f"[CanvasContainer] Resize failed for '{canvas_id}'")
    
    def clear_canvases(self):
        """Remove all canvas panels from grid layout."""
        # Remove all widgets from grid_layout
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
    
    def _rebuild_layout(self):
        """Rebuild grid layout when column count changes (alias for _rebuild_grid_layout)."""
        self._rebuild_grid_layout()
    
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

