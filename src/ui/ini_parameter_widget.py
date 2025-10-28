"""
INI Parameter Widget for MaxManager.

Provides smart UI controls for different INI parameter types.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QSlider, QPushButton, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

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
    
    # Class-level parameter info loader (shared across all instances)
    _param_info_loader = None
    
    # Layout constants
    LABEL_MIN_WIDTH = 100  # Reduced from 150 to allow tighter layouts
    LABEL_MAX_WIDTH = 250  # Reduced from 300 to fit better in narrow windows
    PATH_TEXT_RIGHT_MARGIN = 34  # separator(1) + button(28) + padding(5)
    VALUE_MIN_WIDTH = 60   # Reduced from 80 to allow more compression
    
    def __init__(self, param_name: str, param_value: str, param_type: str = 'auto', help_text: str = None, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.param_value = param_value
        self.original_value = param_value
        self.is_modified = False
        
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
        
        self.name_label = QLabel(display_name)  # Store reference for retranslate
        name_label = self.name_label
        # Set font that supports Cyrillic
        font = QFont("Segoe UI", 9)
        font.setStyleHint(QFont.SansSerif)
        font.setFamily("Segoe UI")
        name_label.setFont(font)
        name_label.setWordWrap(False)
        name_label.setMinimumWidth(self.LABEL_MIN_WIDTH)
        name_label.setMaximumWidth(self.LABEL_MAX_WIDTH)
        name_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # Takes only needed space
        # Tooltip shows full name if truncated
        if len(display_name) > 40:
            name_label.setToolTip(f"{display_name}\n\nTechnical: {self.param_name}")
        else:
            name_label.setToolTip(f"Technical name: {self.param_name}")
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
        
        # Layout strategy: label LEFT, stretch MIDDLE, value RIGHT, undo RIGHTMOST
        # For path/string: no stretch before (they expand themselves)
        # For boolean/int/float: add stretch before to push right
        if self.param_type in ['path', 'string']:
            layout.addWidget(self.value_widget, 1)  # Stretch to fill available space
        else:
            layout.addStretch(1)  # Push control to the right
            layout.addWidget(self.value_widget, 0)  # Fixed size, right-aligned
        
        # Undo button (always takes space, but hidden/disabled when not modified)
        self.undo_button = QPushButton()
        self.undo_button.setObjectName("undo_button")
        self.undo_button.setFixedSize(20, 20)
        self.undo_button.setCursor(Qt.ArrowCursor)  # Default cursor when disabled
        self.undo_button.setToolTip("Revert to original value")
        self.undo_button.clicked.connect(self.reset_to_original)
        self.undo_button.setEnabled(False)  # Disabled by default
        self.undo_button.setProperty("hidden", True)  # Custom property for styling
        
        if QTA_AVAILABLE:
            self.undo_icon_visible = qta.icon('fa5s.undo', color='#990000')  # Burgundy/red
            self.undo_button.setIconSize(self.undo_button.size() * 0.6)  # 12x12 icon
        # Start with no icon/text - completely invisible
        
        layout.addWidget(self.undo_button)
        
    def create_boolean_widget(self) -> QWidget:
        """Create toggle switch for boolean values using FontAwesome icons."""
        if QTA_AVAILABLE:
            # Use QPushButton with FontAwesome toggle icons
            toggle = QPushButton()
            toggle.setCheckable(True)
            toggle.setChecked(self.param_value == '1')
            toggle.setFixedSize(30, 20)
            toggle.setCursor(Qt.PointingHandCursor)
            
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
        """Create spinbox for integer values."""
        spinbox = QSpinBox()
        spinbox.setRange(-999999, 999999)
        spinbox.setValue(int(self.param_value) if self.param_value else 0)
        spinbox.setButtonSymbols(QSpinBox.PlusMinus)  # Use +/- instead of arrows for now
        spinbox.valueChanged.connect(lambda val: self.on_value_changed(str(val)))
        return spinbox
        
    def create_float_widget(self) -> QWidget:
        """Create slider + spinbox for float values."""
        container = QWidget()
        container.setObjectName("float_widget_container")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setObjectName("float_slider")
        slider.setRange(0, 100)
        float_val = float(self.param_value) if self.param_value else 0.0
        slider.setValue(int(float_val * 100))
        # No minimum width - adapts to available space
        layout.addWidget(slider, 1)  # Stretch to fill space
        
        # SpinBox for precise input
        spinbox = QDoubleSpinBox()
        spinbox.setObjectName("float_spinbox")
        spinbox.setRange(-999999.0, 999999.0)
        spinbox.setDecimals(6)
        spinbox.setValue(float_val)
        spinbox.setFixedWidth(100)
        spinbox.setButtonSymbols(QDoubleSpinBox.PlusMinus)  # Use +/- instead of arrows
        layout.addWidget(spinbox)
        
        # Sync slider and spinbox
        slider.valueChanged.connect(lambda val: spinbox.setValue(val / 100.0))
        spinbox.valueChanged.connect(lambda val: slider.setValue(int(val * 100)))
        spinbox.valueChanged.connect(lambda val: self.on_value_changed(f"{val:.6f}"))
        
        # Apply container styles
        container.setStyleSheet("""
            QWidget#float_widget_container {
                background-color: transparent;
            }
        """)
        
        return container
        
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
        lineedit.setMinimumWidth(self.VALUE_MIN_WIDTH)
        
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
            }
            QPushButton#path_browse_button:hover {
                background-color: rgba(255, 255, 255, 20);
            }
        """)
        
        return container
        
    def create_string_widget(self) -> QWidget:
        """Create lineedit for string values."""
        lineedit = QLineEdit(self.param_value)
        lineedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lineedit.setMinimumWidth(self.VALUE_MIN_WIDTH)
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
            # Container with slider + spinbox
            spinbox = self.value_widget.findChild(QDoubleSpinBox)
            if spinbox:
                return f"{spinbox.value():.6f}"
            return self.param_value
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
            spinbox = self.value_widget.findChild(QDoubleSpinBox)
            if spinbox:
                spinbox.setValue(float(self.original_value) if self.original_value else 0.0)
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
                background-color: rgba(255, 255, 0, 30);
                border-left: 3px solid #FFFF00;
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
                border: 1px solid #9C823A;
            }
            INIParameterWidget QSpinBox, INIParameterWidget QDoubleSpinBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            INIParameterWidget QSpinBox:focus, INIParameterWidget QDoubleSpinBox:focus {
                border: 1px solid #555555;
                outline: none;
            }
            /* SpinBox buttons use standard +/- symbols */
            QSlider#float_slider {
                background-color: transparent;
            }
            QSlider#float_slider::groove:horizontal {
                background-color: #555555;
                height: 6px;
                border-radius: 3px;
            }
            QSlider#float_slider::handle:horizontal {
                background-color: white;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
                border: none;
            }
            QSlider#float_slider::handle:horizontal:hover {
                background-color: #E0E0E0;
            }
            QSlider#float_slider::handle:horizontal:pressed {
                background-color: #CCCCCC;
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
            }
            QPushButton#help_button:hover {
                background-color: transparent;
            }
            QPushButton#undo_button {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton#undo_button:hover {
                background-color: transparent;
            }
            QPushButton#undo_button:disabled {
                background-color: transparent;
            }
        """)

