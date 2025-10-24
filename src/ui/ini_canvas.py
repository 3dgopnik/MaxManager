"""
INI Canvas Widget for Dynamic INI Editor

This module provides the INICanvasWidget class for displaying and editing
INI section parameters with inline editing capabilities.

Author: MaxManager Team
Date: 2025-10-23
Version: 1.0.0
"""

from typing import List, Dict, Any, Tuple, Optional
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QStyledItemDelegate, QSpinBox, QComboBox, QLineEdit,
    QMessageBox, QApplication
)
from PySide6.QtCore import Signal, Qt, QTimer, QModelIndex
from PySide6.QtGui import QColor

from ..modules.maxini_parser import MaxINIParser, MaxINIParameter, ParamType
from ..modules.maxini_backup import MaxINIBackupManager

logger = logging.getLogger(__name__)

# Настройка детального логирования для отладки
def setup_detailed_logging():
    """Настройка детального логирования для отладки MaxManager."""
    # Создаем форматтер с техническими деталями
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
        datefmt='%H:%M:%S.%f'
    )
    
    # Создаем handler для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    
    # Настраиваем специфичные логгеры
    logging.getLogger('MaxManager').setLevel(logging.DEBUG)
    logging.getLogger('src.ui').setLevel(logging.DEBUG)
    
    logger.info("=== MaxManager Detailed Logging Initialized ===")
    logger.debug("Logging level: DEBUG")
    logger.debug("Console output: ENABLED")

# Автоматически настраиваем логирование при импорте
setup_detailed_logging()


