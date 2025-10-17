"""
Configuration management for MaxManager
Handles settings, preferences, and application state
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from .logger import get_logger


class UserRole(Enum):
    """User role enumeration"""
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class Theme(Enum):
    """UI theme enumeration"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class UIConfig:
    """UI configuration settings"""
    theme: Theme = Theme.AUTO
    window_width: int = 1200
    window_height: int = 800
    sidebar_width: int = 300
    details_width: int = 300
    show_sidebar: bool = True
    show_details: bool = True
    glassmorphism_enabled: bool = True
    animations_enabled: bool = True


@dataclass
class ModuleConfig:
    """Module-specific configuration"""
    file_manager_enabled: bool = True
    kanban_enabled: bool = True
    gantt_enabled: bool = True
    openai_agent_enabled: bool = False
    integrations_enabled: bool = True


@dataclass
class IntegrationConfig:
    """Integration settings"""
    maxscript_enabled: bool = True
    photoshop_enabled: bool = True
    blender_api_enabled: bool = False
    revit_api_enabled: bool = False
    unreal_api_enabled: bool = False


class Config:
    """
    Main configuration manager
    Handles loading, saving, and accessing application settings
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        # Default config path
        if config_path is None:
            config_dir = Path.home() / ".maxmanager"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        
        # Initialize default configuration
        self.ui = UIConfig()
        self.modules = ModuleConfig()
        self.integrations = IntegrationConfig()
        self.user_role = UserRole.USER
        self.current_project = None
        self.recent_projects = []
        # Storage and performance related settings
        self.nas_root: Optional[str] = None  # e.g. v:\\work\\ or \\\\nas-3d\\Visual\\work\\
        self.cache_root: Optional[str] = None  # local SSD cache path
        self.versions_to_keep: int = 5  # default version retention
        
        # Load existing configuration
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            self.logger.info("No existing config found, using defaults")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load UI config
            if 'ui' in data:
                ui_data = data['ui']
                self.ui = UIConfig(
                    theme=Theme(ui_data.get('theme', 'auto')),
                    window_width=ui_data.get('window_width', 1200),
                    window_height=ui_data.get('window_height', 800),
                    sidebar_width=ui_data.get('sidebar_width', 300),
                    details_width=ui_data.get('details_width', 300),
                    show_sidebar=ui_data.get('show_sidebar', True),
                    show_details=ui_data.get('show_details', True),
                    glassmorphism_enabled=ui_data.get('glassmorphism_enabled', True),
                    animations_enabled=ui_data.get('animations_enabled', True)
                )
            
            # Load module config
            if 'modules' in data:
                module_data = data['modules']
                self.modules = ModuleConfig(
                    file_manager_enabled=module_data.get('file_manager_enabled', True),
                    kanban_enabled=module_data.get('kanban_enabled', True),
                    gantt_enabled=module_data.get('gantt_enabled', True),
                    openai_agent_enabled=module_data.get('openai_agent_enabled', False),
                    integrations_enabled=module_data.get('integrations_enabled', True)
                )
            
            # Load integration config
            if 'integrations' in data:
                int_data = data['integrations']
                self.integrations = IntegrationConfig(
                    maxscript_enabled=int_data.get('maxscript_enabled', True),
                    photoshop_enabled=int_data.get('photoshop_enabled', True),
                    blender_api_enabled=int_data.get('blender_api_enabled', False),
                    revit_api_enabled=int_data.get('revit_api_enabled', False),
                    unreal_api_enabled=int_data.get('unreal_api_enabled', False)
                )
            
            # Load other settings
            if 'user_role' in data:
                self.user_role = UserRole(data['user_role'])
            
            if 'current_project' in data:
                self.current_project = data['current_project']
            
            if 'recent_projects' in data:
                self.recent_projects = data['recent_projects']

            # Storage settings
            self.nas_root = data.get('nas_root')
            self.cache_root = data.get('cache_root')
            self.versions_to_keep = int(data.get('versions_to_keep', 5))
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            # Serialize dataclasses and enums to JSON-safe values
            ui_dict = asdict(self.ui)
            # Ensure enum is saved as value
            ui_dict['theme'] = self.ui.theme.value if isinstance(self.ui.theme, Theme) else self.ui.theme

            data = {
                'ui': ui_dict,
                'modules': asdict(self.modules),
                'integrations': asdict(self.integrations),
                'user_role': self.user_role.value,
                'current_project': self.current_project,
                'recent_projects': self.recent_projects,
                'nas_root': self.nas_root,
                'cache_root': self.cache_root,
                'versions_to_keep': self.versions_to_keep
            }
            
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuration saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def set_project(self, project_path: str) -> None:
        """Set current project and update recent projects"""
        self.current_project = project_path
        
        # Add to recent projects (avoid duplicates)
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        self.recent_projects.insert(0, project_path)
        
        # Keep only last 10 projects
        self.recent_projects = self.recent_projects[:10]
        
        self.save()
    
    def get_module_visibility(self, module_name: str) -> bool:
        """Get module visibility based on user role"""
        # Admin sees everything
        if self.user_role == UserRole.ADMIN:
            return True
        
        # Manager sees most things
        if self.user_role == UserRole.MANAGER:
            return module_name != 'admin_settings'
        
        # User sees basic modules only
        user_modules = ['file_manager', 'kanban', 'gantt']
        return module_name in user_modules