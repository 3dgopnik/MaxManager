"""
Advanced MaxINI Editor - Полный доступ к настройкам 3ds Max
Version: 1.1.1
Description: Advanced editor with full 3ds Max integration
Author: MaxManager
Created: 2025-10-17
Updated: 2025-10-22
"""

# Fluent Design UI with modern components
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap

# Fluent Widgets for modern UI
try:
    from qfluentwidgets import (
        FluentWindow, NavigationItemPosition, FluentIcon,
        FluentCard, HeaderCard, InfoCard, SimpleCard,
        PrimaryPushButton, PushButton, ToolButton,
        FluentTabWidget, TabBar, TabItem,
        CheckBox, SpinBox, LineEdit, ComboBox, Slider,
        ProgressBar, BodyLabel, TitleLabel, CaptionLabel,
        FluentStyleSheet, Theme, setTheme, isDarkTheme,
        FluentIcon as FIcon
    )
    FLUENT_AVAILABLE = True
    print("✅ Fluent Widgets available")
except ImportError:
    FLUENT_AVAILABLE = False
    print("⚠️ Fluent Widgets not available - using fallback")
    # Fallback imports
    from PySide6.QtWidgets import (
        QTabWidget, QPushButton, QGroupBox,
        QSpinBox, QCheckBox, QLineEdit, QComboBox, QSlider,
        QTextEdit, QProgressBar, QTreeWidget, QTreeWidgetItem, QHeaderView
    )
import sys
import os
import importlib
from typing import Dict, Any, Optional, List

# Hot reload system for development
def hot_reload_modules():
    """Hot reload all MaxManager modules for development."""
    try:
        # Reload all MaxManager modules
        modules_to_reload = [
            'modules.maxini_parser',
            'modules.maxini_backup', 
            'modules.maxini_presets',
            'modules.file_manager',
            'modules.kanban',
            'modules.module_manager',
            'modules.project_creator'
        ]
        
        for module_name in modules_to_reload:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    print(f"✅ Reloaded module: {module_name}")
            except Exception as e:
                print(f"⚠️ Could not reload {module_name}: {e}")
                
    except Exception as e:
        print(f"⚠️ Hot reload failed: {e}")

# Try to import MaxScript API with fallback
try:
    import maxscript
    from pymxs import runtime as rt
    MAXSCRIPT_AVAILABLE = True
    print("✅ MaxScript API available")
except ImportError:
    MAXSCRIPT_AVAILABLE = False
    print("⚠️ MaxScript API not available - using fallback mode")

