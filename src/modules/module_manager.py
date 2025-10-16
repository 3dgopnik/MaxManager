from __future__ import annotations

from typing import List
from core.logger import get_logger


class ModuleManager:
    """Minimal stub for module orchestration."""

    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
        self._available: List[str] = ["file_manager"]

    def get_available_modules(self) -> List[str]:
        return list(self._available)

    def toggle_module(self, module_name: str, visible: bool) -> None:
        self.logger.info(f"toggle_module: {module_name} -> {visible}")

    def cleanup(self) -> None:
        self.logger.info("ModuleManager cleanup")
