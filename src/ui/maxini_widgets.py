"""MaxINI Editor Widgets - Custom widgets for editing max.ini parameters."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QToolButton,
    QSizePolicy,
)

from src.modules.maxini_parser import MaxINIParameter, ParamType


class ParameterWidget(QWidget):
    """Base widget for editing a single max.ini parameter."""

    value_changed = Signal(str, object)  # key, new_value

    def __init__(self, parameter: MaxINIParameter, parent: Optional[QWidget] = None) -> None:
        """
        Initialize parameter widget.

        Args:
            parameter: MaxINI parameter to edit
            parent: Parent widget
        """
        super().__init__(parent)
        self.parameter = parameter
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize user interface."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(15)

        # Parameter name label with fixed width for alignment
        name_label = QLabel(f"<b>{self.parameter.key}</b>")
        name_label.setMinimumWidth(320)
        name_label.setMaximumWidth(320)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px;
            color: #ffffff;
            padding: 8px;
            background-color: #4a4a4a;
            border: 1px solid #666666;
            border-radius: 4px;
            margin-right: 10px;
        """)
        
        # Add tooltip if description exists
        if self.parameter.description_en:
            name_label.setToolTip(self.parameter.description_en)
        elif self.parameter.description_ru:
            name_label.setToolTip(self.parameter.description_ru)

        layout.addWidget(name_label)

        # Value widget (implemented by subclasses) with consistent styling
        self.value_widget = self.create_value_widget()
        if self.value_widget:
            self.value_widget.setMinimumWidth(180)
            self.value_widget.setMaximumWidth(200)
            self.value_widget.setStyleSheet("""
                padding: 4px 8px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #3c3c3c;
                color: #ffffff;
            """)
        layout.addWidget(self.value_widget)

        # Unit label if available
        if self.parameter.unit:
            unit_label = QLabel(self.parameter.unit)
            unit_label.setStyleSheet("color: #666; font-size: 10px;")
            layout.addWidget(unit_label)

        layout.addStretch()
        self.setLayout(layout)

    def create_value_widget(self) -> QWidget:
        """Create appropriate widget for parameter type. Override in subclasses."""
        return QLabel(str(self.parameter.value))

    def get_value(self):
        """Get current value from widget. Override in subclasses."""
        return self.parameter.value

    def set_value(self, value) -> None:
        """Set value in widget. Override in subclasses."""
        pass


class IntegerParameterWidget(ParameterWidget):
    """Widget for editing integer parameters."""

    def create_value_widget(self) -> QWidget:
        """Create QSpinBox for integer values."""
        spinbox = QSpinBox()
        spinbox.setMinimum(-2147483647)  # Max 32-bit int
        spinbox.setMaximum(2147483647)
        
        # Set validation constraints if available
        if self.parameter.validation:
            if self.parameter.validation.min_value is not None:
                spinbox.setMinimum(self.parameter.validation.min_value)
            if self.parameter.validation.max_value is not None:
                spinbox.setMaximum(self.parameter.validation.max_value)

        # Set current value
        if isinstance(self.parameter.value, int):
            spinbox.setValue(self.parameter.value)
        else:
            try:
                spinbox.setValue(int(self.parameter.value))
            except (ValueError, TypeError):
                spinbox.setValue(0)

        # Connect signal
        spinbox.valueChanged.connect(self._on_value_changed)
        
        return spinbox

    def get_value(self) -> int:
        """Get current integer value."""
        return self.value_widget.value()

    def set_value(self, value) -> None:
        """Set integer value."""
        if isinstance(value, int):
            self.value_widget.setValue(value)
        else:
            try:
                self.value_widget.setValue(int(value))
            except (ValueError, TypeError):
                self.value_widget.setValue(0)

    def _on_value_changed(self, value: int) -> None:
        """Handle value change."""
        self.value_changed.emit(self.parameter.key, value)


