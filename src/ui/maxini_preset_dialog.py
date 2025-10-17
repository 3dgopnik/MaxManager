"""MaxINI Preset Selection Dialog - Choose and apply presets."""

from typing import Optional, List
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QGroupBox,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QSplitter,
    QFrame,
    QWidget,
)

from src.modules.maxini_presets import MaxINIPreset, MaxINIPresetManager


class PresetListWidget(QListWidget):
    """Custom list widget for presets with enhanced display."""
    
    preset_selected = Signal(str)  # preset_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup list widget appearance."""
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.currentItemChanged.connect(self._on_item_changed)
    
    def add_preset(self, preset: MaxINIPreset, category: str = ""):
        """Add preset to list."""
        item = QListWidgetItem()
        
        # Create display text
        if category:
            display_text = f"{preset.name} ({category})"
        else:
            display_text = preset.name
        
        item.setText(display_text)
        item.setData(Qt.UserRole, preset.name)  # Store preset name
        
        # Add tooltip with description
        tooltip = f"{preset.description_en}\n\nTags: {', '.join(preset.tags)}"
        if preset.author != "MaxManager":
            tooltip += f"\nAuthor: {preset.author}"
        item.setToolTip(tooltip)
        
        self.addItem(item)
    
    def _on_item_changed(self, current, previous):
        """Handle item selection change."""
        if current:
            preset_name = current.data(Qt.UserRole)
            self.preset_selected.emit(preset_name)


class MaxINIPresetDialog(QDialog):
    """Dialog for selecting and applying max.ini presets."""
    
    preset_applied = Signal(str)  # preset_name
    
    def __init__(self, parent=None):
        """
        Initialize preset dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.preset_manager = MaxINIPresetManager()
        self.current_preset: Optional[MaxINIPreset] = None
        
        self.setWindowTitle("MaxINI Presets")
        self.setGeometry(300, 200, 700, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #4a4a4a;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        
        self.init_ui()
        self.load_presets()
    
    def init_ui(self):
        """Initialize user interface."""
        main_layout = QVBoxLayout()
        
        # Header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout()
        
        title_label = QLabel("<h2>MaxINI Presets</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Choose a preset to optimize your 3ds Max configuration")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(subtitle_label)
        
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.currentTextChanged.connect(self.filter_presets)
        filter_layout.addWidget(self.category_combo)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search presets...")
        self.search_edit.textChanged.connect(self.filter_presets)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Preset list
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("<b>Available Presets:</b>"))
        
        self.preset_list = PresetListWidget()
        self.preset_list.preset_selected.connect(self.on_preset_selected)
        left_layout.addWidget(self.preset_list)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right panel - Preset details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("<b>Preset Details:</b>"))
        
        # Preset info
        self.preset_info = QTextEdit()
        self.preset_info.setReadOnly(True)
        self.preset_info.setMaximumHeight(200)
        self.preset_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        right_layout.addWidget(self.preset_info)
        
        # Parameters preview
        right_layout.addWidget(QLabel("<b>Parameters to be changed:</b>"))
        
        self.parameters_preview = QTextEdit()
        self.parameters_preview.setReadOnly(True)
        self.parameters_preview.setMaximumHeight(150)
        self.parameters_preview.setStyleSheet("""
            QTextEdit {
                background-color: #f0f8ff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        right_layout.addWidget(self.parameters_preview)
        
        right_layout.addStretch()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 400])
        main_layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_apply = QPushButton("Apply Preset")
        self.btn_apply.clicked.connect(self.apply_preset)
        self.btn_apply.setEnabled(False)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        button_layout.addWidget(self.btn_apply)
        
        button_layout.addStretch()
        
        self.btn_preview = QPushButton("Preview Changes")
        self.btn_preview.clicked.connect(self.preview_changes)
        self.btn_preview.setEnabled(False)
        button_layout.addWidget(self.btn_preview)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_presets(self):
        """Load all presets into the list."""
        all_presets = self.preset_manager.get_all_presets()
        
        # Clear existing items
        self.preset_list.clear()
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        
        # Get categories
        categories = self.preset_manager.get_categories()
        for category in categories:
            self.category_combo.addItem(category)
        
        # Add presets
        for preset in all_presets.values():
            self.preset_list.add_preset(preset, preset.category)
    
    def filter_presets(self):
        """Filter presets based on category and search text."""
        category = self.category_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        all_presets = self.preset_manager.get_all_presets()
        
        # Clear list
        self.preset_list.clear()
        
        # Add filtered presets
        for preset in all_presets.values():
            # Filter by category
            if category != "All Categories" and preset.category != category:
                continue
            
            # Filter by search text
            if search_text:
                if not (search_text in preset.name.lower() or 
                       search_text in preset.description_en.lower() or
                       any(search_text in tag.lower() for tag in preset.tags)):
                    continue
            
            self.preset_list.add_preset(preset, preset.category)
    
    def on_preset_selected(self, preset_name: str):
        """Handle preset selection."""
        self.current_preset = self.preset_manager.get_preset_by_name(preset_name)
        
        if self.current_preset:
            self.update_preset_info()
            self.btn_apply.setEnabled(True)
            self.btn_preview.setEnabled(True)
        else:
            self.preset_info.clear()
            self.parameters_preview.clear()
            self.btn_apply.setEnabled(False)
            self.btn_preview.setEnabled(False)
    
    def update_preset_info(self):
        """Update preset information display."""
        if not self.current_preset:
            return
        
        preset = self.current_preset
        
        info_text = f"""
<b>{preset.name}</b>

<b>Description:</b>
{preset.description_en}

<b>Category:</b> {preset.category}
<b>Author:</b> {preset.author}
<b>Version:</b> {preset.version}
<b>Created:</b> {preset.created_date}

<b>Tags:</b> {', '.join(preset.tags)}
"""
        
        self.preset_info.setHtml(info_text)
        
        # Update parameters preview
        params_text = ""
        for key, value in preset.parameters.items():
            params_text += f"{key}: {value}\n"
        
        self.parameters_preview.setText(params_text)
    
    def preview_changes(self):
        """Show detailed preview of changes."""
        if not self.current_preset:
            return
        
        # Create detailed preview dialog
        preview_dialog = QMessageBox(self)
        preview_dialog.setWindowTitle("Preset Preview")
        preview_dialog.setIcon(QMessageBox.Information)
        
        preset = self.current_preset
        
        preview_text = f"""
<b>{preset.name}</b>

This preset will modify the following parameters:

"""
        
        for key, value in preset.parameters.items():
            preview_text += f"• <b>{key}</b>: {value}\n"
        
        preview_text += f"""

<b>Total parameters to change:</b> {len(preset.parameters)}

Click "Apply Preset" to confirm these changes.
A backup will be created automatically.
"""
        
        preview_dialog.setText(preview_text)
        preview_dialog.exec()
    
    def apply_preset(self):
        """Apply selected preset."""
        if not self.current_preset:
            return
        
        preset = self.current_preset
        
        # Confirm application
        reply = QMessageBox.question(
            self,
            "Apply Preset",
            f"Apply preset '{preset.name}'?\n\n"
            f"This will modify {len(preset.parameters)} parameters.\n"
            f"A backup will be created automatically.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.preset_applied.emit(preset.name)
            self.accept()


def launch_preset_dialog(parent=None):
    """Launch preset selection dialog."""
    dialog = MaxINIPresetDialog(parent)
    return dialog
