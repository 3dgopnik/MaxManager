from __future__ import annotations

from pathlib import Path
import os
from PySide6 import QtWidgets as Q
from PySide6.QtCore import Qt
import json
import re
import tempfile
import traceback

from integrations.project_schema import load_and_resolve
from core.config import Config
from core.logger import get_logger


SAFE_NAME = re.compile(r"^[\w\-\. ]{1,128}$")  # letters, digits, _, -, ., space


class ProjectCreatorDialog(Q.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Project")
        self.setModal(True)
        self.resize(520, 220)

        lay = Q.QVBoxLayout(self)
        grid = Q.QGridLayout()

        self.root_edit = Q.QLineEdit()
        browse_btn = Q.QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_root)

        self.name_edit = Q.QLineEdit()
        self.schema_combo = Q.QComboBox()
        self.schema_combo.addItem("default", str(Path("resources/project_schemas/default.json").resolve()))

        grid.addWidget(Q.QLabel("Root"), 0, 0)
        grid.addWidget(self.root_edit, 0, 1)
        grid.addWidget(browse_btn, 0, 2)
        grid.addWidget(Q.QLabel("Project name"), 1, 0)
        grid.addWidget(self.name_edit, 1, 1, 1, 2)
        grid.addWidget(Q.QLabel("Schema"), 2, 0)
        grid.addWidget(self.schema_combo, 2, 1, 1, 2)

        lay.addLayout(grid)

        btns = Q.QDialogButtonBox(Q.QDialogButtonBox.Ok | Q.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _browse_root(self):
        d = Q.QFileDialog.getExistingDirectory(self, "Select root folder")
        if d:
            self.root_edit.setText(d)

    def get_values(self):
        return Path(self.root_edit.text()), self.name_edit.text().strip(), Path(self.schema_combo.currentData())


aSYNC_METADATA = "project.mm.json"


def _check_root_writable(root: Path) -> bool:
    logger = get_logger(__name__)
    try:
        root.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(root))
        os.close(fd)  # Important on Windows to allow deletion
        tmp = Path(tmp_path)
        tmp.unlink(missing_ok=True)
        logger.debug(f"Root is writable | root={root}")
        return True
    except Exception as ex:
        logger.error(f"Root is not writable | root={root} | error={ex}")
        return False


def create_project(parent=None, config: Config | None = None):
    dlg = ProjectCreatorDialog(parent)
    if dlg.exec() != Q.QDialog.Accepted:
        return

    root, name, schema_path = dlg.get_values()
    if not root or not name:
        Q.QMessageBox.warning(parent, "Create Project", "Root and project name are required")
        return None

    if not SAFE_NAME.match(name):
        Q.QMessageBox.warning(parent, "Create Project", "Project name has invalid characters")
        return None

    if not _check_root_writable(root):
        get_logger(__name__).error(f"Create Project: root not writable | root={root}")
        Q.QMessageBox.critical(parent, "Create Project", f"Root is not writable:\n{root}")
        return None

    target = root / name
    if target.exists():
        resp = Q.QMessageBox.question(parent, "Create Project", f"Folder exists:\n{target}\nUse anyway?")
        if resp != Q.QMessageBox.Yes:
            return None

    try:
        resolved = load_and_resolve(schema_path, target, name)
        for folder in resolved.folders:
            folder.mkdir(parents=True, exist_ok=True)
        # Build project metadata aligned with constitution/spec
        meta = {
            "name": resolved.name,
            "root": str(resolved.root),
            "paths": {k: str(v) for k, v in resolved.paths.items()},
            "schemaVersion": "0.1.0",
            "createdAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "lastScene": None,
            "versions": [],
            "cacheInfo": {
                "enabled": False,
                "cacheRoot": getattr(config, 'cache_root', None) if config else None
            },
            "storageInfo": {
                "nasRoot": getattr(config, 'nas_root', None) if config else None
            }
        }
        (resolved.root / aSYNC_METADATA).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        Q.QMessageBox.information(parent, "Create Project", f"Project created at:\n{resolved.root}")
        # remember in config
        if config:
            config.set_project(str(resolved.root))
        return resolved.root
    except Exception as ex:
        Q.QMessageBox.critical(parent, "Create Project", f"Error:\n{ex}\n\n{traceback.format_exc()}")
        return None
