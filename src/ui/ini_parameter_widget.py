"""
INI Parameter Widget for MaxManager.

Provides smart UI controls for different INI parameter types.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QSlider, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

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
    
    def __init__(self, param_name: str, param_value: str, param_type: str = 'auto', parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.param_value = param_value
        self.original_value = param_value
        self.is_modified = False
        
        # Auto-detect type
        if param_type == 'auto':
            self.param_type = self.detect_type(param_value)
        else:
            self.param_type = param_type
            
        self.init_ui()
        self.apply_styles()
        
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Parameter name label (40% width)
        name_label = QLabel(self.param_name)
        name_label.setFont(QFont("Segoe UI", 9))
        name_label.setMinimumWidth(200)
        name_label.setMaximumWidth(300)
        layout.addWidget(name_label)
        
        # Value widget (60% width) - depends on type
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
            
        layout.addWidget(self.value_widget)
        layout.addStretch()
        
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
        slider.setMinimumWidth(100)
        layout.addWidget(slider)
        
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
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Path input
        lineedit = QLineEdit(self.param_value)
        lineedit.setObjectName("path_input")
        lineedit.textChanged.connect(self.on_value_changed)
        layout.addWidget(lineedit)
        
        # Separator line
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
                padding: 3px;
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
        
    def remove_highlight(self):
        """Remove modified highlight."""
        self.setProperty("modified", False)
        self.style().unpolish(self)
        self.style().polish(self)
        
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
        
    def apply_styles(self):
        """Apply visual styles."""
        self.setStyleSheet("""
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
        """)

