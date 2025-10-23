#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaxManager Test - точная копия интерфейса для 3ds Max
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

# Import our components
from src.ui.modern_sidebar import ModernSidebar
from src.ui.modern_header import ModernHeader

class MaxManagerTestWindow(QMainWindow):
    """Точная копия MaxManager для тестирования."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaxManager Test - 3ds Max Interface")
        # Flexible size: minimum for current buttons, can expand for more buttons
        # Height: header 80px + content area (sidebar buttons will expand vertically)
        # Width: sidebar 80px + expand space 80px = 160px + content area
        self.setGeometry(100, 100, 1200, 800)  # Flexible size for more buttons
        
        # Apply MaxManager styling
        self.apply_maxmanager_styling()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main HORIZONTAL layout (sidebar on left, content on right)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar (full height, from top to bottom)
        self.sidebar = ModernSidebar()
        self.sidebar.button_clicked.connect(self.on_sidebar_clicked)
        main_layout.addWidget(self.sidebar)
        
        # Right side: header + content
        right_side = QWidget()
        right_layout = QVBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Create contextual header
        # Header with version
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        # Header tabs
        self.header = ModernHeader()
        self.header.tab_changed.connect(self.on_header_tab_changed)
        header_layout.addWidget(self.header)
        
        # Version label in top right corner
                version_label = QLabel("v1.8.0")
        version_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 4px 8px;
                border: none;
                font-size: 10px;
                font-weight: bold;
                margin-top: -40px;
            }
        """)
        version_label.setFixedSize(60, 80)
        version_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(version_label)
        
        right_layout.addWidget(header_widget)
        
        # Main content area (без дублирования вкладок!)
        self.content = QWidget()
        self.content.setStyleSheet("background-color: #4D4D4D; color: white;")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        
        # Create content widgets
        self.content_stack = {}
        self.create_content_widgets()
        
        # Add current content to layout
        content_layout.addWidget(self.content_widget)
        
        right_layout.addWidget(self.content)
        main_layout.addWidget(right_side)
        
        # CRITICAL: Set stretch factors (как в реальном MaxManager)
        main_layout.setStretch(0, 0)  # sidebar fixed width
        main_layout.setStretch(1, 1)  # content stretches
        
        # Status bar (как в реальном MaxManager)
        self.statusBar().showMessage("Ready - MaxManager Test Mode")
        
        # Initialize with ini context (как в реальном MaxManager)
        self.on_sidebar_clicked('ini')
        
    def create_content_widgets(self):
        """Create content widgets for each context/tab combination."""
        
        # Security content
        security_widget = QWidget()
        security_layout = QVBoxLayout(security_widget)
        security_layout.addWidget(QLabel("Security Settings"))
        security_layout.addWidget(QLabel("• File Access Control"))
        security_layout.addWidget(QLabel("• Script Execution Policy"))
        security_layout.addWidget(QLabel("• Network Security"))
        security_layout.addStretch()
        self.content_stack[('ini', 'Security')] = security_widget
        
        # Performance content
        performance_widget = QWidget()
        performance_layout = QVBoxLayout(performance_widget)
        performance_layout.addWidget(QLabel("Performance Settings"))
        performance_layout.addWidget(QLabel("• Render Threads: 4"))
        performance_layout.addWidget(QLabel("• Memory Pool: 1024 MB"))
        performance_layout.addWidget(QLabel("• Dynamic Heap: 512 MB"))
        performance_layout.addStretch()
        self.content_stack[('ini', 'Performance')] = performance_widget
        
        # Renderer content
        renderer_widget = QWidget()
        renderer_layout = QVBoxLayout(renderer_widget)
        renderer_layout.addWidget(QLabel("Renderer Settings"))
        renderer_layout.addWidget(QLabel("• Default Renderer: Arnold"))
        renderer_layout.addWidget(QLabel("• GPU Acceleration: Enabled"))
        renderer_layout.addWidget(QLabel("• Ray Tracing: Hardware"))
        renderer_layout.addStretch()
        self.content_stack[('ini', 'Renderer')] = renderer_widget
        
        # Viewport content
        viewport_widget = QWidget()
        viewport_layout = QVBoxLayout(viewport_widget)
        viewport_layout.addWidget(QLabel("Viewport Settings"))
        viewport_layout.addWidget(QLabel("• Display Mode: Realistic"))
        viewport_layout.addWidget(QLabel("• Shadows: Enabled"))
        viewport_layout.addWidget(QLabel("• Anti-aliasing: 4x"))
        viewport_layout.addStretch()
        self.content_stack[('ini', 'Viewport')] = viewport_widget
        
        # Settings content
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.addWidget(QLabel("General Settings"))
        settings_layout.addWidget(QLabel("• Auto-save: Every 10 minutes"))
        settings_layout.addWidget(QLabel("• Undo Levels: 50"))
        settings_layout.addWidget(QLabel("• Language: English"))
        settings_layout.addStretch()
        self.content_stack[('ini', 'Settings')] = settings_widget
        
        # UI content for ui context
        ui_widget = QWidget()
        ui_layout = QVBoxLayout(ui_widget)
        ui_layout.addWidget(QLabel("UI Settings"))
        ui_layout.addWidget(QLabel("• Interface Theme: Dark"))
        ui_layout.addWidget(QLabel("• Color Scheme: Professional"))
        ui_layout.addWidget(QLabel("• Layout: Modern"))
        ui_layout.addStretch()
        self.content_stack[('ui', 'Interface')] = ui_widget
        
        # Set initial content
        self.content_widget = security_widget
        
    def switch_content(self, context, tab_name):
        """Switch content widget based on context and tab."""
        key = (context, tab_name)
        if key in self.content_stack:
            # Remove current content
            current_layout = self.content.layout()
            if current_layout.count() > 0:
                current_layout.removeWidget(self.content_widget)
                self.content_widget.hide()
            
            # Add new content
            self.content_widget = self.content_stack[key]
            current_layout.addWidget(self.content_widget)
            self.content_widget.show()
            
    def on_sidebar_clicked(self, button_name):
        """Handle sidebar button clicks - switch header context (как в реальном MaxManager)."""
        print(f"Sidebar clicked: {button_name}")
        
        # Get tabs for this context from sidebar
        if hasattr(self.sidebar, 'buttons_data'):
            tabs = self.sidebar.buttons_data.get(button_name, {}).get('tabs', [])
            
            # Switch header context
            if hasattr(self, 'header') and tabs:
                self.header.set_context(button_name, tabs)
            
            # Update status bar
            self.statusBar().showMessage(f"Category: {button_name}")
    
    def on_header_tab_changed(self, context, tab_name):
        """Handle header tab changes - switch content (как в реальном MaxManager)."""
        print(f"Header tab: {context} / {tab_name}")
        self.statusBar().showMessage(f"{context}: {tab_name}")
        
        # Switch content based on context + tab combination
        self.switch_content(context, tab_name)
    
    def apply_maxmanager_styling(self):
        """Apply MaxManager styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D2D;
                color: white;
            }
            QStatusBar {
                background-color: #333333;
                color: white;
                border-top: 1px solid #555555;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties like MaxManager
    app.setApplicationName("MaxManager Test")
    app.setApplicationVersion("1.1.6")
    
    window = MaxManagerTestWindow()
    window.show()
    
    print("MaxManager Test launched!")
    print("This should look exactly like the real MaxManager interface in 3ds Max")
    print("No duplicate tabs - only ModernHeader navigation!")
    
    sys.exit(app.exec())