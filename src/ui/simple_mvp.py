from __future__ import annotations

from PySide6 import QtWidgets as Q
from PySide6.QtCore import Qt

from modules.project_creator import create_project
from core.config import Config


class SimpleMvpWindow(Q.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = getattr(parent, 'config', None)

        # Root layout: sidebar (left) + main (right)
        root = Q.QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Sidebar
        sidebar_wrap = Q.QWidget(self)
        sidebar = Q.QVBoxLayout(sidebar_wrap)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(6)

        header = Q.QHBoxLayout()
        lbl = Q.QLabel("Projects", sidebar_wrap)
        lbl.setStyleSheet("font-weight: 600;")
        self.btn_create = Q.QPushButton("Create Project", sidebar_wrap)
        self.btn_create.setCursor(Qt.PointingHandCursor)
        self.btn_create.clicked.connect(self._on_create_project)
        header.addWidget(lbl)
        header.addStretch(1)
        header.addWidget(self.btn_create)
        sidebar.addLayout(header)

        self.list_projects = Q.QListWidget(sidebar_wrap)
        self.list_projects.setSelectionMode(Q.QAbstractItemView.SingleSelection)
        sidebar.addWidget(self.list_projects, 1)

        # Main area placeholder
        main_wrap = Q.QWidget(self)
        main = Q.QVBoxLayout(main_wrap)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(6)
        main.addWidget(Q.QLabel("File structure will appear here", main_wrap))
        main.addStretch(1)

        root.addWidget(sidebar_wrap, 1)
        root.addWidget(main_wrap, 3)

        self._refresh_projects()

    def _on_create_project(self) -> None:
        create_project(self, self._config)
        self._refresh_projects()

    def _refresh_projects(self) -> None:
        self.list_projects.clear()
        if not self._config:
            return
        for p in (self._config.recent_projects or [])[:50]:
            self.list_projects.addItem(str(p))
