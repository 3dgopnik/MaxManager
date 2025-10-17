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

"""
Module manager for MaxManager
Handles loading, initialization, and lifecycle of application modules
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal

from core.logger import get_logger


class BaseModule(QObject):
    """
    Base class for all MaxManager modules
    """
    
    # Signals
    module_ready = Signal()
    module_error = Signal(str)  # error_message
    
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.logger = get_logger(f"module.{name}")
        self.name = name
        self.is_initialized = False
        self.is_enabled = True
        self.widget = None
    
    def initialize(self) -> bool:
        """
        Initialize the module
        
        Returns:
            True if initialization successful, False otherwise
        """
        raise NotImplementedError("initialize must be implemented in subclass")
    
    def get_widget(self) -> Optional[QWidget]:
        """
        Get the main widget for this module
        
        Returns:
            Module widget or None if not available
        """
        raise NotImplementedError("get_widget must be implemented in subclass")
    
    def cleanup(self) -> None:
        """
        Cleanup module resources
        """
        raise NotImplementedError("cleanup must be implemented in subclass")
    
    def enable(self) -> None:
        """Enable the module"""
        self.is_enabled = True
        self.logger.info(f"Module {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the module"""
        self.is_enabled = False
        self.logger.info(f"Module {self.name} disabled")


class ModuleManager:
    """
    Manages all application modules
    """
    
    def __init__(self, app_instance):
        self.logger = get_logger(__name__)
        self.app = app_instance
        self.modules: Dict[str, BaseModule] = {}
        self.module_widgets: Dict[str, QWidget] = {}
        
        self._register_default_modules()
    
    def _register_default_modules(self) -> None:
        """Register default modules"""
        try:
            from .file_manager import FileManagerModule
            from .kanban import KanbanModule
            from .gantt import GanttModule
            from .openai_agent import OpenAIAgentModule
            
            self.register_module(FileManagerModule("file_manager"))
            self.register_module(KanbanModule("kanban"))
            self.register_module(GanttModule("gantt"))
            self.register_module(OpenAIAgentModule("openai_agent"))
            
        except ImportError as e:
            self.logger.warning(f"Could not import some modules: {e}")
    
    def register_module(self, module: BaseModule) -> bool:
        """
        Register a new module
        
        Args:
            module: Module instance to register
            
        Returns:
            True if registration successful
        """
        try:
            self.modules[module.name] = module
            self.logger.info(f"Registered module: {module.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register module {module.name}: {e}")
            return False
    
    def initialize_module(self, module_name: str) -> bool:
        """
        Initialize a specific module
        
        Args:
            module_name: Name of module to initialize
            
        Returns:
            True if initialization successful
        """
        if module_name not in self.modules:
            self.logger.error(f"Module {module_name} not found")
            return False
        
        module = self.modules[module_name]
        
        try:
            if module.initialize():
                module.is_initialized = True
                self.module_widgets[module_name] = module.get_widget()
                self.logger.info(f"Module {module_name} initialized successfully")
                return True
            else:
                self.logger.error(f"Module {module_name} initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing module {module_name}: {e}")
            return False
    
    def initialize_all_modules(self) -> None:
        """Initialize all registered modules"""
        for module_name in self.modules:
            self.initialize_module(module_name)
    
    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Get module by name
        
        Args:
            module_name: Name of module
            
        Returns:
            Module instance or None if not found
        """
        return self.modules.get(module_name)
    
    def get_module_widget(self, module_name: str) -> Optional[QWidget]:
        """
        Get module widget by name
        
        Args:
            module_name: Name of module
            
        Returns:
            Module widget or None if not found
        """
        return self.module_widgets.get(module_name)
    
    def toggle_module(self, module_name: str, visible: bool) -> None:
        """
        Toggle module visibility
        
        Args:
            module_name: Name of module
            visible: Whether module should be visible
        """
        module = self.get_module(module_name)
        if module:
            if visible:
                module.enable()
            else:
                module.disable()
    
    def get_available_modules(self) -> List[str]:
        """
        Get list of available module names
        
        Returns:
            List of module names
        """
        return list(self.modules.keys())
    
    def get_enabled_modules(self) -> List[str]:
        """
        Get list of enabled module names
        
        Returns:
            List of enabled module names
        """
        return [name for name, module in self.modules.items() if module.is_enabled]
    
    def cleanup(self) -> None:
        """Cleanup all modules"""
        for module in self.modules.values():
            try:
                module.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up module {module.name}: {e}")
        
        self.logger.info("All modules cleaned up")