#!/usr/bin/env python3
"""
MaxManager - Cross-platform desktop application for project management
Architecture inspired by Pulze Scene Manager with modern UI design
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.application import MaxManagerApp
from ui.theme_loader import ThemeLoader
from core.config import Config
from core.logger import setup_logging


def main():
    """Main entry point for MaxManager application"""
    # Setup logging
    setup_logging()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MaxManager")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationName("3dgopnik")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Load configuration
    config = Config()

    # Theme setup (runtime theming with qtass if available)
    styles_dir = Path("resources/styles")
    output_dir = Path.home() / ".maxmanager" / "styles_cache"
    ThemeLoader(app).setup(styles_dir, output_dir, style="qt_material", theme="dark_teal")
    
    # Create main application window
    max_manager = MaxManagerApp(config)
    max_manager.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()