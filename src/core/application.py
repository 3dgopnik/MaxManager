"""
Main application class for MaxManager
Handles window management, modules, and core functionality
"""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence
from typing import Dict, Any, Optional
import logging

from core.config import Config
from core.logger import get_logger
try:
    from ui.main_window import MainWindow
except Exception:
    from ui.simple_mvp import SimpleMvpWindow as MainWindow
from modules.module_manager import ModuleManager


class MaxManagerApp(QMainWindow):
    """
    Main application class that orchestrates all components
    """
    
    # Signals
    project_changed = Signal(str)  # project_path
    scene_changed = Signal(str)    # scene_path
    
    def __init__(self, config: Config):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.config = config
        self.module_manager = ModuleManager(self)
        
        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        self._connect_signals()
        
        self.logger.info("MaxManager application initialized")
    
    def _setup_ui(self):
        """Setup main UI components"""
        self.setWindowTitle("MaxManager v0.0.1")
        self.setMinimumSize(1200, 800)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Initialize main window components
        self.main_window = MainWindow(self)
        self.splitter.addWidget(self.main_window)
        
        # Sizes will be set after sidebar/details are introduced
    
    def _setup_menu(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = QAction("&New Project", self)
        new_project_action.setShortcut(QKeySequence.New)
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("&Open Project", self)
        open_project_action.setShortcut(QKeySequence.Open)
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Module visibility toggles
        for module_name in self.module_manager.get_available_modules():
            toggle_action = QAction(f"Show {module_name}", self)
            toggle_action.setCheckable(True)
            toggle_action.setChecked(True)
            toggle_action.triggered.connect(
                lambda checked, name=module_name: self.toggle_module(name, checked)
            )
            view_menu.addAction(toggle_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Add permanent widgets
        self.project_label = self.status_bar.addPermanentWidget(
            QWidget()  # Will be replaced with proper widget
        )
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.project_changed.connect(self._on_project_changed)
        self.scene_changed.connect(self._on_scene_changed)
    
    def new_project(self):
        """Create new project"""
        self.logger.info("Creating new project...")
        # TODO: Implement project creation dialog
        pass
    
    def open_project(self):
        """Open existing project"""
        self.logger.info("Opening project...")
        # TODO: Implement project opening dialog
        pass
    
    def toggle_module(self, module_name: str, visible: bool):
        """Toggle module visibility"""
        self.logger.info(f"Toggling module {module_name}: {visible}")
        self.module_manager.toggle_module(module_name, visible)
    
    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About MaxManager", 
                         "MaxManager v0.0.1\n"
                         "Cross-platform project management for 3D artists\n"
                         "Inspired by Pulze Scene Manager")
    
    def _on_project_changed(self, project_path: str):
        """Handle project change"""
        self.logger.info(f"Project changed to: {project_path}")
        self.status_bar.showMessage(f"Project: {project_path}")
    
    def _on_scene_changed(self, scene_path: str):
        """Handle scene change"""
        self.logger.info(f"Scene changed to: {scene_path}")
        # Update scene-specific UI components
    
    def closeEvent(self, event):
        """Handle application close"""
        self.logger.info("MaxManager application closing...")
        self.module_manager.cleanup()
        event.accept()