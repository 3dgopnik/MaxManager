"""MaxINI Editor GUI - Main Window."""

import sys
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QGroupBox,
    QScrollArea,
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
from src.ui.maxini_widgets import create_parameter_widget, ParameterWidget
from src.ui.maxini_preset_dialog import launch_preset_dialog


class MaxINIEditorWindow(QDialog):
    """Main editor window for max.ini configuration."""
    
    VERSION = "0.3.4"
    BUILD_DATE = "2025-10-17"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize editor window.

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
        self.parameters: list[MaxINIParameter] = []
        self.parameter_widgets: list[ParameterWidget] = []
        self.ini_path: Optional[Path] = None
        self.has_unsaved_changes = False

        # UI Setup
        self.init_ui()
        self.load_max_ini()

    def init_ui(self) -> None:
        """Initialize user interface."""
        self.setWindowTitle(f"MaxINI Editor v{self.VERSION}")
        self.setGeometry(200, 100, 900, 700)
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
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
            QScrollArea {
                background-color: #2b2b2b;
                border: 1px solid #555555;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header = QLabel(f"<h2>MaxINI Editor v{self.VERSION}</h2>")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Version info label
        self.version_label = QLabel(f"Build: {self.BUILD_DATE} | MaxINI Configuration Editor with Presets")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("color: #888; font-size: 10px; margin-bottom: 8px;")
        main_layout.addWidget(self.version_label)

        # Tab widget for categories
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Button bar with responsive layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 5, 10, 5)

        # Create button group with flex layout
        button_container = QWidget()
        button_container.setMinimumHeight(50)
        button_container.setStyleSheet("""
            background-color: #3c3c3c; 
            border-radius: 5px; 
            padding: 5px;
            border: 1px solid #555555;
        """)
        
        button_inner_layout = QHBoxLayout()
        button_inner_layout.setSpacing(10)
        button_inner_layout.setContentsMargins(10, 5, 10, 5)

        # Common button style
        button_style = """
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_save.setEnabled(False)
        self.btn_save.setMinimumHeight(35)
        self.btn_save.setStyleSheet(button_style)
        button_inner_layout.addWidget(self.btn_save)

        self.btn_reload = QPushButton("Reload")
        self.btn_reload.clicked.connect(self.load_max_ini)
        self.btn_reload.setMinimumHeight(35)
        self.btn_reload.setStyleSheet(button_style)
        button_inner_layout.addWidget(self.btn_reload)

        self.btn_presets = QPushButton("Load Preset...")
        self.btn_presets.clicked.connect(self.load_preset)
        self.btn_presets.setMinimumHeight(35)
        self.btn_presets.setStyleSheet("""
            QPushButton {
                background-color: #4169E1;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0000CD;
            }
            QPushButton:pressed {
                background-color: #000080;
            }
        """)
        button_inner_layout.addWidget(self.btn_presets)

        self.btn_restore_backup = QPushButton("Restore from Backup...")
        self.btn_restore_backup.clicked.connect(self.restore_from_backup)
        self.btn_restore_backup.setMinimumHeight(35)
        self.btn_restore_backup.setStyleSheet(button_style)
        button_inner_layout.addWidget(self.btn_restore_backup)

        button_inner_layout.addStretch()

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setMinimumHeight(35)
        self.btn_close.setStyleSheet(button_style)
        button_inner_layout.addWidget(self.btn_close)

        button_container.setLayout(button_inner_layout)
        button_layout.addWidget(button_container)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def load_max_ini(self) -> None:
        """Load max.ini file and populate UI."""
        try:
            # Find max.ini
            self.ini_path = self._find_max_ini()

            if not self.ini_path:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Could not find max.ini file!\n\nLooked in:\n"
                    "- C:/Users/<user>/AppData/Local/Autodesk/3dsMax/2025 - 64bit/ENU/\n"
                    "- C:/Users/<user>/AppData/Local/Autodesk/3dsMax/2024 - 64bit/ENU/",
                )
                return

            # Update version label
            self.version_label.setText(f"Editing: {self.ini_path}")

            # Load parameters
            self.parameters = self.parser.load(self.ini_path)

            # Group by category
            grouped = self.parser.group_by_category(self.parameters)

            # Clear existing tabs and widgets
            self.tab_widget.clear()
            self.parameter_widgets.clear()

            # Create tab for each category
            for category, params in grouped.items():
                tab = self._create_category_tab(category, params)
                self.tab_widget.addTab(tab, category.value.title())

            self.has_unsaved_changes = False
            self._update_window_title()

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading max.ini", f"Failed to load max.ini:\n\n{str(e)}"
            )

    def save_changes(self) -> None:
        """Save changes to max.ini with validation."""
        try:
            # Update parameters from widgets
            self._update_parameters_from_widgets()

            # Validate parameters
            errors = self.parser.validate(self.parameters)

            if errors:
                error_msg = "\n".join([f"• {err.key}: {err.message}" for err in errors])
                QMessageBox.warning(
                    self,
                    "Validation Errors",
                    f"Found {len(errors)} validation error(s):\n\n{error_msg}",
                )
                return

            # Create backup
            if self.ini_path:
                backup = self.backup_manager.create_backup(self.ini_path, reason="manual_edit")

                # Save
                self.parser.save(self.ini_path, self.parameters, create_backup=False)

                QMessageBox.information(
                    self,
                    "Success",
                    f"Changes saved successfully!\n\nBackup created: {backup.file_path.name}",
                )

                self.has_unsaved_changes = False
                self._update_window_title()

        except Exception as e:
            QMessageBox.critical(self, "Error Saving", f"Failed to save changes:\n\n{str(e)}")

    def load_preset(self) -> None:
        """Load and apply a preset."""
        try:
            # Launch preset dialog as non-modal to prevent freezing
            preset_dialog = launch_preset_dialog(parent=self)
            preset_dialog.preset_applied.connect(self.apply_preset)
            preset_dialog.show()  # Use show() instead of exec() to prevent blocking
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Preset", f"Failed to load preset dialog:\n\n{str(e)}"
            )

    def apply_preset(self, preset_name: str) -> None:
        """Apply selected preset to parameters."""
        try:
            # Get preset
            preset = self.preset_manager.get_preset_by_name(preset_name)
            if not preset:
                QMessageBox.warning(self, "Error", f"Preset '{preset_name}' not found.")
                return

            # Create backup before applying preset
            if self.ini_path:
                backup = self.backup_manager.create_backup(
                    self.ini_path, 
                    reason=f"preset_applied_{preset_name.lower().replace(' ', '_')}"
                )

            # Apply preset to parameters
            self.parameters = self.preset_manager.apply_preset_to_parameters(preset, self.parameters)

            # Update widgets with new values
            self.update_widgets_from_parameters()

            # Show success message
            QMessageBox.information(
                self,
                "Preset Applied",
                f"Preset '{preset.name}' applied successfully!\n\n"
                f"Modified {len(preset.parameters)} parameters.\n"
                f"Backup created: {backup.file_path.name}\n\n"
                f"Click 'Save' to apply changes to max.ini file.",
            )

            # Mark as changed
            self.has_unsaved_changes = True
            self._update_window_title()
            self.btn_save.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(
                self, "Error Applying Preset", f"Failed to apply preset:\n\n{str(e)}"
            )

    def update_widgets_from_parameters(self) -> None:
        """Update widget values from parameters."""
        for widget in self.parameter_widgets:
            # Find corresponding parameter
            for param in self.parameters:
                if param.key == widget.parameter.key:
                    widget.set_value(param.value)
                    break

    def restore_from_backup(self) -> None:
        """Restore max.ini from a backup."""
        if not self.ini_path:
            return

        backups = self.backup_manager.list_backups(self.ini_path)

        if not backups:
            QMessageBox.information(self, "No Backups", "No backups found for this max.ini file.")
            return

        # Simple dialog showing backup list (for now)
        backup_info = "\n".join(
            [f"{i+1}. {b.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({b.file_size} bytes)" 
             for i, b in enumerate(backups[:10])]
        )

        QMessageBox.information(
            self,
            "Backups Available",
            f"Found {len(backups)} backup(s):\n\n{backup_info}\n\n"
            "Full backup restore UI will be implemented in next iteration.",
        )

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.save_changes()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def _find_max_ini(self) -> Optional[Path]:
        """Find max.ini file in standard locations."""
        possible_paths = [
            Path.home() / "AppData/Local/Autodesk/3dsMax/2025 - 64bit/ENU/3dsMax.ini",
            Path.home() / "AppData/Local/Autodesk/3dsMax/2024 - 64bit/ENU/3dsMax.ini",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _create_category_tab(self, category: ParamCategory, params: list[MaxINIParameter]) -> QWidget:
        """
        Create a tab for a parameter category with editable widgets.

        Args:
            category: Category enum
            params: Parameters in this category

        Returns:
            Tab widget
        """
        tab_widget = QWidget()
        tab_layout = QVBoxLayout()

        # Scroll area for parameters with proper scrolling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMinimumHeight(400)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(5)

        # Group parameters by INI sections
        param_groups = self._group_parameters(params)
        
        # Sort groups by name for consistent display
        sorted_groups = sorted(param_groups.items(), key=lambda x: x[0])
        
        # Add parameter groups
        for group_name, group_params in sorted_groups:
            group_widget = self._create_parameter_group(group_name, group_params)
            scroll_layout.addWidget(group_widget)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        tab_layout.addWidget(scroll)
        tab_widget.setLayout(tab_layout)

        return tab_widget

    def _update_window_title(self) -> None:
        """Update window title with unsaved indicator."""
        title = "MaxINI Editor"
        if self.has_unsaved_changes:
            title += " *"
        self.setWindowTitle(title)

    def _on_parameter_changed(self, key: str, value) -> None:
        """Handle parameter value change."""
        # Find and update parameter
        for param in self.parameters:
            if param.key == key:
                param.value = value
                break

        self.has_unsaved_changes = True
        self._update_window_title()
        self.btn_save.setEnabled(True)

    def _update_parameters_from_widgets(self) -> None:
        """Update parameter values from widgets before saving."""
        for widget in self.parameter_widgets:
            if widget.parameter.key:
                # Find corresponding parameter
                for param in self.parameters:
                    if param.key == widget.parameter.key:
                        param.value = widget.get_value()
                        break
    
    def _group_parameters(self, parameters: List[MaxINIParameter]) -> Dict[str, List[MaxINIParameter]]:
        """Group parameters by INI sections from max.ini file."""
        groups = {}
        
        # Map common parameter prefixes to INI sections
        section_mapping = {
            'safe': '[Security]',
            'showsecurity': '[Security]',
            'selection': '[Selection]',
            'standard': '[Standard]',
            'scene': '[Scene]',
            'sound': '[Sound]',
            'script': '[Script]',
            'startup': '[Startup]',
            'system': '[System]',
            'scand': '[Scan]',
            'sfmask': '[Mask]',
            'spinner': '[Spinner]',
            'save': '[Save]',
            'size': '[Size]',
            'shellac': '[Shellac]',
            'height': '[HeightManagerUS_Standard]',
            'normal': '[NormalBump]',
            'render': '[Rendering]',
            'viewport': '[Viewport]',
            'ui': '[UI]',
            'path': '[Paths]',
            'file': '[Files]',
            'backup': '[Backup]',
            'auto': '[AutoSave]',
            'undo': '[Undo]',
            'redo': '[Redo]',
            'grid': '[Grid]',
            'snap': '[Snap]',
            'units': '[Units]',
            'coordinate': '[Coordinate]',
            'transform': '[Transform]',
            'material': '[Material]',
            'light': '[Lighting]',
            'camera': '[Camera]',
            'animation': '[Animation]',
            'time': '[Time]',
            'playback': '[Playback]',
            'keyframe': '[Keyframe]',
            'track': '[TrackView]',
            'curve': '[Curve]',
            'motion': '[Motion]',
            'ik': '[IK]',
            'bone': '[Bone]',
            'skin': '[Skin]',
            'modifier': '[Modifier]',
            'space': '[Space]',
            'constraint': '[Constraint]',
            'reactor': '[Reactor]',
            'dynamics': '[Dynamics]',
            'cloth': '[Cloth]',
            'hair': '[Hair]',
            'fur': '[Fur]',
            'particle': '[Particle]',
            'fluid': '[Fluid]',
            'smoke': '[Smoke]',
            'fire': '[Fire]',
            'explosion': '[Explosion]',
            'wind': '[Wind]',
            'gravity': '[Gravity]',
            'force': '[Force]',
            'collision': '[Collision]',
            'deform': '[Deform]',
            'morph': '[Morph]',
            'blend': '[Blend]',
            'mix': '[Mix]',
            'noise': '[Noise]',
            'wave': '[Wave]',
            'ripple': '[Ripple]',
            'displace': '[Displace]',
            'bend': '[Bend]',
            'twist': '[Twist]',
            'taper': '[Taper]',
            'skew': '[Skew]',
            'squeeze': '[Squeeze]',
            'push': '[Push]',
            'relax': '[Relax]',
            'smooth': '[Smooth]',
            'optimize': '[Optimize]',
            'multires': '[Multires]',
            'tessellate': '[Tessellate]',
            'subdivide': '[Subdivide]',
            'meshsmooth': '[MeshSmooth]',
            'hsds': '[HSDS]',
            'nurbs': '[NURBS]',
            'spline': '[Spline]',
            'bezier': '[Bezier]',
            'catmull': '[Catmull]',
            'cardinal': '[Cardinal]',
            'linear': '[Linear]',
            'step': '[Step]',
            'smooth': '[Smooth]',
            'corner': '[Corner]',
            'beziercorner': '[BezierCorner]',
            'beziercorner': '[BezierCorner]',
        }
        
        for param in parameters:
            # Try to match parameter to INI section
            group_name = "[General]"  # Default section
            
            param_key_lower = param.key.lower()
            
            # Check for exact matches first
            for prefix, section in section_mapping.items():
                if param_key_lower.startswith(prefix):
                    group_name = section
                    break
            
            # Special cases for specific parameter names
            if 'height' in param_key_lower and 'manager' in param_key_lower:
                group_name = "[HeightManagerUS_Standard]"
            elif 'normal' in param_key_lower and 'bump' in param_key_lower:
                group_name = "[NormalBump]"
            elif 'security' in param_key_lower or 'safe' in param_key_lower:
                group_name = "[Security]"
            elif 'rendering' in param_key_lower or 'render' in param_key_lower:
                group_name = "[Rendering]"
            elif 'ui' in param_key_lower or 'interface' in param_key_lower:
                group_name = "[UI]"
            elif 'path' in param_key_lower:
                group_name = "[Paths]"
            elif 'viewport' in param_key_lower:
                group_name = "[Viewport]"
            elif 'backup' in param_key_lower or 'autosave' in param_key_lower:
                group_name = "[Backup]"
            elif 'undo' in param_key_lower or 'redo' in param_key_lower:
                group_name = "[Undo]"
            elif 'grid' in param_key_lower or 'snap' in param_key_lower:
                group_name = "[Grid]"
            elif 'units' in param_key_lower or 'coordinate' in param_key_lower:
                group_name = "[Units]"
            elif 'transform' in param_key_lower:
                group_name = "[Transform]"
            elif 'material' in param_key_lower:
                group_name = "[Material]"
            elif 'light' in param_key_lower:
                group_name = "[Lighting]"
            elif 'camera' in param_key_lower:
                group_name = "[Camera]"
            elif 'animation' in param_key_lower or 'time' in param_key_lower:
                group_name = "[Animation]"
            elif 'motion' in param_key_lower or 'ik' in param_key_lower:
                group_name = "[Motion]"
            elif 'modifier' in param_key_lower:
                group_name = "[Modifier]"
            elif 'space' in param_key_lower or 'constraint' in param_key_lower:
                group_name = "[Space]"
            elif 'dynamics' in param_key_lower or 'reactor' in param_key_lower:
                group_name = "[Dynamics]"
            elif 'particle' in param_key_lower:
                group_name = "[Particle]"
            elif 'fluid' in param_key_lower or 'smoke' in param_key_lower:
                group_name = "[Fluid]"
            elif 'deform' in param_key_lower or 'morph' in param_key_lower:
                group_name = "[Deform]"
            elif 'spline' in param_key_lower or 'nurbs' in param_key_lower:
                group_name = "[Spline]"
            
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(param)
        
        return groups
    
    def _create_parameter_group(self, group_name: str, parameters: List[MaxINIParameter]) -> QWidget:
        """Create collapsible group widget for parameters."""
        from PySide6.QtWidgets import QGroupBox
        
        # Create group box
        group_box = QGroupBox(group_name)
        group_box.setCheckable(True)
        group_box.setChecked(False)  # Collapsed by default
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 4px;
            }
            QGroupBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        
        # Create layout for parameters
        layout = QVBoxLayout()
        layout.setSpacing(2)
        
        # Add parameters to group
        for param in parameters:
            param_widget = create_parameter_widget(param)
            self.parameter_widgets.append(param_widget)
            layout.addWidget(param_widget)
            
            # Connect value changed signal
            param_widget.value_changed.connect(self._on_parameter_changed)
        
        group_box.setLayout(layout)
        return group_box

