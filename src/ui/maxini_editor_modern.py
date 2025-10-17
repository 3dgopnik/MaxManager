"""MaxINI Editor Modern - Fluent Design GUI with QFluentWidgets."""

import sys
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

# QFluentWidgets imports
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon, 
    Theme, setTheme, isDarkTheme, toggleTheme,
    CardWidget, HeaderCardWidget, InfoCardWidget,
    PushButton, PrimaryPushButton, ToolButton,
    LineEdit, ComboBox, SpinBox, CheckBox,
    TabBar, TabCloseButtonDisplayMode,
    ScrollArea, SimpleCardWidget,
    MessageBox, InfoBar, InfoBarPosition,
    FluentStyleSheet, setCustomStyleSheet,
    QApplication as FluentQApplication
)

# Add src to path for imports when running from 3ds Max
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.maxini_parser import (
    MaxINIParser,
    MaxINIParameter,
    ParamCategory,
)
from src.modules.maxini_backup import MaxINIBackupManager
from src.modules.maxini_exceptions import MaxINIEditorError
from src.modules.maxini_presets import MaxINIPresetManager


class MaxINIEditorModern(FluentWindow):
    """Modern MaxINI Editor with Fluent Design."""
    
    VERSION = "0.4.2"
    BUILD_DATE = "2025-10-17"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize modern editor window.
        
        Args:
            parent: Parent widget (typically Max main window from qtmax)
        """
        super().__init__(parent)
        
        # Initialize managers
        validation_rules_path = Path(__file__).parent.parent.parent / "data" / "validation" / "rules.json"
        self.parser = MaxINIParser(validation_rules_path)
        self.backup_manager = MaxINIBackupManager(max_backups=10)
        self.preset_manager = MaxINIPresetManager()
        
        # State
        self.parameters: List[MaxINIParameter] = []
        self.ini_path: Optional[Path] = None
        self.has_unsaved_changes = False
        
        # Setup UI
        self.setWindowTitle(f"MaxINI Editor v{self.VERSION}")
        self.setGeometry(200, 100, 1200, 800)
        
        # Set Fluent theme
        setTheme(Theme.DARK)
        
        # Custom accent color for MaxManager
        self.setCustomStyleSheet()
        
        self.init_ui()
        self.load_max_ini()
    
    def setCustomStyleSheet(self):
        """Set custom MaxManager accent color."""
        custom_style = f"""
        FluentWindow {{
            --primary-color: #29b866;
            --primary-color-hover: #2ac970;
            --primary-color-pressed: #249e5a;
        }}
        PrimaryPushButton {{
            background-color: #29b866;
            border: 1px solid #29b866;
        }}
        PrimaryPushButton:hover {{
            background-color: #2ac970;
            border: 1px solid #2ac970;
        }}
        PrimaryPushButton:pressed {{
            background-color: #249e5a;
            border: 1px solid #249e5a;
        }}
        """
        setCustomStyleSheet(self, custom_style)
    
    def init_ui(self) -> None:
        """Initialize modern user interface."""
        # Add navigation items
        self.addSubInterface(
            self.create_parameters_interface(), 
            FluentIcon.SETTING, 
            "Parameters", 
            NavigationItemPosition.TOP
        )
        
        self.addSubInterface(
            self.create_presets_interface(), 
            FluentIcon.LIBRARY, 
            "Presets", 
            NavigationItemPosition.TOP
        )
        
        self.addSubInterface(
            self.create_backup_interface(), 
            FluentIcon.HISTORY, 
            "Backups", 
            NavigationItemPosition.TOP
        )
        
        # Add status bar
        self.statusBar().showMessage("Ready")
    
    def create_parameters_interface(self) -> QWidget:
        """Create parameters editing interface."""
        interface = QWidget()
        layout = QVBoxLayout()
        
        # Header card
        header_card = HeaderCardWidget()
        header_card.setTitle("MaxINI Parameters")
        header_card.setSubTitle(f"Editing: {self.ini_path or 'Loading...'}")
        layout.addWidget(header_card)
        
        # Parameters scroll area
        scroll_area = ScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Group parameters by INI sections
        if self.parameters:
            param_groups = self._group_parameters(self.parameters)
            
            for group_name, group_params in sorted(param_groups.items()):
                group_card = self.create_parameter_group_card(group_name, group_params)
                scroll_layout.addWidget(group_card)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = PrimaryPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        save_btn.setEnabled(False)
        button_layout.addWidget(save_btn)
        
        reload_btn = PushButton("Reload")
        reload_btn.clicked.connect(self.load_max_ini)
        button_layout.addWidget(reload_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        interface.setLayout(layout)
        return interface
    
    def create_parameter_group_card(self, group_name: str, parameters: List[MaxINIParameter]) -> CardWidget:
        """Create a card for parameter group."""
        card = CardWidget()
        card.setTitle(group_name)
        card.setExpandable(True)
        card.setExpanded(False)  # Collapsed by default
        
        layout = QVBoxLayout()
        
        for param in parameters:
            param_widget = self.create_parameter_widget(param)
            layout.addWidget(param_widget)
        
        card.setContentLayout(layout)
        return card
    
    def create_parameter_widget(self, parameter: MaxINIParameter) -> QWidget:
        """Create modern parameter widget."""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Parameter name
        name_label = LineEdit()
        name_label.setText(parameter.key)
        name_label.setReadOnly(True)
        name_label.setMaximumWidth(300)
        layout.addWidget(name_label)
        
        # Value widget based on type
        if parameter.type == "integer":
            value_widget = SpinBox()
            value_widget.setRange(-999999, 999999)
            value_widget.setValue(int(parameter.value) if str(parameter.value).isdigit() else 0)
        elif parameter.type == "boolean":
            value_widget = CheckBox()
            value_widget.setChecked(bool(parameter.value))
        else:
            value_widget = LineEdit()
            value_widget.setText(str(parameter.value))
        
        layout.addWidget(value_widget)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_presets_interface(self) -> QWidget:
        """Create presets interface."""
        interface = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_card = HeaderCardWidget()
        header_card.setTitle("MaxINI Presets")
        header_card.setSubTitle("Choose optimization presets for your 3ds Max configuration")
        layout.addWidget(header_card)
        
        # Presets grid
        presets_layout = QVBoxLayout()
        
        # Built-in presets
        all_presets = self.preset_manager.get_all_presets()
        
        for preset_name, preset in all_presets.items():
            preset_card = InfoCardWidget(
                preset.name,
                preset.description_en,
                preset.category,
                FluentIcon.SETTING
            )
            preset_card.clicked.connect(lambda checked, p=preset: self.apply_preset(p))
            presets_layout.addWidget(preset_card)
        
        layout.addLayout(presets_layout)
        interface.setLayout(layout)
        return interface
    
    def create_backup_interface(self) -> QWidget:
        """Create backup management interface."""
        interface = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_card = HeaderCardWidget()
        header_card.setTitle("Backup Management")
        header_card.setSubTitle("Manage max.ini backups and restore points")
        layout.addWidget(header_card)
        
        # Backup actions
        button_layout = QHBoxLayout()
        
        create_backup_btn = PrimaryPushButton("Create Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        button_layout.addWidget(create_backup_btn)
        
        restore_backup_btn = PushButton("Restore from Backup")
        restore_backup_btn.clicked.connect(self.restore_from_backup)
        button_layout.addWidget(restore_backup_btn)
        
        layout.addLayout(button_layout)
        interface.setLayout(layout)
        return interface
    
    def load_max_ini(self) -> None:
        """Load max.ini file."""
        try:
            # Find max.ini path
            possible_paths = [
                Path.home() / "AppData" / "Local" / "Autodesk" / "3dsMax" / "2025 - 64bit" / "ENU" / "3dsMax.ini",
                Path.home() / "AppData" / "Local" / "Autodesk" / "3dsMax" / "2024 - 64bit" / "ENU" / "3dsMax.ini",
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.ini_path = path
                    break
            
            if not self.ini_path:
                InfoBar.error(
                    "Error", 
                    "max.ini file not found. Please ensure 3ds Max is installed.",
                    parent=self
                )
                return
            
            # Load parameters
            self.parameters = self.parser.load(self.ini_path)
            
            # Update UI
            self.update_parameters_interface()
            
            InfoBar.success(
                "Success", 
                f"Loaded {len(self.parameters)} parameters from {self.ini_path.name}",
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                "Error", 
                f"Failed to load max.ini: {str(e)}",
                parent=self
            )
    
    def update_parameters_interface(self) -> None:
        """Update parameters interface with loaded data."""
        # This would update the parameters interface
        # Implementation depends on how we structure the UI
        pass
    
    def save_changes(self) -> None:
        """Save changes to max.ini."""
        try:
            if not self.ini_path:
                return
            
            # Create backup before saving
            backup = self.backup_manager.create_backup(self.ini_path, reason="manual_save")
            
            # Save changes
            self.parser.save(self.ini_path, self.parameters)
            
            self.has_unsaved_changes = False
            
            InfoBar.success(
                "Success", 
                f"Changes saved successfully. Backup created: {backup.file_path.name}",
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                "Error", 
                f"Failed to save changes: {str(e)}",
                parent=self
            )
    
    def apply_preset(self, preset) -> None:
        """Apply selected preset."""
        try:
            # Create backup before applying preset
            if self.ini_path:
                backup = self.backup_manager.create_backup(
                    self.ini_path, 
                    reason=f"preset_applied_{preset.name.lower().replace(' ', '_')}"
                )
            
            # Apply preset to parameters
            self.parameters = self.preset_manager.apply_preset_to_parameters(preset, self.parameters)
            
            # Update UI
            self.update_parameters_interface()
            
            InfoBar.success(
                "Preset Applied", 
                f"Applied preset '{preset.name}' successfully!",
                parent=self
            )
            
            self.has_unsaved_changes = True
            
        except Exception as e:
            InfoBar.error(
                "Error", 
                f"Failed to apply preset: {str(e)}",
                parent=self
            )
    
    def create_backup(self) -> None:
        """Create manual backup."""
        try:
            if not self.ini_path:
                return
            
            backup = self.backup_manager.create_backup(self.ini_path, reason="manual_backup")
            
            InfoBar.success(
                "Backup Created", 
                f"Backup created: {backup.file_path.name}",
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                "Error", 
                f"Failed to create backup: {str(e)}",
                parent=self
            )
    
    def restore_from_backup(self) -> None:
        """Restore from backup."""
        # Implementation for backup restoration
        InfoBar.info(
            "Info", 
            "Backup restoration feature will be implemented in next iteration",
            parent=self
            )
    
    def _group_parameters(self, parameters: List[MaxINIParameter]) -> Dict[str, List[MaxINIParameter]]:
        """Group parameters by INI sections."""
        groups = {}
        
        for param in parameters:
            # Simple grouping logic - can be enhanced
            group_name = "[General]"
            
            param_key_lower = param.key.lower()
            
            if 'security' in param_key_lower or 'safe' in param_key_lower:
                group_name = "[Security]"
            elif 'render' in param_key_lower:
                group_name = "[Rendering]"
            elif 'ui' in param_key_lower:
                group_name = "[UI]"
            elif 'path' in param_key_lower:
                group_name = "[Paths]"
            elif 'animation' in param_key_lower:
                group_name = "[Animation]"
            elif 'backup' in param_key_lower:
                group_name = "[Backup]"
            
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(param)
        
        return groups


def launch_modern_editor(parent=None):
    """Launch modern MaxINI Editor."""
    try:
        # Use QFluentWidgets QApplication for better integration
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            # Set Fluent theme globally
            setTheme(Theme.DARK)
        
        editor = MaxINIEditorModern(parent)
        editor.show()
        return editor
        
    except ImportError as e:
        print(f"QFluentWidgets not available: {e}")
        print("Falling back to classic editor...")
        # Fallback to classic editor
        from src.ui.maxini_editor_window import MaxINIEditorWindow
        return MaxINIEditorWindow(parent)
        
    except Exception as e:
        print(f"Error launching modern editor: {e}")
        # Fallback to classic editor
        from src.ui.maxini_editor_window import MaxINIEditorWindow
        return MaxINIEditorWindow(parent)