class AdvancedMaxINIEditor(FluentWindow if FLUENT_AVAILABLE else QMainWindow):
    """Advanced MaxINI Editor with Fluent Design UI."""
    
    VERSION = "1.1.2"
    BUILD_DATE = "2025-10-22"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Hot reload for development
        hot_reload_modules()
        
        self.max_settings = {}
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize Fluent Design interface."""
        self.setWindowTitle(f"Advanced MaxINI Editor v{self.VERSION}")
        self.setGeometry(100, 100, 1400, 900)
        
        if FLUENT_AVAILABLE:
            self.init_fluent_ui()
        else:
            self.init_fallback_ui()
    
    def init_fluent_ui(self):
        """Initialize modern Fluent Design UI with bright accents."""
        # Set Fluent theme with bright accents
        setTheme(Theme.AUTO)
        
        # Apply custom bright styling
        self.apply_bright_styling()
        
        # Create navigation interface
        self.addSubInterface(self.create_security_page(), FIcon.SHIELD, "Security", NavigationItemPosition.TOP)
        self.addSubInterface(self.create_performance_page(), FIcon.SPEED_HIGH, "Performance", NavigationItemPosition.TOP)
        self.addSubInterface(self.create_renderer_page(), FIcon.PALETTE, "Renderer", NavigationItemPosition.TOP)
        self.addSubInterface(self.create_viewport_page(), FIcon.VIEW, "Viewport", NavigationItemPosition.TOP)
        self.addSubInterface(self.create_material_page(), FIcon.BRUSH, "Material Editor", NavigationItemPosition.TOP)
        self.addSubInterface(self.create_system_page(), FIcon.SETTING, "System", NavigationItemPosition.TOP)
        self.addSubInterface(self.create_advanced_page(), FIcon.CODE, "Advanced", NavigationItemPosition.BOTTOM)
        
        # Add status info card
        self.status_card = InfoCard(
            FIcon.INFO if MAXSCRIPT_AVAILABLE else FIcon.WARNING,
            "API Status",
            "MaxScript API Connected" if MAXSCRIPT_AVAILABLE else "MaxScript API Not Available - Fallback Mode",
            self
        )
        self.status_card.setFixedHeight(80)
        
        # Add hot reload button
        self.hot_reload_btn = PrimaryPushButton("Hot Reload", self)
        self.hot_reload_btn.setToolTip("Reload all modules (development)")
        self.hot_reload_btn.clicked.connect(self.hot_reload)
        
        # Add action buttons
        self.refresh_btn = PushButton("Refresh", self)
        self.refresh_btn.clicked.connect(self.load_current_settings)
        
        self.apply_btn = PrimaryPushButton("Apply All", self)
        self.apply_btn.clicked.connect(self.apply_all_settings)
        
        # Set initial page
        self.stackedWidget.setCurrentWidget(self.create_security_page())
    
    def apply_bright_styling(self):
        """Apply bright color accents and modern styling."""
        bright_style = """
        /* Bright accent colors */
        PrimaryPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }
        
        PrimaryPushButton:hover {
            background-color: #106ebe;
        }
        
        PrimaryPushButton:pressed {
            background-color: #005a9e;
        }
        
        /* FluentCard with bright accents */
        FluentCard {
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(0, 120, 212, 0.2);
            border-radius: 8px;
            padding: 16px;
        }
        
        /* HeaderCard with gradient */
        HeaderCard {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0078d4, stop:1 #106ebe);
            color: white;
            border-radius: 8px;
            padding: 16px;
            font-weight: 600;
            font-size: 16px;
        }
        
        /* InfoCard with bright colors */
        InfoCard {
            background-color: rgba(0, 120, 212, 0.1);
            border-left: 4px solid #0078d4;
            border-radius: 6px;
            padding: 12px;
        }
        
        /* SimpleCard with subtle accent */
        SimpleCard {
            background-color: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(0, 120, 212, 0.1);
            border-radius: 6px;
            padding: 12px;
        }
        
        /* TitleLabel with bright color */
        TitleLabel {
            color: #0078d4;
            font-weight: 600;
            font-size: 14px;
        }
        
        /* CheckBox with bright accent */
        CheckBox {
            color: #323130;
            font-weight: 500;
        }
        
        CheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
            border-radius: 3px;
        }
        
        /* SpinBox with bright border */
        SpinBox {
            border: 2px solid rgba(0, 120, 212, 0.3);
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
        }
        
        SpinBox:focus {
            border-color: #0078d4;
        }
        
        /* ComboBox with bright styling */
        ComboBox {
            border: 2px solid rgba(0, 120, 212, 0.3);
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
        }
        
        ComboBox:focus {
            border-color: #0078d4;
        }
        
        /* Navigation with bright accents */
        NavigationWidget {
            background-color: rgba(0, 120, 212, 0.05);
        }
        
        NavigationItem {
            color: #323130;
            font-weight: 500;
        }
        
        NavigationItem:hover {
            background-color: rgba(0, 120, 212, 0.1);
        }
        
        NavigationItem:selected {
            background-color: #0078d4;
            color: white;
        }
        """
        
        # Apply custom stylesheet
        self.setStyleSheet(bright_style)
        
    def init_fallback_ui(self):
        """Initialize fallback UI for compatibility."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Advanced MaxINI Editor v{self.VERSION}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title_label)
        
        # Hot reload button for development
        reload_btn = QPushButton("Hot Reload")
        reload_btn.setToolTip("Reload all modules (development)")
        reload_btn.clicked.connect(self.hot_reload)
        header_layout.addWidget(reload_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # API Status
        if MAXSCRIPT_AVAILABLE:
            status_label = QLabel("MaxScript API Connected")
            status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            status_label = QLabel("MaxScript API Not Available - Fallback Mode")
            status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_security_tab()
        self.create_performance_tab()
        self.create_renderer_tab()
        self.create_viewport_tab()
        self.create_material_editor_tab()
        self.create_system_tab()
        self.create_advanced_tab()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_current_settings)
        button_layout.addWidget(refresh_btn)
        
        apply_btn = QPushButton("Apply All")
        apply_btn.setStyleSheet("background-color: #00aa00; color: white; font-weight: bold;")
        apply_btn.clicked.connect(self.apply_all_settings)
        button_layout.addWidget(apply_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def hot_reload(self):
        """Hot reload all modules."""
        try:
            hot_reload_modules()
            QMessageBox.information(self, "Hot Reload", "All modules reloaded successfully!")
            self.statusBar().showMessage("Modules reloaded")
        except Exception as e:
            QMessageBox.critical(self, "Hot Reload Error", f"Failed to reload modules:\n\n{e}")
    
    def create_security_page(self):
        """Create Security settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_security_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card with bright accent
        header_card = HeaderCard("Security Settings", page)
        layout.addWidget(header_card)
        
        # Security options card
        security_card = FluentCard(page)
        security_layout = QVBoxLayout(security_card)
        security_layout.setSpacing(15)
        
        # Security checkboxes with bright styling
        self.safe_scene_cb = CheckBox("Safe Scene Script Execution")
        self.safe_scene_cb.setToolTip("Enable safe execution of scene scripts")
        security_layout.addWidget(self.safe_scene_cb)
        
        self.python_cb = CheckBox("Allow Embedded Python Execution")
        self.python_cb.setToolTip("Allow Python scripts to run")
        security_layout.addWidget(self.python_cb)
        
        self.maxscript_cb = CheckBox("Allow Embedded MaxScript Execution")
        self.maxscript_cb.setToolTip("Allow MaxScript to run system commands")
        security_layout.addWidget(self.maxscript_cb)
        
        self.dotnet_cb = CheckBox("Allow Embedded .NET Execution")
        self.dotnet_cb.setToolTip("Allow .NET code execution")
        security_layout.addWidget(self.dotnet_cb)
        
        layout.addWidget(security_card)
        layout.addStretch()
        
        return page
    
    def create_security_tab(self):
        """Create Security settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Security Settings
        security_group = QGroupBox("Security Settings")
        security_layout = QVBoxLayout(security_group)
        
        self.safe_scene_cb = QCheckBox("Safe Scene Script Execution")
        self.safe_scene_cb.setToolTip("Enable safe execution of scene scripts")
        security_layout.addWidget(self.safe_scene_cb)
        
        self.python_cb = QCheckBox("Allow Embedded Python Execution")
        self.python_cb.setToolTip("Allow Python scripts to run")
        security_layout.addWidget(self.python_cb)
        
        self.maxscript_cb = QCheckBox("Allow Embedded MaxScript Execution")
        self.maxscript_cb.setToolTip("Allow MaxScript to run system commands")
        security_layout.addWidget(self.maxscript_cb)
        
        self.dotnet_cb = QCheckBox("Allow Embedded .NET Execution")
        self.dotnet_cb.setToolTip("Allow .NET code execution")
        security_layout.addWidget(self.dotnet_cb)
        
        layout.addWidget(security_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Security")
    
    def create_performance_page(self):
        """Create Performance settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_performance_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card
        header_card = HeaderCard("Performance Settings", page)
        layout.addWidget(header_card)
        
        # Performance card with bright accent
        perf_card = FluentCard(page)
        perf_layout = QVBoxLayout(perf_card)
        perf_layout.setSpacing(20)
        
        # Render Threads
        threads_card = SimpleCard(page)
        threads_layout = QVBoxLayout(threads_card)
        threads_layout.addWidget(TitleLabel("Render Threads"))
        self.render_threads_spin = SpinBox()
        self.render_threads_spin.setRange(1, 128)
        self.render_threads_spin.setValue(1)
        self.render_threads_spin.setToolTip("Number of render threads (1-128)")
        threads_layout.addWidget(self.render_threads_spin)
        perf_layout.addWidget(threads_card)
        
        # Memory Pool
        memory_card = SimpleCard(page)
        memory_layout = QVBoxLayout(memory_card)
        memory_layout.addWidget(TitleLabel("Memory Pool (MB)"))
        self.memory_pool_spin = SpinBox()
        self.memory_pool_spin.setRange(128, 8192)
        self.memory_pool_spin.setValue(512)
        self.memory_pool_spin.setToolTip("Memory pool size in MB")
        memory_layout.addWidget(self.memory_pool_spin)
        perf_layout.addWidget(memory_card)
        
        # Dynamic Heap Size
        heap_card = SimpleCard(page)
        heap_layout = QVBoxLayout(heap_card)
        heap_layout.addWidget(TitleLabel("Dynamic Heap Size (MB)"))
        self.heap_size_spin = SpinBox()
        self.heap_size_spin.setRange(1, 1024)
        self.heap_size_spin.setValue(256)
        self.heap_size_spin.setToolTip("Dynamic heap size in MB")
        heap_layout.addWidget(self.heap_size_spin)
        perf_layout.addWidget(heap_card)
        
        layout.addWidget(perf_card)
        layout.addStretch()
        
        return page
    
    def create_performance_tab(self):
        """Create Performance settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance Settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QVBoxLayout(perf_group)
        
        # Render Threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Render Threads:"))
        self.render_threads_spin = QSpinBox()
        self.render_threads_spin.setRange(1, 128)
        self.render_threads_spin.setValue(1)
        self.render_threads_spin.setToolTip("Number of render threads (1-128)")
        threads_layout.addWidget(self.render_threads_spin)
        threads_layout.addStretch()
        perf_layout.addLayout(threads_layout)
        
        # Memory Pool
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Pool (MB):"))
        self.memory_pool_spin = QSpinBox()
        self.memory_pool_spin.setRange(128, 8192)
        self.memory_pool_spin.setValue(512)
        self.memory_pool_spin.setToolTip("Memory pool size in MB")
        memory_layout.addWidget(self.memory_pool_spin)
        memory_layout.addStretch()
        perf_layout.addLayout(memory_layout)
        
        # Dynamic Heap Size
        heap_layout = QHBoxLayout()
        heap_layout.addWidget(QLabel("Dynamic Heap Size (MB):"))
        self.heap_size_spin = QSpinBox()
        self.heap_size_spin.setRange(1, 1024)
        self.heap_size_spin.setValue(256)
        self.heap_size_spin.setToolTip("Dynamic heap size in MB")
        heap_layout.addWidget(self.heap_size_spin)
        heap_layout.addStretch()
        perf_layout.addLayout(heap_layout)
        
        layout.addWidget(perf_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Performance")
    
    def create_renderer_page(self):
        """Create Renderer settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_renderer_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card
        header_card = HeaderCard("Renderer Settings", page)
        layout.addWidget(header_card)
        
        # Renderer card
        render_card = FluentCard(page)
        render_layout = QVBoxLayout(render_card)
        render_layout.setSpacing(20)
        
        # Thread Count
        thread_card = SimpleCard(page)
        thread_layout = QVBoxLayout(thread_card)
        thread_layout.addWidget(TitleLabel("Thread Count"))
        self.thread_count_spin = SpinBox()
        self.thread_count_spin.setRange(-1, 128)
        self.thread_count_spin.setValue(-1)
        self.thread_count_spin.setToolTip("Thread count (-1 = auto)")
        thread_layout.addWidget(self.thread_count_spin)
        render_layout.addWidget(thread_card)
        
        layout.addWidget(render_card)
        layout.addStretch()
        
        return page
    
    def create_renderer_tab(self):
        """Create Renderer settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Renderer Settings
        render_group = QGroupBox("Renderer Settings")
        render_layout = QVBoxLayout(render_group)
        
        # Thread Count
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Thread Count:"))
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(-1, 128)
        self.thread_count_spin.setValue(-1)
        self.thread_count_spin.setToolTip("Thread count (-1 = auto)")
        thread_layout.addWidget(self.thread_count_spin)
        thread_layout.addStretch()
        render_layout.addLayout(thread_layout)
        
        layout.addWidget(render_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Renderer")
    
    def create_viewport_page(self):
        """Create Viewport settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_viewport_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card
        header_card = HeaderCard("Viewport Settings", page)
        layout.addWidget(header_card)
        
        # Viewport card
        viewport_card = FluentCard(page)
        viewport_layout = QVBoxLayout(viewport_card)
        viewport_layout.setSpacing(20)
        
        # Anti-aliasing Quality
        aa_card = SimpleCard(page)
        aa_layout = QVBoxLayout(aa_card)
        aa_layout.addWidget(TitleLabel("Anti-aliasing Quality"))
        self.quality_combo = ComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.quality_combo.setCurrentText("High")
        self.quality_combo.setToolTip("Viewport anti-aliasing quality")
        aa_layout.addWidget(self.quality_combo)
        viewport_layout.addWidget(aa_card)
        
        layout.addWidget(viewport_card)
        layout.addStretch()
        
        return page
    
    def create_viewport_tab(self):
        """Create Viewport settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Viewport Settings
        viewport_group = QGroupBox("Viewport Settings")
        viewport_layout = QVBoxLayout(viewport_group)
        
        # Anti-aliasing Quality
        aa_layout = QHBoxLayout()
        aa_layout.addWidget(QLabel("Anti-aliasing Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.quality_combo.setCurrentText("High")
        self.quality_combo.setToolTip("Viewport anti-aliasing quality")
        aa_layout.addWidget(self.quality_combo)
        aa_layout.addStretch()
        viewport_layout.addLayout(aa_layout)
        
        layout.addWidget(viewport_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Viewport")
    
    def create_material_page(self):
        """Create Material Editor settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_material_editor_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card
        header_card = HeaderCard("Material Editor Settings", page)
        layout.addWidget(header_card)
        
        # Material card
        mat_card = FluentCard(page)
        mat_layout = QVBoxLayout(mat_card)
        mat_layout.setSpacing(20)
        
        # 3D Map Scale
        scale_card = SimpleCard(page)
        scale_layout = QVBoxLayout(scale_card)
        scale_layout.addWidget(TitleLabel("3D Map Scale (meters)"))
        self.map_scale_spin = SpinBox()
        self.map_scale_spin.setRange(1, 1000)
        self.map_scale_spin.setValue(3)
        self.map_scale_spin.setToolTip("3D Map Scale in meters")
        scale_layout.addWidget(self.map_scale_spin)
        mat_layout.addWidget(scale_card)
        
        layout.addWidget(mat_card)
        layout.addStretch()
        
        return page
    
    def create_material_editor_tab(self):
        """Create Material Editor settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Material Editor Settings
        mat_group = QGroupBox("Material Editor Settings")
        mat_layout = QVBoxLayout(mat_group)
        
        # 3D Map Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("3D Map Scale (meters):"))
        self.map_scale_spin = QSpinBox()
        self.map_scale_spin.setRange(1, 1000)
        self.map_scale_spin.setValue(3)
        self.map_scale_spin.setToolTip("3D Map Scale in meters")
        scale_layout.addWidget(self.map_scale_spin)
        scale_layout.addStretch()
        mat_layout.addLayout(scale_layout)
        
        layout.addWidget(mat_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Material Editor")
    
    def create_system_page(self):
        """Create System settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_system_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card
        header_card = HeaderCard("System Settings", page)
        layout.addWidget(header_card)
        
        # System card
        system_card = FluentCard(page)
        system_layout = QVBoxLayout(system_card)
        system_layout.setSpacing(20)
        
        # Undo Levels
        undo_card = SimpleCard(page)
        undo_layout = QVBoxLayout(undo_card)
        undo_layout.addWidget(TitleLabel("Undo Levels"))
        self.undo_levels_spin = SpinBox()
        self.undo_levels_spin.setRange(10, 500)
        self.undo_levels_spin.setValue(200)
        self.undo_levels_spin.setToolTip("Number of undo levels")
        undo_layout.addWidget(self.undo_levels_spin)
        system_layout.addWidget(undo_card)
        
        # Auto Backup
        backup_card = SimpleCard(page)
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.addWidget(TitleLabel("Auto Backup"))
        self.auto_backup_cb = CheckBox("Enable Auto Backup")
        self.auto_backup_cb.setToolTip("Enable automatic backup")
        backup_layout.addWidget(self.auto_backup_cb)
        
        backup_layout.addWidget(TitleLabel("Backup Interval (minutes)"))
        self.backup_interval_spin = SpinBox()
        self.backup_interval_spin.setRange(1, 60)
        self.backup_interval_spin.setValue(15)
        self.backup_interval_spin.setToolTip("Auto backup interval in minutes")
        backup_layout.addWidget(self.backup_interval_spin)
        system_layout.addWidget(backup_card)
        
        layout.addWidget(system_card)
        layout.addStretch()
        
        return page
    
    def create_system_tab(self):
        """Create System settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # System Settings
        system_group = QGroupBox("System Settings")
        system_layout = QVBoxLayout(system_group)
        
        # Undo Levels
        undo_layout = QHBoxLayout()
        undo_layout.addWidget(QLabel("Undo Levels:"))
        self.undo_levels_spin = QSpinBox()
        self.undo_levels_spin.setRange(10, 500)
        self.undo_levels_spin.setValue(200)
        self.undo_levels_spin.setToolTip("Number of undo levels")
        undo_layout.addWidget(self.undo_levels_spin)
        undo_layout.addStretch()
        system_layout.addLayout(undo_layout)
        
        # Auto Backup
        self.auto_backup_cb = QCheckBox("Enable Auto Backup")
        self.auto_backup_cb.setToolTip("Enable automatic backup")
        system_layout.addWidget(self.auto_backup_cb)
        
        # Backup Interval
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Backup Interval (minutes):"))
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 60)
        self.backup_interval_spin.setValue(15)
        self.backup_interval_spin.setToolTip("Auto backup interval in minutes")
        backup_layout.addWidget(self.backup_interval_spin)
        backup_layout.addStretch()
        system_layout.addLayout(backup_layout)
        
        layout.addWidget(system_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "System")
    
    def create_advanced_page(self):
        """Create Advanced settings page with Fluent Design."""
        if not FLUENT_AVAILABLE:
            return self.create_advanced_tab()
            
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header card
        header_card = HeaderCard("Advanced Settings", page)
        layout.addWidget(header_card)
        
        # Advanced card
        advanced_card = FluentCard(page)
        advanced_layout = QVBoxLayout(advanced_card)
        advanced_layout.setSpacing(20)
        
        # API Status
        api_card = InfoCard(
            FIcon.INFO if MAXSCRIPT_AVAILABLE else FIcon.WARNING,
            "API Status",
            "MaxScript API Available" if MAXSCRIPT_AVAILABLE else "MaxScript API Not Available",
            page
        )
        advanced_layout.addWidget(api_card)
        
        # Hot Reload Button
        hot_reload_btn = PrimaryPushButton("Hot Reload Modules", page)
        hot_reload_btn.setToolTip("Reload all MaxManager modules")
        hot_reload_btn.clicked.connect(self.hot_reload)
        advanced_layout.addWidget(hot_reload_btn)
        
        layout.addWidget(advanced_card)
        layout.addStretch()
        
        return page
    
    def create_advanced_tab(self):
        """Create Advanced settings tab (fallback)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Advanced Settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # API Status
        api_label = QLabel("API Status:")
        advanced_layout.addWidget(api_label)
        
        if MAXSCRIPT_AVAILABLE:
            api_status = QLabel("MaxScript API Available")
            api_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            api_status = QLabel("MaxScript API Not Available")
            api_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        advanced_layout.addWidget(api_status)
        
        # Hot Reload Button
        hot_reload_btn = QPushButton("Hot Reload Modules")
        hot_reload_btn.setToolTip("Reload all MaxManager modules")
        hot_reload_btn.clicked.connect(self.hot_reload)
        advanced_layout.addWidget(hot_reload_btn)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_current_settings(self):
        """Load current settings from 3ds Max."""
        try:
            if not MAXSCRIPT_AVAILABLE:
                self.statusBar().showMessage("MaxScript API not available - using default values")
                return
                
            # Load Security settings
            try:
                safe_scene = rt.getIniSetting("Security", "SafeSceneScriptExecutionEnabled")
                self.safe_scene_cb.setChecked(safe_scene == "1")
            except:
                pass
                
            try:
                python_blocked = rt.getIniSetting("Security", "EmbeddedPythonExecutionBlocked")
                self.python_cb.setChecked(python_blocked != "1")
            except:
                pass
                
            try:
                maxscript_blocked = rt.getIniSetting("Security", "EmbeddedMAXScriptSystemCommandsExecutionBlocked")
                self.maxscript_cb.setChecked(maxscript_blocked != "1")
            except:
                pass
                
            try:
                dotnet_blocked = rt.getIniSetting("Security", "EmbeddedDotNetExecutionBlocked")
                self.dotnet_cb.setChecked(dotnet_blocked != "1")
            except:
                pass
            
            # Load Performance settings
            try:
                threads = rt.getIniSetting("Renderer", "ThreadCount")
                if threads:
                    self.render_threads_spin.setValue(int(threads))
            except:
                pass
                
            try:
                memory = rt.getIniSetting("Performance", "MemoryPool")
                if memory:
                    self.memory_pool_spin.setValue(int(memory))
            except:
                pass
                
            try:
                heap = rt.getIniSetting("Performance", "DynamicHeapSize")
                if heap:
                    self.heap_size_spin.setValue(int(heap))
            except:
                pass
            
            # Load System settings
            try:
                undo = rt.getIniSetting("Performance", "UndoLevels")
                if undo:
                    self.undo_levels_spin.setValue(int(undo))
            except:
                pass
                
            try:
                autobackup = rt.getIniSetting("Autobackup", "AutoBackupEnabled")
                self.auto_backup_cb.setChecked(autobackup == "1")
            except:
                pass
                
            try:
                interval = rt.getIniSetting("Autobackup", "AutoBackupInterval")
                if interval:
                    self.backup_interval_spin.setValue(int(interval))
            except:
                pass
            
            self.statusBar().showMessage("Settings loaded successfully")
            
        except Exception as e:
            self.statusBar().showMessage(f"Error loading settings: {e}")
            print(f"Error loading settings: {e}")
    
    def apply_all_settings(self):
        """Apply all settings to 3ds Max."""
        try:
            if not MAXSCRIPT_AVAILABLE:
                QMessageBox.warning(self, "API Error", "MaxScript API not available!\nCannot apply changes to 3ds Max.")
                return
                
            # Apply Security settings
            rt.setIniSetting("Security", "SafeSceneScriptExecutionEnabled", str(int(self.safe_scene_cb.isChecked())))
            rt.setIniSetting("Security", "EmbeddedPythonExecutionBlocked", str(int(not self.python_cb.isChecked())))
            rt.setIniSetting("Security", "EmbeddedMAXScriptSystemCommandsExecutionBlocked", str(int(not self.maxscript_cb.isChecked())))
            rt.setIniSetting("Security", "EmbeddedDotNetExecutionBlocked", str(int(not self.dotnet_cb.isChecked())))
            
            # Apply Performance settings
            rt.setIniSetting("Renderer", "ThreadCount", str(self.render_threads_spin.value()))
            rt.setIniSetting("Performance", "MemoryPool", str(self.memory_pool_spin.value()))
            rt.setIniSetting("Performance", "DynamicHeapSize", str(self.heap_size_spin.value()))
            
            # Apply System settings
            rt.setIniSetting("Performance", "UndoLevels", str(self.undo_levels_spin.value()))
            rt.setIniSetting("Autobackup", "AutoBackupEnabled", str(int(self.auto_backup_cb.isChecked())))
            rt.setIniSetting("Autobackup", "AutoBackupInterval", str(self.backup_interval_spin.value()))
            
            # Force 3ds Max to reload settings
            rt.refreshSystem()
            
            QMessageBox.information(self, "Success", "Settings applied successfully to 3ds Max!")
            self.statusBar().showMessage("All settings applied successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply settings to 3ds Max:\n\n{e}")
            print(f"Error applying settings: {e}")
            self.statusBar().showMessage(f"Error: {e}")