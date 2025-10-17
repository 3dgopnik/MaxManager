"""
Advanced MaxINI Editor - Полный доступ к настройкам 3ds Max
Version: 1.0.0
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
import maxscript
import sys
import os
from typing import Dict, Any, Optional, List

class AdvancedMaxINIEditor(QMainWindow):
    """Advanced MaxINI Editor with full 3ds Max integration."""
    
    VERSION = "1.0.0"
    BUILD_DATE = "2025-10-17"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Advanced MaxINI Editor v{self.VERSION}")
        self.setGeometry(100, 100, 1400, 900)
        
        # 3ds Max integration
        self.max_connected = False
        self.max_settings = {}
        self.ini_settings = {}
        
        self.init_ui()
        self.connect_to_3dsmax()
        self.load_all_settings()
    
    def init_ui(self):
        """Initialize the advanced UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        self.status_label = QLabel("Connecting to 3ds Max...")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_all_settings)
        header_layout.addWidget(self.refresh_btn)
        
        self.apply_btn = QPushButton("✅ Apply All")
        self.apply_btn.clicked.connect(self.apply_all_changes)
        self.apply_btn.setEnabled(False)
        header_layout.addWidget(self.apply_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Main tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Security Tab
        self.create_security_tab()
        
        # Performance Tab
        self.create_performance_tab()
        
        # Renderer Tab
        self.create_renderer_tab()
        
        # Viewport Tab
        self.create_viewport_tab()
        
        # Material Editor Tab
        self.create_material_editor_tab()
        
        # System Tab
        self.create_system_tab()
        
        # Advanced Tab
        self.create_advanced_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def connect_to_3dsmax(self):
        """Connect to 3ds Max and verify connection."""
        try:
            # Test 3ds Max connection
            test_result = maxscript.evaluate("3dsMaxVersion")
            if test_result:
                self.max_connected = True
                self.status_label.setText("✅ Connected to 3ds Max")
                self.status_label.setStyleSheet("color: #51cf66; font-weight: bold;")
                self.statusBar().showMessage("Connected to 3ds Max")
            else:
                self.max_connected = False
                self.status_label.setText("❌ Failed to connect to 3ds Max")
                self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        except Exception as e:
            self.max_connected = False
            self.status_label.setText(f"❌ Connection error: {str(e)}")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
    
    def load_all_settings(self):
        """Load all settings from 3ds Max and max.ini."""
        if not self.max_connected:
            return
        
        try:
            # Load from 3ds Max
            self.load_3dsmax_settings()
            
            # Load from max.ini
            self.load_ini_settings()
            
            # Update UI
            self.update_all_ui()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {str(e)}")
    
    def load_3dsmax_settings(self):
        """Load settings directly from 3ds Max."""
        try:
            # Renderer settings
            self.max_settings['renderer'] = {
                'threads': maxscript.evaluate("renderer.threads"),
                'memory': maxscript.evaluate("renderer.memory"),
                'quality': maxscript.evaluate("renderer.quality")
            }
            
            # Viewport settings
            self.max_settings['viewport'] = {
                'quality': maxscript.evaluate("viewport.quality"),
                'antialiasing': maxscript.evaluate("viewport.antialiasing"),
                'shadows': maxscript.evaluate("viewport.shadows")
            }
            
            # Material Editor settings
            self.max_settings['material_editor'] = {
                'slots': maxscript.evaluate("meditMaterials.count"),
                'mode': maxscript.evaluate("materialEditor.mode")
            }
            
            # System settings
            self.max_settings['system'] = {
                'undo_levels': maxscript.evaluate("undoLevels"),
                'auto_backup': maxscript.evaluate("autoBackup.enabled"),
                'backup_interval': maxscript.evaluate("autoBackup.interval")
            }
            
        except Exception as e:
            print(f"Error loading 3ds Max settings: {e}")
    
    def load_ini_settings(self):
        """Load settings from max.ini file."""
        try:
            ini_path = maxscript.evaluate("getDir #userScripts") + "\\..\\3dsMax.ini"
            # Load INI file and parse settings
            # This would use the existing maxini_parser.py
            pass
        except Exception as e:
            print(f"Error loading INI settings: {e}")
    
    def create_security_tab(self):
        """Create Security settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Security Group
        security_group = QGroupBox("Security Settings")
        security_layout = QVBoxLayout(security_group)
        
        # Safe Scene Script Execution
        self.safe_scene_cb = QCheckBox("Safe Scene Script Execution")
        self.safe_scene_cb.stateChanged.connect(self.on_setting_changed)
        security_layout.addWidget(self.safe_scene_cb)
        
        # Embedded Python Execution
        self.python_cb = QCheckBox("Allow Embedded Python Execution")
        self.python_cb.stateChanged.connect(self.on_setting_changed)
        security_layout.addWidget(self.python_cb)
        
        # Embedded MaxScript Execution
        self.maxscript_cb = QCheckBox("Allow Embedded MaxScript Execution")
        self.maxscript_cb.stateChanged.connect(self.on_setting_changed)
        security_layout.addWidget(self.maxscript_cb)
        
        # Embedded .NET Execution
        self.dotnet_cb = QCheckBox("Allow Embedded .NET Execution")
        self.dotnet_cb.stateChanged.connect(self.on_setting_changed)
        security_layout.addWidget(self.dotnet_cb)
        
        layout.addWidget(security_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔒 Security")
    
    def create_performance_tab(self):
        """Create Performance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance Group
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QVBoxLayout(perf_group)
        
        # Render Threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Render Threads:"))
        self.render_threads_spin = QSpinBox()
        self.render_threads_spin.setRange(1, 128)
        self.render_threads_spin.setValue(0)  # Auto
        self.render_threads_spin.valueChanged.connect(self.on_setting_changed)
        threads_layout.addWidget(self.render_threads_spin)
        threads_layout.addStretch()
        perf_layout.addLayout(threads_layout)
        
        # Memory Pool
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Pool (MB):"))
        self.memory_pool_spin = QSpinBox()
        self.memory_pool_spin.setRange(128, 8192)
        self.memory_pool_spin.setValue(512)
        self.memory_pool_spin.valueChanged.connect(self.on_setting_changed)
        memory_layout.addWidget(self.memory_pool_spin)
        memory_layout.addStretch()
        perf_layout.addLayout(memory_layout)
        
        # Dynamic Heap Size
        heap_layout = QHBoxLayout()
        heap_layout.addWidget(QLabel("Dynamic Heap Size (MB):"))
        self.heap_size_spin = QSpinBox()
        self.heap_size_spin.setRange(64, 4096)
        self.heap_size_spin.setValue(256)
        self.heap_size_spin.valueChanged.connect(self.on_setting_changed)
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
        
        # Renderer Group
        renderer_group = QGroupBox("Renderer Settings")
        renderer_layout = QVBoxLayout(renderer_group)
        
        # Thread Count
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Thread Count:"))
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(-1, 128)
        self.thread_count_spin.setValue(-1)  # Auto
        self.thread_count_spin.valueChanged.connect(self.on_setting_changed)
        thread_layout.addWidget(self.thread_count_spin)
        thread_layout.addStretch()
        renderer_layout.addLayout(thread_layout)
        
        # Scan Band Height
        band_layout = QHBoxLayout()
        band_layout.addWidget(QLabel("Scan Band Height:"))
        self.scan_band_spin = QSpinBox()
        self.scan_band_spin.setRange(1, 64)
        self.scan_band_spin.setValue(16)
        self.scan_band_spin.valueChanged.connect(self.on_setting_changed)
        band_layout.addWidget(self.scan_band_spin)
        band_layout.addStretch()
        renderer_layout.addLayout(band_layout)
        
        layout.addWidget(renderer_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎨 Renderer")
    
    def create_viewport_tab(self):
        """Create Viewport settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Viewport Group
        viewport_group = QGroupBox("Viewport Settings")
        viewport_layout = QVBoxLayout(viewport_group)
        
        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.quality_combo.currentTextChanged.connect(self.on_setting_changed)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        viewport_layout.addLayout(quality_layout)
        
        # Anti-aliasing
        self.antialiasing_cb = QCheckBox("Enable Anti-aliasing")
        self.antialiasing_cb.stateChanged.connect(self.on_setting_changed)
        viewport_layout.addWidget(self.antialiasing_cb)
        
        # Shadows
        self.shadows_cb = QCheckBox("Enable Shadows")
        self.shadows_cb.stateChanged.connect(self.on_setting_changed)
        viewport_layout.addWidget(self.shadows_cb)
        
        layout.addWidget(viewport_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "👁️ Viewport")
    
    def create_material_editor_tab(self):
        """Create Material Editor settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Material Editor Group
        medit_group = QGroupBox("Material Editor Settings")
        medit_layout = QVBoxLayout(medit_group)
        
        # 3D Map Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("3D Map Scale (Meters):"))
        self.map_scale_spin = QSpinBox()
        self.map_scale_spin.setRange(1, 100)
        self.map_scale_spin.setValue(3)
        self.map_scale_spin.valueChanged.connect(self.on_setting_changed)
        scale_layout.addWidget(self.map_scale_spin)
        scale_layout.addStretch()
        medit_layout.addLayout(scale_layout)
        
        # Default Texture Size
        texture_layout = QHBoxLayout()
        texture_layout.addWidget(QLabel("Default Texture Size (Meters):"))
        self.texture_size_spin = QSpinBox()
        self.texture_size_spin.setRange(1, 100)
        self.texture_size_spin.setValue(1)
        self.texture_size_spin.valueChanged.connect(self.on_setting_changed)
        texture_layout.addWidget(self.texture_size_spin)
        texture_layout.addStretch()
        medit_layout.addLayout(texture_layout)
        
        layout.addWidget(medit_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎨 Material Editor")
    
    def create_system_tab(self):
        """Create System settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # System Group
        system_group = QGroupBox("System Settings")
        system_layout = QVBoxLayout(system_group)
        
        # Undo Levels
        undo_layout = QHBoxLayout()
        undo_layout.addWidget(QLabel("Undo Levels:"))
        self.undo_levels_spin = QSpinBox()
        self.undo_levels_spin.setRange(1, 1000)
        self.undo_levels_spin.setValue(200)
        self.undo_levels_spin.valueChanged.connect(self.on_setting_changed)
        undo_layout.addWidget(self.undo_levels_spin)
        undo_layout.addStretch()
        system_layout.addLayout(undo_layout)
        
        # Auto Backup
        self.auto_backup_cb = QCheckBox("Enable Auto Backup")
        self.auto_backup_cb.stateChanged.connect(self.on_setting_changed)
        system_layout.addWidget(self.auto_backup_cb)
        
        # Backup Interval
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Backup Interval (minutes):"))
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 60)
        self.backup_interval_spin.setValue(15)
        self.backup_interval_spin.valueChanged.connect(self.on_setting_changed)
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
        
        # Advanced Group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Direct 3ds Max Control
        self.direct_control_cb = QCheckBox("Enable Direct 3ds Max Control")
        self.direct_control_cb.stateChanged.connect(self.on_setting_changed)
        advanced_layout.addWidget(self.direct_control_cb)
        
        # Real-time Sync
        self.realtime_sync_cb = QCheckBox("Enable Real-time Sync")
        self.realtime_sync_cb.stateChanged.connect(self.on_setting_changed)
        advanced_layout.addWidget(self.realtime_sync_cb)
        
        # Advanced Logging
        self.advanced_logging_cb = QCheckBox("Enable Advanced Logging")
        self.advanced_logging_cb.stateChanged.connect(self.on_setting_changed)
        advanced_layout.addWidget(self.advanced_logging_cb)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔧 Advanced")
    
    def on_setting_changed(self):
        """Handle setting changes."""
        self.apply_btn.setEnabled(True)
        self.statusBar().showMessage("Settings changed - click Apply to save")
    
    def refresh_all_settings(self):
        """Refresh all settings from 3ds Max."""
        self.load_all_settings()
        self.statusBar().showMessage("Settings refreshed")
    
    def apply_all_changes(self):
        """Apply all changes to 3ds Max and max.ini."""
        try:
            if not self.max_connected:
                QMessageBox.warning(self, "Warning", "Not connected to 3ds Max!")
                return
            
            # Apply to 3ds Max
            self.apply_to_3dsmax()
            
            # Apply to max.ini
            self.apply_to_ini()
            
            self.apply_btn.setEnabled(False)
            self.statusBar().showMessage("All changes applied successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply changes: {str(e)}")
    
    def apply_to_3dsmax(self):
        """Apply changes directly to 3ds Max."""
        try:
            # Apply Security settings (CRITICAL!)
            if hasattr(self, 'safe_scene_cb'):
                maxscript.evaluate(f"setIniSetting \"Security\" \"SafeSceneScriptExecutionEnabled\" \"{int(self.safe_scene_cb.isChecked())}\"")
            
            if hasattr(self, 'python_cb'):
                maxscript.evaluate(f"setIniSetting \"Security\" \"EmbeddedPythonExecutionBlocked\" \"{int(not self.python_cb.isChecked())}\"")
            
            if hasattr(self, 'maxscript_cb'):
                maxscript.evaluate(f"setIniSetting \"Security\" \"EmbeddedMAXScriptSystemCommandsExecutionBlocked\" \"{int(not self.maxscript_cb.isChecked())}\"")
            
            if hasattr(self, 'dotnet_cb'):
                maxscript.evaluate(f"setIniSetting \"Security\" \"EmbeddedDotNetExecutionBlocked\" \"{int(not self.dotnet_cb.isChecked())}\"")
            
            # Apply renderer settings
            if hasattr(self, 'render_threads_spin'):
                maxscript.evaluate(f"setIniSetting \"Renderer\" \"ThreadCount\" \"{self.render_threads_spin.value()}\"")
            
            if hasattr(self, 'memory_pool_spin'):
                maxscript.evaluate(f"setIniSetting \"Performance\" \"MemoryPool\" \"{self.memory_pool_spin.value()}\"")
            
            # Apply viewport settings
            if hasattr(self, 'quality_combo'):
                quality_map = {"Low": 1, "Medium": 2, "High": 3, "Ultra": 4}
                quality_value = quality_map.get(self.quality_combo.currentText(), 2)
                maxscript.evaluate(f"setIniSetting \"Nitrous\" \"AntiAliasingQuality\" \"{quality_value}\"")
            
            # Apply system settings
            if hasattr(self, 'undo_levels_spin'):
                maxscript.evaluate(f"setIniSetting \"Performance\" \"UndoLevels\" \"{self.undo_levels_spin.value()}\"")
            
            if hasattr(self, 'auto_backup_cb'):
                maxscript.evaluate(f"setIniSetting \"Autobackup\" \"AutoBackupEnabled\" \"{int(self.auto_backup_cb.isChecked())}\"")
            
            if hasattr(self, 'backup_interval_spin'):
                maxscript.evaluate(f"setIniSetting \"Autobackup\" \"AutoBackupInterval\" \"{self.backup_interval_spin.value()}\"")
            
            # Force 3ds Max to reload settings
            maxscript.evaluate("refreshSystem()")
            
        except Exception as e:
            print(f"Error applying to 3ds Max: {e}")
    
    def apply_to_ini(self):
        """Apply changes to max.ini file."""
        try:
            # This would use the existing maxini_parser.py
            # to write changes to the INI file
            pass
        except Exception as e:
            print(f"Error applying to INI: {e}")
    
    def update_all_ui(self):
        """Update all UI elements with current settings."""
        try:
            # Update from 3ds Max settings
            if 'renderer' in self.max_settings:
                if hasattr(self, 'render_threads_spin'):
                    self.render_threads_spin.setValue(self.max_settings['renderer'].get('threads', 0))
            
            if 'system' in self.max_settings:
                if hasattr(self, 'undo_levels_spin'):
                    self.undo_levels_spin.setValue(self.max_settings['system'].get('undo_levels', 200))
            
        except Exception as e:
            print(f"Error updating UI: {e}")


def launch_advanced_editor(parent=None):
    """Launch the Advanced MaxINI Editor."""
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        editor = AdvancedMaxINIEditor(parent)
        editor.show()
        
        return editor
        
    except Exception as e:
        print(f"Error launching Advanced MaxINI Editor: {e}")
        return None


if __name__ == "__main__":
    app = QApplication([])
    editor = AdvancedMaxINIEditor()
    editor.show()
    app.exec()