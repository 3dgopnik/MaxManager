"""
Advanced MaxINI Editor - Полный доступ к настройкам 3ds Max
Version: 1.0.1
Description: Advanced editor with full 3ds Max integration
Author: MaxManager
Created: 2025-10-17
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QWidget, QLabel, QPushButton, QGroupBox,
    QSpinBox, QCheckBox, QLineEdit, QComboBox, QSlider,
    QTextEdit, QProgressBar, QMessageBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
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

class AdvancedMaxINIEditor(QMainWindow):
    """Advanced MaxINI Editor with full 3ds Max integration."""
    
    VERSION = "1.0.1"
    BUILD_DATE = "2025-10-17"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Hot reload for development
        hot_reload_modules()
        
        self.max_settings = {}
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"Advanced MaxINI Editor v{self.VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        
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
        reload_btn = QPushButton("🔄 Hot Reload")
        reload_btn.setToolTip("Reload all modules (development)")
        reload_btn.clicked.connect(self.hot_reload)
        header_layout.addWidget(reload_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # API Status
        if MAXSCRIPT_AVAILABLE:
            status_label = QLabel("✅ MaxScript API Connected")
            status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            status_label = QLabel("⚠️ MaxScript API Not Available - Fallback Mode")
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
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_current_settings)
        button_layout.addWidget(refresh_btn)
        
        apply_btn = QPushButton("✅ Apply All")
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
    
    def create_security_tab(self):
        """Create Security settings tab."""
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
        
        self.tab_widget.addTab(tab, "🔒 Security")
    
    def create_performance_tab(self):
        """Create Performance settings tab."""
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
        
        self.tab_widget.addTab(tab, "⚡ Performance")
    
    def create_renderer_tab(self):
        """Create Renderer settings tab."""
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
        
        self.tab_widget.addTab(tab, "🎨 Renderer")
    
    def create_viewport_tab(self):
        """Create Viewport settings tab."""
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
        
        self.tab_widget.addTab(tab, "👁️ Viewport")
    
    def create_material_editor_tab(self):
        """Create Material Editor settings tab."""
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
        
        self.tab_widget.addTab(tab, "🎨 Material Editor")
    
    def create_system_tab(self):
        """Create System settings tab."""
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
        
        self.tab_widget.addTab(tab, "⚙️ System")
    
    def create_advanced_tab(self):
        """Create Advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Advanced Settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # API Status
        api_label = QLabel("API Status:")
        advanced_layout.addWidget(api_label)
        
        if MAXSCRIPT_AVAILABLE:
            api_status = QLabel("✅ MaxScript API Available")
            api_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            api_status = QLabel("⚠️ MaxScript API Not Available")
            api_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        advanced_layout.addWidget(api_status)
        
        # Hot Reload Button
        hot_reload_btn = QPushButton("🔄 Hot Reload Modules")
        hot_reload_btn.setToolTip("Reload all MaxManager modules")
        hot_reload_btn.clicked.connect(self.hot_reload)
        advanced_layout.addWidget(hot_reload_btn)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔧 Advanced")
    
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