class INICanvasWidget(QWidget):
    """
    Canvas widget for displaying and editing INI section parameters.
    
    Features:
    - QTreeWidget с inline editing
    - Change tracking (yellow highlights)
    - Save confirmation (green highlights)
    - Apply/Revert/Refresh buttons
    """
    
    # Signals
    changes_made = Signal(int)  # emit number of changed params
    save_requested = Signal()
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        parser: Optional[MaxINIParser] = None
    ) -> None:
        """
        Initialize canvas widget.
        
        Args:
            parent: Parent Qt widget
            parser: MaxINIParser instance for save/load operations
        """
        super().__init__(parent)
        
        # Store parser and backup manager
        logger.debug(f"Initializing parser: {parser is not None}")
        self.parser = parser or MaxINIParser()
        self.backup_manager = MaxINIBackupManager()
        logger.debug("Parser and backup manager created")
        
        # Initialize change tracking
        self._changes: Dict[str, Any] = {}
        self._original_params: List[MaxINIParameter] = []
        self._current_section: Optional[str] = None
        logger.debug("Change tracking structures initialized")
        
        # Setup UI
        logger.debug("Setting up UI components")
        self._setup_ui()
        
        logger.info("INICanvasWidget initialized successfully")
    
    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        logger.debug("=== UI SETUP START ===")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        logger.debug(f"Main layout margins: {layout.contentsMargins()}")
        logger.debug(f"Main layout spacing: {layout.spacing()}")
        
        # Create QTreeWidget
        logger.debug("Creating QTreeWidget")
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Parameter", "Value", "Type"])
        self.tree.setColumnWidth(0, 200)  # Parameter column
        self.tree.setColumnWidth(1, 300)  # Value column
        self.tree.setColumnWidth(2, 80)   # Type column
        logger.debug(f"Tree column widths: {[self.tree.columnWidth(i) for i in range(3)]}")
        logger.debug(f"Tree size: {self.tree.size()}")
        logger.debug(f"Tree geometry: {self.tree.geometry()}")
        
        # Enable inline editing
        self.tree.setEditTriggers(QTreeWidget.DoubleClicked)
        logger.debug("Tree edit triggers set to DoubleClicked")
        
        # Set custom delegate for Value column
        self.tree.setItemDelegateForColumn(1, INIValueDelegate())
        logger.debug("Custom delegate set for Value column")
        
        # Connect item changed signal
        self.tree.itemChanged.connect(self._on_item_changed)
        logger.debug("Item changed signal connected")
        
        # Add tree to layout
        layout.addWidget(self.tree)
        logger.debug("Tree widget added to main layout")
        
        # Create button bar
        logger.debug("Creating button layout")
        button_layout = QHBoxLayout()
        logger.debug(f"Button layout spacing: {button_layout.spacing()}")
        logger.debug(f"Button layout margins: {button_layout.contentsMargins()}")
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_from_file)
        button_layout.addWidget(self.refresh_btn)
        
        # Stretch
        button_layout.addStretch()
        logger.debug("Stretch added to button layout")
        
        # Revert button
        self.revert_btn = QPushButton("Revert")
        self.revert_btn.clicked.connect(self.revert_changes)
        button_layout.addWidget(self.revert_btn)
        
        # Apply button (primary)
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_changes)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
        """)
        button_layout.addWidget(self.apply_btn)
        logger.debug("Apply button added to layout")
        
        # Add button bar to layout
        layout.addLayout(button_layout)
        logger.debug("Button layout added to main layout")
        
        # Final UI state logging
        logger.debug(f"Final widget size: {self.size()}")
        logger.debug(f"Final widget geometry: {self.geometry()}")
        logger.debug(f"Final tree size: {self.tree.size()}")
        logger.debug(f"Final tree geometry: {self.tree.geometry()}")
        logger.debug("=== UI SETUP COMPLETE ===")
    
    def load_section(
        self,
        section_name: str,
        parameters: List[MaxINIParameter]
    ) -> None:
        """
        Load and display parameters for a specific INI section.
        
        Args:
            section_name: Name of INI section (e.g., "Security")
            parameters: List of parameters to display
            
        Raises:
            ValueError: If section_name is empty or parameters is empty
        """
        if not section_name:
            raise ValueError("Section name cannot be empty")
        if not parameters:
            raise ValueError("Parameters list cannot be empty")
        
        logger.info(f"Loading section: {section_name} ({len(parameters)} params)")
        logger.debug(f"Section name validation: {bool(section_name)}")
        logger.debug(f"Parameters count: {len(parameters)}")
        
        # Store current section and original parameters
        self._current_section = section_name
        self._original_params = parameters.copy()
        logger.debug(f"Current section set to: {self._current_section}")
        logger.debug(f"Original params copied: {len(self._original_params)} items")
        
        # Clear tree
        logger.debug("Clearing existing tree items")
        self.tree.clear()
        
        # Add parameters to tree
        logger.debug(f"Adding {len(parameters)} parameters to tree widget")
        for param in parameters:
            item = QTreeWidgetItem()
            item.setText(0, param.key)
            item.setText(1, str(param.value))
            item.setText(2, param.type.value)
            
            # Store parameter data in item
            item.setData(0, Qt.UserRole, param)
            
            self.tree.addTopLevelItem(item)
        
        # Apply any existing changes for this section
        self._apply_pending_changes()
        
        logger.debug(f"Section loaded: {section_name}")
    
    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle parameter value change.
        
        Args:
            item: Tree item that was changed
            column: Column that was edited (should be 1 for Value)
        """
        if column != 1:  # Only track changes in Value column
            return
        
        # Get parameter data
        param = item.data(0, Qt.UserRole)
        if not param:
            return
        
        # Get new value
        new_value = item.text(1)
        
        # Validate value
        is_valid, error_msg = self._validate_value(param, new_value)
        if not is_valid:
            # Show error tooltip
            item.setToolTip(1, error_msg)
            item.setBackground(1, QColor(255, 200, 200))  # Red for error
            return
        
        # Clear error state
        item.setToolTip(1, "")
        
        # Track change
        self._changes[param.key] = new_value
        
        # Set yellow background for modified
        item.setBackground(1, QColor(255, 255, 200))  # Yellow
        
        # Emit changes signal
        self.changes_made.emit(len(self._changes))
        
        logger.debug(f"Parameter changed: {param.key} = {new_value}")
    
    def _validate_value(self, param: MaxINIParameter, value: str) -> Tuple[bool, str]:
        """
        Умная валидация параметров с детальными сообщениями об ошибках.
        
        Args:
            param: Parameter being edited
            value: New value to validate
            
        Returns:
            (is_valid, error_message)
        """
        try:
            if param.type == ParamType.INT:
                # Проверяем диапазон для INT
                int_val = int(value)
                if int_val < -2147483648 or int_val > 2147483647:
                    return False, f"Integer value out of range: {value} (must be between -2,147,483,648 and 2,147,483,647)"
                return True, ""
                
            elif param.type == ParamType.BOOL:
                # Расширенная валидация для BOOL
                valid_bool_values = ["0", "1", "true", "false", "yes", "no", "on", "off", "enabled", "disabled"]
                if value.lower() not in valid_bool_values:
                    return False, f"Invalid boolean value: {value}. Use: 0/1, true/false, yes/no, on/off, enabled/disabled"
                return True, ""
                
            elif param.type == ParamType.PATH:
                # Расширенная валидация путей
                if len(value) > 260:
                    return False, "Path too long (max 260 characters)"
                
                # Проверяем запрещенные символы в путях
                invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
                for char in invalid_chars:
                    if char in value:
                        return False, f"Path contains invalid character: '{char}'"
                
                # Проверяем относительные пути
                if value.startswith('.') and not value.startswith('./'):
                    return False, "Relative path should start with './'"
                return True, ""
                
            else:  # STRING
                # Валидация строковых значений
                if len(value) > 1000:
                    return False, "String value too long (max 1000 characters)"
                
                # Проверяем на потенциально опасные символы
                if '\x00' in value:
                    return False, "String contains null character (\\x00)"
                return True, ""
                
        except ValueError as e:
            return False, f"Invalid {param.type.value} value: {value} - {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _apply_pending_changes(self) -> None:
        """Apply any pending changes for current section."""
        if not self._current_section:
            return
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            param = item.data(0, Qt.UserRole)
            if param and param.key in self._changes:
                # Update value and set yellow background
                item.setText(1, str(self._changes[param.key]))
                item.setBackground(1, QColor(255, 255, 200))  # Yellow
    
    def get_modified_params(self) -> List[MaxINIParameter]:
        """
        Get list of modified parameters ready for saving.
        
        Returns:
            List of MaxINIParameter objects with updated values
        """
        modified = []
        
        for param in self._original_params:
            if param.key in self._changes:
                # Create new parameter with updated value
                new_param = MaxINIParameter(
                    key=param.key,
                    value=self._changes[param.key],
                    type=param.type,
                    category=param.category,
                    section=param.section,
                    description_ru=param.description_ru,
                    description_en=param.description_en,
                    validation=param.validation,
                    default_value=param.default_value,
                    unit=param.unit
                )
                modified.append(new_param)
        
        return modified
    
    def apply_changes(self) -> Tuple[bool, str]:
        """
        Apply pending changes to INI file.
        
        Returns:
            (success, message): Tuple of success flag and message
        """
        if not self._changes:
            return True, "No changes to apply"
        
        try:
            # Get modified parameters
            modified_params = self.get_modified_params()
            
            # Create backup with error handling
            if self.parser.current_file:
                try:
                    backup_path = self.backup_manager.create_backup(self.parser.current_file)
                    logger.info(f"Backup created: {backup_path}")
                except PermissionError:
                    return False, "Permission denied: Cannot create backup file"
                except OSError as e:
                    return False, f"Backup failed: {str(e)}"
                except Exception as e:
                    logger.warning(f"Backup creation failed: {e}")
                    # Continue without backup if it's not critical
            
            # Save changes with detailed error handling
            try:
                success = self.parser.save(modified_params)
            except FileNotFoundError:
                return False, "INI file not found. It may have been moved or deleted."
            except PermissionError:
                return False, "Permission denied: Cannot write to INI file. Check file permissions."
            except OSError as e:
                return False, f"File system error: {str(e)}"
            except UnicodeEncodeError:
                return False, "Encoding error: Cannot save file with current encoding"
            except Exception as e:
                logger.error(f"Unexpected error during save: {e}")
                return False, f"Unexpected error: {str(e)}"
            
            if success:
                # Show green backgrounds briefly
                self._show_save_success()
                
                # Clear changes
                self._changes.clear()
                self.changes_made.emit(0)
                
                # Emit save signal
                self.save_requested.emit()
                
                msg = f"Saved {len(modified_params)} parameters"
                logger.info(msg)
                return True, msg
            else:
                msg = "Failed to save changes"
                logger.error(msg)
                return False, msg
                
        except Exception as e:
            msg = f"Error saving changes: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def _show_save_success(self) -> None:
        """Show green backgrounds on saved items for 2 seconds."""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            param = item.data(0, Qt.UserRole)
            if param and param.key in self._changes:
                # Set green background
                item.setBackground(1, QColor(200, 255, 200))  # Green
                
                # Fade to white after 2 seconds
                QTimer.singleShot(2000, lambda item=item: item.setBackground(1, QColor(255, 255, 255)))
    
    def revert_changes(self) -> int:
        """
        Discard all pending changes and reload original values.
        
        Returns:
            Number of changes discarded
        """
        count = len(self._changes)
        
        # Clear changes
        self._changes.clear()
        
        # Reload original parameters
        if self._original_params:
            self.load_section(self._current_section, self._original_params)
        
        # Emit changes signal
        self.changes_made.emit(0)
        
        logger.info(f"Reverted {count} changes")
        return count
    
    def refresh_from_file(self) -> Tuple[bool, str]:
        """
        Reload current section from disk (external changes).
        
        Returns:
            (success, message): Tuple of success flag and message
        """
        if self._changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"You have {len(self._changes)} unsaved changes.\n"
                "Discard changes and reload from disk?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return False, "Refresh cancelled"
        
        try:
            # Reload from parser
            if self.parser.current_file:
                params = self.parser.load(self.parser.current_file)
                section_params = [p for p in params if p.section == self._current_section]
                
                if section_params:
                    self.load_section(self._current_section, section_params)
                    return True, "Refreshed from disk"
                else:
                    return False, "Section not found in file"
            else:
                return False, "No file loaded"
                
        except Exception as e:
            msg = f"Error refreshing: {str(e)}"
            logger.error(msg)
            return False, msg
    
    @property
    def section_name(self) -> Optional[str]:
        """Currently displayed section name."""
        return self._current_section
    
    @property
    def has_unsaved_changes(self) -> bool:
        """True if there are pending changes."""
        return len(self._changes) > 0
    
    @property
    def change_count(self) -> int:
        """Number of modified parameters."""
        return len(self._changes)