class BooleanParameterWidget(ParameterWidget):
    """Widget for editing boolean parameters."""

    def create_value_widget(self) -> QWidget:
        """Create QCheckBox for boolean values."""
        checkbox = QCheckBox()
        
        # Set current value
        if isinstance(self.parameter.value, bool):
            checkbox.setChecked(self.parameter.value)
        else:
            # Convert string/int to bool
            str_value = str(self.parameter.value).lower()
            checkbox.setChecked(str_value in ("1", "true", "yes", "on"))

        # Connect signal
        checkbox.toggled.connect(self._on_value_changed)
        
        return checkbox

    def get_value(self) -> bool:
        """Get current boolean value."""
        return self.value_widget.isChecked()

    def set_value(self, value) -> None:
        """Set boolean value."""
        if isinstance(value, bool):
            self.value_widget.setChecked(value)
        else:
            str_value = str(value).lower()
            self.value_widget.setChecked(str_value in ("1", "true", "yes", "on"))

    def _on_value_changed(self, checked: bool) -> None:
        """Handle value change."""
        self.value_changed.emit(self.parameter.key, checked)


class StringParameterWidget(ParameterWidget):
    """Widget for editing string parameters."""

    def create_value_widget(self) -> QWidget:
        """Create QLineEdit for string values."""
        line_edit = QLineEdit()
        line_edit.setText(str(self.parameter.value))
        
        # Set placeholder if available
        if self.parameter.description_en:
            line_edit.setPlaceholderText(self.parameter.description_en[:50] + "...")

        # Connect signal
        line_edit.textChanged.connect(self._on_value_changed)
        
        return line_edit

    def get_value(self) -> str:
        """Get current string value."""
        return self.value_widget.text()

    def set_value(self, value) -> None:
        """Set string value."""
        self.value_widget.setText(str(value))

    def _on_value_changed(self, text: str) -> None:
        """Handle value change."""
        self.value_changed.emit(self.parameter.key, text)


class PathParameterWidget(ParameterWidget):
    """Widget for editing path parameters."""

    def create_value_widget(self) -> QWidget:
        """Create QLineEdit with browse button for path values."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Path input
        line_edit = QLineEdit()
        line_edit.setText(str(self.parameter.value))
        
        # Browse button
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(30)
        browse_btn.clicked.connect(self._browse_path)

        layout.addWidget(line_edit)
        layout.addWidget(browse_btn)
        widget.setLayout(layout)

        # Store reference to line_edit
        self.path_line_edit = line_edit

        # Connect signal
        line_edit.textChanged.connect(self._on_value_changed)
        
        return widget

    def get_value(self) -> str:
        """Get current path value."""
        return self.path_line_edit.text()

    def set_value(self, value) -> None:
        """Set path value."""
        self.path_line_edit.setText(str(value))

    def _on_value_changed(self, text: str) -> None:
        """Handle value change."""
        self.value_changed.emit(self.parameter.key, text)

    def _browse_path(self) -> None:
        """Open file dialog for path selection."""
        current_path = self.path_line_edit.text()
        
        if current_path and Path(current_path).exists():
            start_dir = str(Path(current_path).parent)
        else:
            start_dir = str(Path.home())

        # Choose dialog type based on parameter name
        if "folder" in self.parameter.key.lower() or "directory" in self.parameter.key.lower():
            path = QFileDialog.getExistingDirectory(self, "Select Directory", start_dir)
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir)

        if path:
            self.path_line_edit.setText(path)


def create_parameter_widget(parameter: MaxINIParameter, parent: Optional[QWidget] = None) -> ParameterWidget:
    """
    Factory function to create appropriate widget for parameter type.

    Args:
        parameter: MaxINI parameter
        parent: Parent widget

    Returns:
        Appropriate parameter widget
    """
    if parameter.type == ParamType.INT:
        return IntegerParameterWidget(parameter, parent)
    elif parameter.type == ParamType.BOOL:
        return BooleanParameterWidget(parameter, parent)
    elif parameter.type == ParamType.PATH:
        return PathParameterWidget(parameter, parent)
    else:  # STRING or unknown
        return StringParameterWidget(parameter, parent)
