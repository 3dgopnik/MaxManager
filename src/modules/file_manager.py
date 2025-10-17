"""
File Manager Module for MaxManager
Handles project files, scenes, and asset management
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon

from .module_manager import BaseModule
from ..core.logger import get_logger


class FileManagerWidget(QWidget):
    """
    File Manager UI Widget
    """
    
    # Signals
    file_selected = Signal(str)  # file_path
    file_double_clicked = Signal(str)  # file_path
    folder_expanded = Signal(str)  # folder_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(f"{__name__}.widget")
        self.current_path = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup file manager UI"""
        layout = QVBoxLayout(self)
        
        # File tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Type", "Size", "Modified"])
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(self.tree_widget)
        
        # Set initial directory
        self.set_path(Path.home())
    
    def set_path(self, path: Path) -> None:
        """Set current directory path"""
        self.current_path = path
        self._populate_tree()
    
    def _populate_tree(self) -> None:
        """Populate tree widget with directory contents"""
        if not self.current_path or not self.current_path.exists():
            return
        
        self.tree_widget.clear()
        
        try:
            # Add parent directory item
            if self.current_path.parent != self.current_path:
                parent_item = QTreeWidgetItem(["..", "Folder", "", ""])
                parent_item.setData(0, Qt.UserRole, self.current_path.parent)
                self.tree_widget.addTopLevelItem(parent_item)
            
            # Add current directory contents
            for item in sorted(self.current_path.iterdir()):
                if item.is_dir():
                    self._add_folder_item(item)
                else:
                    self._add_file_item(item)
        
        except PermissionError:
            self.logger.warning(f"Permission denied accessing {self.current_path}")
        except Exception as e:
            self.logger.error(f"Error populating tree: {e}")
    
    def _add_folder_item(self, folder_path: Path) -> None:
        """Add folder item to tree"""
        item = QTreeWidgetItem([
            folder_path.name,
            "Folder",
            "",
            folder_path.stat().st_mtime if folder_path.exists() else ""
        ])
        item.setData(0, Qt.UserRole, folder_path)
        item.setIcon(0, QIcon(":/icons/folder.png"))  # Will be replaced with proper icon
        self.tree_widget.addTopLevelItem(item)
    
    def _add_file_item(self, file_path: Path) -> None:
        """Add file item to tree"""
        try:
            stat = file_path.stat()
            size = self._format_size(stat.st_size)
            modified = self._format_date(stat.st_mtime)
            
            # Determine file type
            file_type = self._get_file_type(file_path)
            
            item = QTreeWidgetItem([
                file_path.name,
                file_type,
                size,
                modified
            ])
            item.setData(0, Qt.UserRole, file_path)
            item.setIcon(0, self._get_file_icon(file_path))
            self.tree_widget.addTopLevelItem(item)
            
        except Exception as e:
            self.logger.warning(f"Could not add file {file_path}: {e}")
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type based on extension"""
        ext = file_path.suffix.lower()
        
        type_map = {
            '.max': '3ds Max Scene',
            '.ma': 'Maya Scene',
            '.mb': 'Maya Binary',
            '.blend': 'Blender Scene',
            '.fbx': 'FBX Model',
            '.obj': 'OBJ Model',
            '.psd': 'Photoshop',
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.png': 'Image',
            '.exr': 'EXR Image',
            '.hdr': 'HDR Image',
            '.mp4': 'Video',
            '.avi': 'Video',
            '.mov': 'Video'
        }
        
        return type_map.get(ext, 'File')
    
    def _get_file_icon(self, file_path: Path) -> QIcon:
        """Get icon for file type"""
        # TODO: Implement proper icon system
        return QIcon()
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _format_date(self, timestamp: float) -> str:
        """Format modification date"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.file_selected.emit(str(path))
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item double click"""
        path = item.data(0, Qt.UserRole)
        if path:
            if path.is_dir():
                self.set_path(path)
                self.folder_expanded.emit(str(path))
            else:
                self.file_double_clicked.emit(str(path))


class FileManagerModule(BaseModule):
    """
    File Manager Module
    """
    
    def __init__(self, name: str = "file_manager"):
        super().__init__(name)
        self.widget = None
    
    def initialize(self) -> bool:
        """Initialize file manager module"""
        try:
            self.widget = FileManagerWidget()
            self.logger.info("File Manager module initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize File Manager: {e}")
            return False
    
    def get_widget(self) -> Optional[QWidget]:
        """Get file manager widget"""
        return self.widget
    
    def cleanup(self) -> None:
        """Cleanup file manager module"""
        if self.widget:
            self.widget = None
        self.logger.info("File Manager module cleaned up")