class INIValueDelegate(QStyledItemDelegate):
    """
    Custom delegate for inline editing of INI parameter values.
    
    Provides type-specific editors for different parameter types.
    """
    
    def createEditor(
        self,
        parent: QWidget,
        option: Any,
        index: QModelIndex
    ) -> QWidget:
        """
        Create appropriate editor for parameter type.
        
        Args:
            parent: Parent widget
            option: Style option
            index: Model index
            
        Returns:
            Appropriate editor widget
        """
        # Get parameter from item data
        item = index.model().itemFromIndex(index)
        if not item:
            return QLineEdit(parent)
        
        param = item.data(Qt.UserRole)
        if not param:
            return QLineEdit(parent)
        
        # Create type-specific editor
        if param.type == ParamType.INT:
            editor = QSpinBox(parent)
            editor.setRange(-2147483648, 2147483647)  # int32 range
            return editor
        
        elif param.type == ParamType.BOOL:
            editor = QComboBox(parent)
            editor.addItems(["0", "1"])
            return editor
        
        elif param.type == ParamType.PATH:
            editor = QLineEdit(parent)
            # TODO: Add browse button for paths
            return editor
        
        else:  # STRING
            editor = QLineEdit(parent)
            return editor
    
    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        """
        Load current value into editor.
        
        Args:
            editor: Editor widget
            index: Model index
        """
        value = index.data(Qt.DisplayRole)
        
        if isinstance(editor, QSpinBox):
            try:
                editor.setValue(int(value))
            except (ValueError, TypeError):
                editor.setValue(0)
        
        elif isinstance(editor, QComboBox):
            editor.setCurrentText(str(value))
        
        else:  # QLineEdit
            editor.setText(str(value))
    
    def setModelData(
        self,
        editor: QWidget,
        model: Any,
        index: QModelIndex
    ) -> None:
        """
        Save edited value to model.
        
        Args:
            editor: Editor widget
            model: Model
            index: Model index
        """
        if isinstance(editor, QSpinBox):
            value = str(editor.value())
        elif isinstance(editor, QComboBox):
            value = editor.currentText()
        else:  # QLineEdit
            value = editor.text()
        
        model.setData(index, value, Qt.EditRole)