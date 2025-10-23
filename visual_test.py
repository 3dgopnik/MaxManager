#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visual test to verify UI changes are visible
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

# Import our components
from src.ui.modern_sidebar import ModernSidebar
from src.ui.modern_header import ModernHeader

class VisualTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Test - UI Changes")
        self.setGeometry(100, 100, 1200, 1000)  # Taller window to see changes
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = ModernSidebar()
        self.sidebar.button_clicked.connect(self.on_sidebar_clicked)
        main_layout.addWidget(self.sidebar)
        
        # Right side
        right_side = QWidget()
        right_layout = QVBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Create header
        self.header = ModernHeader()
        self.header.tab_changed.connect(self.on_header_tab_changed)
        right_layout.addWidget(self.header)
        
        # Content area with info
        self.content = QWidget()
        self.content.setStyleSheet("background-color: #4D4D4D; color: white;")
        content_layout = QVBoxLayout(self.content)
        
        # Add info labels
        info_label = QLabel("Visual Test - Check the following:")
        info_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 10px;")
        content_layout.addWidget(info_label)
        
        info1 = QLabel("1. Sidebar buttons should be 160px tall (not 80px)")
        info1.setStyleSheet("color: yellow; font-size: 14px; padding: 5px;")
        content_layout.addWidget(info1)
        
        info2 = QLabel("2. Header tabs should be at 40px from top (bottom of logo button)")
        info2.setStyleSheet("color: yellow; font-size: 14px; padding: 5px;")
        content_layout.addWidget(info2)
        
        info3 = QLabel("3. Click sidebar buttons to see contextual header tabs")
        info3.setStyleSheet("color: cyan; font-size: 14px; padding: 5px;")
        content_layout.addWidget(info3)
        
        content_layout.addStretch()
        right_layout.addWidget(self.content)
        
        main_layout.addWidget(right_side)
        
        # Set stretch factors
        main_layout.setStretch(0, 0)  # sidebar fixed
        main_layout.setStretch(1, 1)  # content stretches
        
        # Initialize with ini context
        self.on_sidebar_clicked('ini')
        
    def on_sidebar_clicked(self, button_name):
        print(f"Sidebar clicked: {button_name}")
        if hasattr(self.sidebar, 'buttons_data'):
            tabs = self.sidebar.buttons_data.get(button_name, {}).get('tabs', [])
            if tabs:
                self.header.set_context(button_name, tabs)

    def on_header_tab_changed(self, context, tab_name):
        print(f"Header tab: {context} / {tab_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VisualTestWindow()
    window.show()
    sys.exit(app.exec())
