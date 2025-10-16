from __future__ import annotations

from PySide6 import QtWidgets as Q
from PySide6.QtCore import Qt

from modules.project_creator import create_project
from core.config import Config


class SimpleMvpWindow(Q.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = Q.QVBoxLayout(self)
        self.btn_create = Q.QPushButton("Create Project")
        # Pass shared config instance if available via parent chain
        self._config = getattr(parent, 'config', None)
        self.btn_create.clicked.connect(lambda: create_project(self, self._config))
        lay.addWidget(self.btn_create)
        lay.addStretch(1)
