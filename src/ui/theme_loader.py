from __future__ import annotations

from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets as Q

try:
    # Qt Advanced Stylesheets (Python port)
    from qtass_pyside6 import QtAdvancedStylesheet  # type: ignore
    QTASS_AVAILABLE = True
except Exception:  # pragma: no cover
    QtAdvancedStylesheet = None  # type: ignore
    QTASS_AVAILABLE = False


class ThemeLoader:
    def __init__(self, app: Q.QApplication):
        self.app = app
        self.manager: Optional[QtAdvancedStylesheet] = None

    def setup(self, styles_dir: Path, output_dir: Path, style: str = "qt_material", theme: str = "dark_teal") -> None:
        styles_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        if QTASS_AVAILABLE:
            self.manager = QtAdvancedStylesheet()
            self.manager.setStylesDirPath(str(styles_dir))
            self.manager.setOutputDirPath(str(output_dir))
            self.manager.setCurrentStyle(style)
            self.manager.setCurrentTheme(theme)
            self.app.setStyleSheet(self.manager.styleSheet())
        else:
            # fallback: apply plain QSS if exists
            qss = styles_dir / "fallback.qss"
            if qss.exists():
                self.app.setStyleSheet(qss.read_text(encoding="utf-8"))

    def switch_theme(self, theme: str) -> None:
        if self.manager:
            self.manager.setCurrentTheme(theme)
            self.app.setStyleSheet(self.manager.styleSheet())

    def set_accent(self, color_name: str) -> None:
        if self.manager:
            self.manager.setThemeColor("accentColor", color_name)
            self.app.setStyleSheet(self.manager.styleSheet())
