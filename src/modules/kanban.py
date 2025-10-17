"""
Kanban Module for MaxManager
Task management with drag-and-drop boards
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag, QPainter, QColor

from .module_manager import BaseModule
from ..core.logger import get_logger


@dataclass
class Task:
    """Task data structure"""
    id: str
    title: str
    description: str
    status: str  # "todo", "doing", "done"
    assignee: Optional[str] = None
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class TaskListWidget(QListWidget):
    """
    Custom list widget for tasks with drag-and-drop support
    """
    
    # Signals
    task_moved = Signal(str, str, int)  # task_id, new_status, position
    
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.status = status
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasFormat("application/x-task"):
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move event"""
        if event.mimeData().hasFormat("application/x-task"):
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasFormat("application/x-task"):
            task_id = event.mimeData().data("application/x-task").data().decode()
            item = self.itemAt(event.pos())
            
            if item:
                position = self.row(item)
            else:
                position = self.count()
            
            self.task_moved.emit(task_id, self.status, position)
            event.accept()
        else:
            event.ignore()
    
    def startDrag(self, supportedActions):
        """Handle start drag event"""
        item = self.currentItem()
        if not item:
            return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData("application/x-task", item.data(Qt.UserRole).encode())
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = self.itemWidget(item).grab()
        drag.setPixmap(pixmap)
        
        drag.exec_(Qt.MoveAction)


class TaskItemWidget(QWidget):
    """
    Individual task item widget
    """
    
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup task item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Task title
        title_label = QLabel(self.task.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Task description
        if self.task.description:
            desc_label = QLabel(self.task.description)
            desc_label.setStyleSheet("color: #666; font-size: 12px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Task metadata
        meta_layout = QHBoxLayout()
        
        # Priority indicator
        priority_colors = {
            "low": "#4CAF50",
            "medium": "#FF9800", 
            "high": "#F44336",
            "urgent": "#9C27B0"
        }
        priority_color = priority_colors.get(self.task.priority, "#666")
        
        priority_label = QLabel("●")
        priority_label.setStyleSheet(f"color: {priority_color}; font-size: 16px;")
        meta_layout.addWidget(priority_label)
        
        meta_layout.addStretch()
        
        # Assignee
        if self.task.assignee:
            assignee_label = QLabel(f"👤 {self.task.assignee}")
            assignee_label.setStyleSheet("font-size: 11px; color: #666;")
            meta_layout.addWidget(assignee_label)
        
        layout.addLayout(meta_layout)
        
        # Set background color based on priority
        bg_color = priority_colors.get(self.task.priority, "#f5f5f5")
        self.setStyleSheet(f"""
            TaskItemWidget {{
                background-color: {bg_color}20;
                border: 1px solid {bg_color}40;
                border-radius: 8px;
                margin: 2px;
            }}
            TaskItemWidget:hover {{
                background-color: {bg_color}30;
            }}
        """)


class KanbanWidget(QWidget):
    """
    Main Kanban board widget
    """
    
    # Signals
    task_created = Signal(Task)
    task_updated = Signal(Task)
    task_deleted = Signal(str)  # task_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(f"{__name__}.widget")
        self.tasks: Dict[str, Task] = {}
        self._setup_ui()
        self._create_sample_tasks()
    
    def _setup_ui(self):
        """Setup Kanban UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        
        # Create columns for each status
        statuses = [
            ("todo", "To Do", "#FF5722"),
            ("doing", "Doing", "#2196F3"),
            ("done", "Done", "#4CAF50")
        ]
        
        self.task_lists = {}
        
        for status, title, color in statuses:
            column_widget = self._create_column(status, title, color)
            layout.addWidget(column_widget)
    
    def _create_column(self, status: str, title: str, color: str) -> QWidget:
        """Create a Kanban column"""
        column = QWidget()
        column.setMaximumWidth(300)
        column.setMinimumWidth(250)
        
        layout = QVBoxLayout(column)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Column header
        header = QLabel(title)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }}
        """)
        layout.addWidget(header)
        
        # Task list
        task_list = TaskListWidget(status)
        task_list.task_moved.connect(self._on_task_moved)
        self.task_lists[status] = task_list
        layout.addWidget(task_list)
        
        # Add task button
        add_button = QPushButton("+ Add Task")
        add_button.clicked.connect(lambda: self._add_task(status))
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 12px;
                color: #666;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
        """)
        layout.addWidget(add_button)
        
        return column
    
    def _create_sample_tasks(self):
        """Create sample tasks for demonstration"""
        sample_tasks = [
            Task("1", "Setup project structure", "Create basic folder structure", "todo", priority="high"),
            Task("2", "Design UI mockups", "Create wireframes and mockups", "todo", priority="medium"),
            Task("3", "Implement file manager", "Build file browser widget", "doing", priority="high", assignee="Alex"),
            Task("4", "Setup database", "Configure project database", "done", priority="low")
        ]
        
        for task in sample_tasks:
            self.add_task(task)
    
    def add_task(self, task: Task) -> None:
        """Add task to Kanban board"""
        self.tasks[task.id] = task
        self._update_task_display(task)
        self.task_created.emit(task)
    
    def _update_task_display(self, task: Task) -> None:
        """Update task display in appropriate column"""
        # Remove from all lists first
        for task_list in self.task_lists.values():
            for i in range(task_list.count()):
                item = task_list.item(i)
                if item and item.data(Qt.UserRole) == task.id:
                    task_list.takeItem(i)
                    break
        
        # Add to appropriate list
        task_list = self.task_lists[task.status]
        item = QListWidgetItem()
        item.setData(Qt.UserRole, task.id)
        item.setSizeHint(task_item.sizeHint())
        
        task_item = TaskItemWidget(task)
        task_list.addItem(item)
        task_list.setItemWidget(item, task_item)
    
    def _on_task_moved(self, task_id: str, new_status: str, position: int) -> None:
        """Handle task moved between columns"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = new_status
            task.updated_at = datetime.now()
            
            self._update_task_display(task)
            self.task_updated.emit(task)
    
    def _add_task(self, status: str) -> None:
        """Add new task"""
        from PySide6.QtWidgets import QInputDialog
        
        title, ok = QInputDialog.getText(self, "New Task", "Task title:")
        if ok and title:
            task_id = str(len(self.tasks) + 1)
            task = Task(
                id=task_id,
                title=title,
                description="",
                status=status,
                priority="medium"
            )
            self.add_task(task)


class KanbanModule(BaseModule):
    """
    Kanban Module
    """
    
    def __init__(self, name: str = "kanban"):
        super().__init__(name)
        self.widget = None
    
    def initialize(self) -> bool:
        """Initialize Kanban module"""
        try:
            self.widget = KanbanWidget()
            self.logger.info("Kanban module initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Kanban: {e}")
            return False
    
    def get_widget(self) -> Optional[QWidget]:
        """Get Kanban widget"""
        return self.widget
    
    def cleanup(self) -> None:
        """Cleanup Kanban module"""
        if self.widget:
            self.widget = None
        self.logger.info("Kanban module cleaned up")