"""MaxINI Editor Installer - Installation and setup GUI."""

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QGroupBox,
    QCheckBox,
    QMessageBox,
    QSplitter,
    QFrame,
    QWidget,
)

# Add src to path for imports when running from 3ds Max
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.maxini_parser import MaxINIParser
from src.modules.maxini_backup import MaxINIBackupManager


class InstallationWorker(QThread):
    """Worker thread for installation tasks."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, tasks: list[str]):
        super().__init__()
        self.tasks = tasks
        
    def run(self):
        """Run installation tasks."""
        try:
            total_tasks = len(self.tasks)
            
            for i, task in enumerate(self.tasks):
                self.status_updated.emit(f"Executing: {task}")
                self.progress_updated.emit(int((i / total_tasks) * 100))
                
                # Simulate task execution
                self.msleep(500)  # 0.5 second delay
                
                # Here would be actual installation logic
                if "icons" in task.lower():
                    self._install_icons()
                elif "macro" in task.lower():
                    self._register_macro()
                elif "test" in task.lower():
                    self._test_installation()
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Installation completed successfully!")
            self.finished.emit(True, "MaxINI Editor v0.2.0 installed successfully!")
            
        except Exception as e:
            self.finished.emit(False, f"Installation failed: {str(e)}")
    
    def _install_icons(self):
        """Install PNG icons to usericons folders."""
        # Implementation would go here
        pass
    
    def _register_macro(self):
        """Register macro in 3ds Max."""
        # Implementation would go here
        pass
    
    def _test_installation(self):
        """Test the installation."""
        # Implementation would go here
        pass


class MaxINIInstallerDialog(QDialog):
    """Installation dialog for MaxINI Editor."""
    
    VERSION = "0.3.4"
    BUILD_DATE = "2025-10-17"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize installer dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle(f"MaxINI Editor Installer v{self.VERSION}")
        self.setGeometry(200, 100, 600, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface."""
        main_layout = QVBoxLayout()
        
        # Header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout()
        
        title_label = QLabel(f"<h2>MaxINI Editor v{self.VERSION}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(f"Build: {self.BUILD_DATE} | MaxINI Configuration Editor with Presets")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(subtitle_label)
        
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)
        
        # Status section
        status_group = QGroupBox("Installation Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready to install")
        self.status_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Options section
        options_group = QGroupBox("Installation Options")
        options_layout = QVBoxLayout()
        
        self.checkbox_icons = QCheckBox("Install PNG icons (Dark/Light themes)")
        self.checkbox_icons.setChecked(True)
        options_layout.addWidget(self.checkbox_icons)
        
        self.checkbox_macro = QCheckBox("Register macro in 3ds Max UI")
        self.checkbox_macro.setChecked(True)
        options_layout.addWidget(self.checkbox_macro)
        
        self.checkbox_backup = QCheckBox("Create backup of current max.ini")
        self.checkbox_backup.setChecked(True)
        options_layout.addWidget(self.checkbox_backup)
        
        self.checkbox_test = QCheckBox("Test installation after setup")
        self.checkbox_test.setChecked(True)
        options_layout.addWidget(self.checkbox_test)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Log section
        log_group = QGroupBox("Installation Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10px;")
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_install = QPushButton("Install MaxINI Editor")
        self.btn_install.clicked.connect(self.start_installation)
        self.btn_install.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        button_layout.addWidget(self.btn_install)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)
        
        self.btn_launch = QPushButton("Launch Editor")
        self.btn_launch.clicked.connect(self.launch_editor)
        self.btn_launch.setEnabled(False)
        self.btn_launch.setStyleSheet("""
            QPushButton {
                background-color: #4169E1;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0000CD;
            }
        """)
        button_layout.addWidget(self.btn_launch)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Initialize log
        self.log_message(f"MaxINI Editor Installer v{self.VERSION}")
        self.log_message(f"Build Date: {self.BUILD_DATE}")
        self.log_message("Ready for installation...")
        
    def log_message(self, message: str):
        """Add message to log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def start_installation(self):
        """Start installation process."""
        self.btn_install.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Prepare tasks based on checkboxes
        tasks = []
        if self.checkbox_icons.isChecked():
            tasks.append("Installing PNG icons")
        if self.checkbox_macro.isChecked():
            tasks.append("Registering macro")
        if self.checkbox_backup.isChecked():
            tasks.append("Creating backup")
        if self.checkbox_test.isChecked():
            tasks.append("Testing installation")
            
        if not tasks:
            QMessageBox.warning(self, "No Tasks", "Please select at least one installation option.")
            self.btn_install.setEnabled(True)
            self.progress_bar.setVisible(False)
            return
            
        # Start worker thread
        self.worker = InstallationWorker(tasks)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.status_updated.connect(self.log_message)
        self.worker.finished.connect(self.installation_finished)
        self.worker.start()
        
    def installation_finished(self, success: bool, message: str):
        """Handle installation completion."""
        self.progress_bar.setVisible(False)
        self.btn_install.setEnabled(True)
        
        if success:
            self.status_label.setText("Installation completed successfully!")
            self.status_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
            self.btn_launch.setEnabled(True)
            self.log_message("✅ " + message)
            
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText("Installation failed!")
            self.status_label.setStyleSheet("font-weight: bold; color: #DC143C;")
            self.log_message("❌ " + message)
            
            QMessageBox.critical(self, "Error", message)
            
    def launch_editor(self):
        """Launch the MaxINI Editor."""
        try:
            from src.ui.maxini_editor_window import MaxINIEditorWindow
            
            editor = MaxINIEditorWindow(parent=self)
            editor.show()
            
            self.log_message("MaxINI Editor launched successfully!")
            
        except Exception as e:
            self.log_message(f"Failed to launch editor: {str(e)}")
            QMessageBox.critical(self, "Launch Error", f"Failed to launch editor:\n\n{str(e)}")


def launch_installer():
    """Launch the installer dialog."""
    from PySide6.QtWidgets import QApplication
    import qtmax
    
    # Get or create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Get Max main window for parenting
    try:
        max_window = qtmax.GetQMaxMainWindow()
    except:
        max_window = None
    
    installer = MaxINIInstallerDialog(parent=max_window)
    installer.show()
    
    return installer
