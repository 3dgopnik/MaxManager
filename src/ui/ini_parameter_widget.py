"""
INI Parameter Widget for MaxManager.

Provides smart UI controls for different INI parameter types.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QSlider, QPushButton, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QPainter, QFontMetrics, QCursor

# Import name formatter and parameter info loader
from ..utils.name_formatter import format_parameter_name
from ..modules.parameter_info_loader import ParameterInfoLoader
# DON'T import get_translation_manager here - will import inside functions to avoid caching

try:
    import qtawesome as qta
    QTA_AVAILABLE = True
except ImportError:
    QTA_AVAILABLE = False
    print("QtAwesome not available, using simple checkbox for toggles")


class ElidedLabel(QLabel):
    """QLabel with text eliding (truncate with ...) for long text."""
    
    def paintEvent(self, event):
        """Custom paint with elided text."""
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment() | Qt.TextSingleLine, elided)
        painter.end()


class ScrubbyIntSpinBox(QLineEdit):
    """Integer input with drag-to-change (scrubby slider). Minimal style."""
    
    valueChanged = Signal(int)
    
    def __init__(self, value=0, minimum=-999999, maximum=999999, parent=None):
        super().__init__(str(value), parent)
        self.setAlignment(Qt.AlignRight)
        self._value = value
        self._min = minimum
        self._max = maximum
        self._dragging = False
        self._drag_start_pos = None
        self._drag_start_value = 0
        self.setFixedWidth(100)  # Same as float for consistency
        
        # Connect text editing
        self.editingFinished.connect(self._on_text_changed)
        
    def _on_text_changed(self):
        """Handle manual text input."""
        try:
            new_val = int(self.text())
            self.setValue(new_val)
        except ValueError:
            self.setText(str(self._value))
    
    def setValue(self, value):
        """Set value programmatically."""
        value = max(self._min, min(self._max, value))
        if value != self._value:
            self._value = value
            self.setText(str(value))
            self.valueChanged.emit(value)
    
    def value(self):
        """Get current value."""
        return self._value
    
    def mousePressEvent(self, event):
        """Start drag on left mouse button."""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_start_value = self._value
            self.setCursor(QCursor(Qt.SizeHorCursor))  # ⟷ cursor
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Drag to change value."""
        if self._dragging:
            delta_x = event.globalPosition().toPoint().x() - self._drag_start_pos.x()
            
            # Modifiers for precision
            modifiers = event.modifiers()
            if modifiers & Qt.ShiftModifier:
                sensitivity = 0.1  # Slow (fine control)
            elif modifiers & Qt.ControlModifier:
                sensitivity = 10.0  # Fast
            else:
                sensitivity = 1.0  # Normal
            
            new_value = int(self._drag_start_value + delta_x * sensitivity)
            self.setValue(new_value)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """End drag."""
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self.setCursor(QCursor(Qt.IBeamCursor))  # Back to text cursor
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Mouse wheel to change value."""
        delta = event.angleDelta().y() / 120  # Standard wheel step
        
        # Modifiers for precision
        modifiers = event.modifiers()
        if modifiers & Qt.ShiftModifier:
            step = 0.1
        elif modifiers & Qt.ControlModifier:
            step = 10
        else:
            step = 1
        
        new_value = int(self._value + delta * step)
        self.setValue(new_value)
        event.accept()
    
    def enterEvent(self, event):
        """Change cursor on hover."""
        if not self._dragging:
            self.setCursor(QCursor(Qt.SizeHorCursor))  # ⟷ cursor
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Restore cursor on leave."""
        if not self._dragging:
            self.setCursor(QCursor(Qt.IBeamCursor))
        super().leaveEvent(event)


class ScrubbyFloatSpinBox(QLineEdit):
    """Float input with drag-to-change (scrubby slider). Minimal style."""
    
    valueChanged = Signal(float)
    
    def __init__(self, value=0.0, minimum=-999999.0, maximum=999999.0, decimals=6, parent=None):
        super().__init__(f"{value:.{decimals}f}", parent)
        self.setAlignment(Qt.AlignRight)
        self._value = value
        self._min = minimum
        self._max = maximum
        self._decimals = decimals
        self._dragging = False
        self._drag_start_pos = None
        self._drag_start_value = 0.0
        self.setFixedWidth(100)
        
        # Connect text editing
        self.editingFinished.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """Handle manual text input."""
        try:
            new_val = float(self.text())
            self.setValue(new_val)
        except ValueError:
            self.setText(f"{self._value:.{self._decimals}f}")
    
    def setValue(self, value):
        """Set value programmatically."""
        value = max(self._min, min(self._max, value))
        if abs(value - self._value) > 1e-10:
            self._value = value
            self.setText(f"{value:.{self._decimals}f}")
            self.valueChanged.emit(value)
    
    def value(self):
        """Get current value."""
        return self._value
    
    def mousePressEvent(self, event):
        """Start drag on left mouse button."""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_start_value = self._value
            self.setCursor(QCursor(Qt.SizeHorCursor))  # ⟷ cursor
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Drag to change value."""
        if self._dragging:
            delta_x = event.globalPosition().toPoint().x() - self._drag_start_pos.x()
            
            # Modifiers for precision
            modifiers = event.modifiers()
            if modifiers & Qt.ShiftModifier:
                sensitivity = 0.001  # Very slow (fine control)
            elif modifiers & Qt.ControlModifier:
                sensitivity = 0.1  # Fast
            else:
                sensitivity = 0.01  # Normal
            
            new_value = self._drag_start_value + delta_x * sensitivity
            self.setValue(new_value)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """End drag."""
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self.setCursor(QCursor(Qt.IBeamCursor))  # Back to text cursor
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Mouse wheel to change value."""
        delta = event.angleDelta().y() / 120  # Standard wheel step
        
        # Modifiers for precision
        modifiers = event.modifiers()
        if modifiers & Qt.ShiftModifier:
            step = 0.001
        elif modifiers & Qt.ControlModifier:
            step = 0.1
        else:
            step = 0.01
        
        new_value = self._value + delta * step
        self.setValue(new_value)
        event.accept()
    
    def enterEvent(self, event):
        """Change cursor on hover."""
        if not self._dragging:
            self.setCursor(QCursor(Qt.SizeHorCursor))  # ⟷ cursor
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Restore cursor on leave."""
        if not self._dragging:
            self.setCursor(QCursor(Qt.IBeamCursor))
        super().leaveEvent(event)


class INIParameterWidget(QWidget):
    """
    Smart widget for INI parameter with auto-type detection.
    
    Supports:
    - Boolean (0/1) → Toggle Switch
    - Integer → SpinBox
    - Float → Slider + DoubleSpinBox
    - Path → LineEdit + Browse button
    - String → LineEdit
    """
    
    value_changed = Signal(str, str)  # (param_name, new_value)
    modified_state_changed = Signal(bool)  # Emits True when modified, False when reverted
    parameter_added = Signal()  # Emitted when + button clicked and confirmed
    
    # Class-level parameter info loader (shared across all instances)
    _param_info_loader = None
    
    # Layout constants
    LABEL_FIXED_WIDTH = 180  # Fixed width for clean vertical alignment
    PATH_TEXT_RIGHT_MARGIN = 34  # separator(1) + button(28) + padding(5)
    NUMERIC_FIELD_WIDTH = 100  # Fixed width for all numeric fields (int/float)
    
    def __init__(self, param_name: str, param_value: str, param_type: str = 'auto', help_text: str = None, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.param_value = param_value
        self.original_value = param_value
        self.is_modified = False
        self.is_available = False  # Track if parameter is available from database
        
        # Initialize parameter info loader (once)
        if INIParameterWidget._param_info_loader is None:
            INIParameterWidget._param_info_loader = ParameterInfoLoader()
        
        # DON'T cache language in __init__ - will be read fresh in init_ui
        self.help_text_key = param_name  # Store key for later
        
        # Auto-detect type
        if param_type == 'auto':
            self.param_type = self.detect_type(param_value)
        else:
            self.param_type = param_type
            
        self.init_ui()
        self.apply_styles()
        
        # Don't register callback on each widget - too many callbacks!
        # Language change will be triggered manually from parent window
        
    def eventFilter(self, obj, event):
        """Handle hover events for help button."""
        if obj == self.help_button and QTA_AVAILABLE:
            if event.type() == event.Type.Enter:
                # Mouse entered - show white icon
                self.help_button.setIcon(self.help_button_white_icon)
                return False
            elif event.type() == event.Type.Leave:
                # Mouse left - show gray icon
                self.help_button.setIcon(self.help_button_gray_icon)
                return False
        return super().eventFilter(obj, event)
    
    def detect_type(self, value: str) -> str:
        """Auto-detect parameter type from value."""
        if not value:
            return 'string'
            
        # Boolean (0 or 1)
        if value in ('0', '1'):
            return 'boolean'
            
        # Path (contains :\ or .\ or starts with C:)
        if ':\\' in value or '.\\' in value or value.startswith('C:'):
            return 'path'
            
        # Float (contains decimal point)
        if '.' in value:
            try:
                float(value)
                return 'float'
            except ValueError:
                return 'string'
                
        # Integer
        try:
            int(value)
            return 'integer'
        except ValueError:
            return 'string'
            
    def init_ui(self):
        """Initialize UI based on parameter type."""
        # Import HERE to get FRESH translation manager
        from ..i18n import get_translation_manager
        
        # Get FRESH language RIGHT NOW
        tm = get_translation_manager()
        current_lang = tm.current_language.value
        
        # Get localized help text with FRESH language
        if INIParameterWidget._param_info_loader.has_info(self.param_name):
            help_text = INIParameterWidget._param_info_loader.get_help_text(self.param_name, current_lang) or f"Parameter: {self.param_name}"
        else:
            help_text = f"Parameter: {self.param_name}"
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # NO minimum width on widget - let it adapt to available space
        
        # Help icon button (at the beginning)
        self.help_button = QPushButton()
        self.help_button.setObjectName("help_button")
        self.help_button.setFixedSize(20, 20)
        self.help_button.setCursor(Qt.PointingHandCursor)
        self.help_button.setToolTip(help_text)
        self.help_button.setFocusPolicy(Qt.NoFocus)  # Prevent focus outline
        
        if QTA_AVAILABLE:
            # Start with gray icon
            self.help_button_gray_icon = qta.icon('fa5.question-circle', color='#666666')
            self.help_button_white_icon = qta.icon('fa5s.question-circle', color='white')
            self.help_button.setIcon(self.help_button_gray_icon)
            self.help_button.setIconSize(self.help_button.size() * 0.8)  # 16x16 in 20x20 button
            
            # Install event filter for hover
            self.help_button.installEventFilter(self)
        else:
            self.help_button.setText("?")
            
        layout.addWidget(self.help_button)
        
        # Parameter name label (40% width) - use localized name with FRESH language
        display_name = INIParameterWidget._param_info_loader.get_display_name(self.param_name, current_lang)
        if not display_name:  # Fallback if no info found
            display_name = format_parameter_name(self.param_name)
        
        self.name_label = ElidedLabel(display_name)  # Custom label with eliding
        name_label = self.name_label
        # Set font that supports Cyrillic
        font = QFont("Segoe UI", 9)
        font.setStyleHint(QFont.SansSerif)
        font.setFamily("Segoe UI")
        name_label.setFont(font)
        name_label.setWordWrap(False)
        name_label.setFixedWidth(self.LABEL_FIXED_WIDTH)  # Fixed width for clean alignment
        name_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Tooltip shows full name (always useful for long names)
        name_label.setToolTip(f"{display_name}\n\nTechnical: {self.param_name}")
        layout.addWidget(name_label, 0)  # No stretch
        
        # Value widget - depends on type
        if self.param_type == 'boolean':
            self.value_widget = self.create_boolean_widget()
        elif self.param_type == 'integer':
            self.value_widget = self.create_integer_widget()
        elif self.param_type == 'float':
            self.value_widget = self.create_float_widget()
        elif self.param_type == 'path':
            self.value_widget = self.create_path_widget()
        else:  # string
            self.value_widget = self.create_string_widget()
        
        # CRITICAL: Fixed layout - ALWAYS same order, no conditional spacing
        # Structure: [? icon] [name label] [stretch] [value widget] [undo 20px] [add 20px]
        
        # Add stretch BEFORE value widget (pushes value to the right)
        layout.addStretch(1)
        
        # Value widget with fixed behavior
        if self.param_type in ['path', 'string']:
            layout.addWidget(self.value_widget, 2)  # More stretch than the spacer
        else:
            layout.addWidget(self.value_widget, 0)  # Fixed size
        
        # UNDO button - ALWAYS reserved (20px fixed)
        self.undo_button = QPushButton()
        self.undo_button.setObjectName("undo_button")
        self.undo_button.setFixedSize(20, 20)
        self.undo_button.setCursor(Qt.ArrowCursor)
        self.undo_button.setToolTip("Revert to original value")
        self.undo_button.clicked.connect(self.reset_to_original)
        self.undo_button.setEnabled(False)
        self.undo_button.setProperty("hidden", True)
        self.undo_button.setFocusPolicy(Qt.NoFocus)
        
        if QTA_AVAILABLE:
            self.undo_icon_visible = qta.icon('fa5s.undo', color='#990000')
            self.undo_button.setIconSize(self.undo_button.size() * 0.6)
        
        layout.addWidget(self.undo_button, 0, Qt.AlignRight)
        
        # ADD button - ALWAYS reserved (20px fixed)
        self.add_button = QPushButton()
        self.add_button.setObjectName("add_button")
        self.add_button.setFixedSize(20, 20)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setToolTip("Add parameter to INI")
        self.add_button.clicked.connect(self.on_add_clicked)
        self.add_button.setVisible(False)
        self.add_button.setEnabled(False)
        self.add_button.setFocusPolicy(Qt.NoFocus)
        
        if QTA_AVAILABLE:
            add_icon = qta.icon('fa5s.plus', color='#4ec9b0')
            self.add_button.setIcon(add_icon)
            self.add_button.setIconSize(self.add_button.size() * 0.6)
        else:
            self.add_button.setText("+")
        
        layout.addWidget(self.add_button, 0, Qt.AlignRight)
        
        # Add button (for available parameters only, shown in ADVANCED mode)
        self.add_button = QPushButton()
        self.add_button.setObjectName("add_button")
        self.add_button.setFixedSize(20, 20)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setToolTip("Add parameter to INI")
        self.add_button.clicked.connect(self.on_add_clicked)
        self.add_button.setVisible(False)  # Hidden by default
        self.add_button.setFocusPolicy(Qt.NoFocus)
        
        if QTA_AVAILABLE:
            add_icon = qta.icon('fa5s.plus', color='#4ec9b0')
            self.add_button.setIcon(add_icon)
            self.add_button.setIconSize(self.add_button.size() * 0.6)
        else:
            self.add_button.setText("+")
        
        layout.addWidget(self.add_button)
        
    def create_boolean_widget(self) -> QWidget:
        """Create toggle switch for boolean values using FontAwesome icons."""
        if QTA_AVAILABLE:
            # Use QPushButton with FontAwesome toggle icons
            toggle = QPushButton()
            toggle.setCheckable(True)
            toggle.setChecked(self.param_value == '1')
            toggle.setFixedSize(30, 20)
            toggle.setCursor(Qt.PointingHandCursor)
            toggle.setFocusPolicy(Qt.NoFocus)  # Prevent focus outline
            
            # Update icon based on state
            def update_icon():
                if toggle.isChecked():
                    icon = qta.icon('fa5s.toggle-on', color='#E0E0E0')
                else:
                    icon = qta.icon('fa5s.toggle-off', color='#666666')
                toggle.setIcon(icon)
                toggle.setIconSize(toggle.size())  # Full 30x20 icon size
                
            update_icon()
            toggle.toggled.connect(lambda checked: (
                update_icon(),
                self.on_value_changed('1' if checked else '0')
            ))
            
            toggle.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                }
            """)
            
            return toggle
        else:
            # Fallback to simple checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(self.param_value == '1')
            checkbox.stateChanged.connect(lambda state: self.on_value_changed('1' if state else '0'))
            return checkbox
        
    def create_integer_widget(self) -> QWidget:
        """Create scrubby slider for integer values."""
        scrubby = ScrubbyIntSpinBox(
            value=int(self.param_value) if self.param_value else 0,
            minimum=-999999,
            maximum=999999
        )
        scrubby.valueChanged.connect(lambda val: self.on_value_changed(str(val)))
        return scrubby
        
    def create_float_widget(self) -> QWidget:
        """Create scrubby slider for float values."""
        float_val = float(self.param_value) if self.param_value else 0.0
        scrubby = ScrubbyFloatSpinBox(
            value=float_val,
            minimum=-999999.0,
            maximum=999999.0,
            decimals=6
        )
        scrubby.valueChanged.connect(lambda val: self.on_value_changed(f"{val:.6f}"))
        return scrubby
        
    def create_path_widget(self) -> QWidget:
        """Create lineedit + browse button for paths (integrated design)."""
        container = QWidget()
        container.setObjectName("path_widget_container")
        # No minimum width - adapts to available space
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Path input - expands to fill available space
        lineedit = QLineEdit(self.param_value)
        lineedit.setObjectName("path_input")
        lineedit.textChanged.connect(self.on_value_changed)
        lineedit.setCursorPosition(0)
        
        # Set text margins to prevent text overlap with browse button
        lineedit.setTextMargins(3, 0, self.PATH_TEXT_RIGHT_MARGIN, 0)
        
        lineedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # No minimum width - stretches to fill available space
        
        layout.addWidget(lineedit, 1)
        
        # Separator line - no spacing, lineedit padding handles it
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: #555555;")
        layout.addWidget(separator)
        
        # Browse button with folder icon
        browse_btn = QPushButton()
        browse_btn.setObjectName("path_browse_button")
        browse_btn.setFixedSize(28, 26)
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.setFocusPolicy(Qt.NoFocus)  # Prevent focus outline
        browse_btn.clicked.connect(lambda: self.browse_path(lineedit))
        
        if QTA_AVAILABLE:
            icon = qta.icon('fa6.folder', color='white')
            browse_btn.setIcon(icon)
            browse_btn.setIconSize(browse_btn.size() * 0.6)  # 16x16 icon in 28x26 button
        else:
            browse_btn.setText("📁")
            
        layout.addWidget(browse_btn)
        
        # Container styling - unified border
        container.setStyleSheet("""
            QWidget#path_widget_container {
                background-color: #2A2A2A;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QLineEdit#path_input {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0px;  /* No padding - using textMargins instead */
            }
            QPushButton#path_browse_button {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QPushButton#path_browse_button:hover {
                background-color: rgba(255, 255, 255, 20);
            }
            QPushButton#path_browse_button:focus {
                outline: none;
                border: none;
            }
        """)
        
        return container
        
    def create_string_widget(self) -> QWidget:
        """Create lineedit for string values (stretches like path fields)."""
        lineedit = QLineEdit(self.param_value)
        lineedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # No minimum width - stretches to fill available space like path fields
        lineedit.textChanged.connect(self.on_value_changed)
        return lineedit
        
    def browse_path(self, lineedit: QLineEdit):
        """Open file/folder browser."""
        from PySide6.QtWidgets import QFileDialog
        
        # Determine if it's a file or folder
        current_path = lineedit.text()
        if current_path.endswith(('\\', '/')):
            # Folder
            path = QFileDialog.getExistingDirectory(self, "Select Folder", current_path)
        else:
            # File
            path, _ = QFileDialog.getOpenFileName(self, "Select File", current_path)
            
        if path:
            lineedit.setText(path)
            
    def on_value_changed(self, new_value):
        """Handle value change."""
        if isinstance(new_value, int):
            new_value = str(new_value)
            
        if new_value != self.original_value:
            if not self.is_modified:  # State changed to modified
                self.is_modified = True
                self.highlight_modified()
                self.modified_state_changed.emit(True)
        else:
            if self.is_modified:  # State changed to unmodified
                self.is_modified = False
                self.remove_highlight()
                self.modified_state_changed.emit(False)
            
        self.value_changed.emit(self.param_name, new_value)
        
    def highlight_modified(self):
        """Highlight widget as modified (yellow background)."""
        # Don't override entire stylesheet, just add property
        self.setProperty("modified", True)
        self.style().unpolish(self)
        self.style().polish(self)
        # Show undo button (make visible and enabled)
        if hasattr(self, 'undo_button'):
            self.undo_button.setEnabled(True)
            self.undo_button.setProperty("hidden", False)
            self.undo_button.setCursor(Qt.PointingHandCursor)
            if QTA_AVAILABLE and hasattr(self, 'undo_icon_visible'):
                self.undo_button.setIcon(self.undo_icon_visible)
            else:
                self.undo_button.setText("⟲")
        
    def remove_highlight(self):
        """Remove modified highlight."""
        self.setProperty("modified", False)
        self.style().unpolish(self)
        self.style().polish(self)
        # Hide undo button (make invisible and disabled, but keep space)
        if hasattr(self, 'undo_button'):
            self.undo_button.setEnabled(False)
            self.undo_button.setProperty("hidden", True)
            self.undo_button.setCursor(Qt.ArrowCursor)
            # Clear icon/text completely - fully invisible
            from PySide6.QtGui import QIcon
            self.undo_button.setIcon(QIcon())  # Empty icon
            self.undo_button.setText("")
        
    def get_value(self) -> str:
        """Get current value as string."""
        if self.param_type == 'boolean':
            return '1' if self.value_widget.isChecked() else '0'
        elif self.param_type == 'integer':
            return str(self.value_widget.value())
        elif self.param_type == 'float':
            return f"{self.value_widget.value():.6f}"
        else:  # string or path
            if isinstance(self.value_widget, QLineEdit):
                return self.value_widget.text()
            else:
                lineedit = self.value_widget.findChild(QLineEdit)
                return lineedit.text() if lineedit else self.param_value
                
    def reset_to_original(self):
        """Reset value to original."""
        # Reset based on type
        if self.param_type == 'boolean':
            self.value_widget.setChecked(self.original_value == '1')
        elif self.param_type == 'integer':
            self.value_widget.setValue(int(self.original_value) if self.original_value else 0)
        elif self.param_type == 'float':
            self.value_widget.setValue(float(self.original_value) if self.original_value else 0.0)
        elif self.param_type == 'path' or self.param_type == 'string':
            if isinstance(self.value_widget, QLineEdit):
                self.value_widget.setText(self.original_value)
            else:
                lineedit = self.value_widget.findChild(QLineEdit)
                if lineedit:
                    lineedit.setText(self.original_value)
        
        self.is_modified = False
        self.remove_highlight()
        self.modified_state_changed.emit(False)
    
    def set_available_state(self, available: bool, can_add: bool = True):
        """Set widget as available (dimmed) - parameter exists in database but not in real INI."""
        self.is_available = available
        if available:
            # Make widget visually dimmed
            self.setProperty("available", True)
            self.setEnabled(False)  # Disable editing (can only add via + button)
            # Show + button if allowed (ADVANCED mode)
            if hasattr(self, 'add_button'):
                self.add_button.setVisible(can_add)
        else:
            self.setProperty("available", False)
            self.setEnabled(True)
            if hasattr(self, 'add_button'):
                self.add_button.setVisible(False)
        
        self.style().unpolish(self)
        self.style().polish(self)
    
    def on_add_clicked(self):
        """Handle add button click - signal to add parameter to INI."""
        # Emit signal that parent can handle
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Add Parameter",
            f"Add {self.param_name} to INI file?\n\nDefault value: {self.param_value}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Emit signal to parent to handle actual INI modification
            self.parameter_added.emit()
            # Convert to active state
            self.set_available_state(False)
            self.setEnabled(True)
    
    def set_tooltip(self, text: str):
        """Set tooltip text for parameter."""
        if hasattr(self, 'name_label'):
            self.name_label.setToolTip(text)
        self.setToolTip(text)
    
    def on_language_changed(self):
        """Handle language change."""
        # Import FRESH to avoid caching
        from ..i18n import get_translation_manager
        
        # Get FRESH language
        tm = get_translation_manager()
        current_lang = tm.current_language.value
        
        # Update display name
        if INIParameterWidget._param_info_loader.has_info(self.param_name):
            display_name = INIParameterWidget._param_info_loader.get_display_name(self.param_name, current_lang) or format_parameter_name(self.param_name)
        else:
            display_name = format_parameter_name(self.param_name)
        
        # Find and update name label - search all QLabel children
        labels = self.findChildren(QLabel)
        if labels:
            # First QLabel is the name label
            labels[0].setText(display_name)
            labels[0].update()  # Force repaint
        
        # Update help text
        if INIParameterWidget._param_info_loader.has_info(self.param_name):
            help_text = INIParameterWidget._param_info_loader.get_help_text(self.param_name, current_lang) or f"Parameter: {self.param_name}"
        else:
            help_text = f"Parameter: {self.param_name}"
        
        # Update tooltip on help button
        if hasattr(self, 'help_button'):
            self.help_button.setToolTip(help_text)
        
        # Force repaint of entire widget
        self.update()
        
    def apply_styles(self):
        """Apply visual styles."""
        self.setStyleSheet("""
            QToolTip {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444444;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 10px;
                border-radius: 0px;
            }
            INIParameterWidget {
                background-color: transparent;
                border: none;
                padding: 2px;
            }
            INIParameterWidget:hover {
                background-color: rgba(255, 255, 255, 10);
            }
            INIParameterWidget[modified="true"] {
                background-color: transparent;
                border-left: none;
            }
            INIParameterWidget[available="true"] {
                opacity: 0.5;
            }
            INIParameterWidget[available="true"] > QLabel {
                color: #888888;
            }
            INIParameterWidget[available="true"] QLineEdit,
            INIParameterWidget[available="true"] QSpinBox,
            INIParameterWidget[available="true"] QDoubleSpinBox {
                background-color: #1A1A1A;
                color: #666666;
                border: 1px solid #333333;
            }
            INIParameterWidget > QLabel {
                color: white;
                background-color: transparent;
            }
            INIParameterWidget QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            INIParameterWidget QLineEdit:focus {
                border: 1px solid #555555;
                outline: none;
            }
            INIParameterWidget QSpinBox, INIParameterWidget QDoubleSpinBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            INIParameterWidget QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 3px;
            }
            INIParameterWidget QPushButton:hover {
                background-color: #555555;
            }
            QPushButton#help_button {
                background-color: transparent;
                border: none;
                padding: 0px;
                outline: none;
            }
            QPushButton#help_button:hover {
                background-color: transparent;
            }
            QPushButton#help_button:focus {
                outline: none;
                border: none;
            }
            QPushButton#undo_button {
                background-color: transparent;
                border: none;
                padding: 0px;
                outline: none;
            }
            QPushButton#undo_button:hover {
                background-color: transparent;
            }
            QPushButton#undo_button:focus {
                outline: none;
                border: none;
            }
            QPushButton#undo_button:disabled {
                background-color: transparent;
            }
        """)

