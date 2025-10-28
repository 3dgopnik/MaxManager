"""
INI Manager for MaxManager.

Manages INI file loading, editing, and saving with UI integration.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .maxini_parser import MaxINIParser, MaxINIParameter
from .maxini_backup import MaxINIBackupManager


@dataclass
class INISection:
    """Represents a section in INI file."""
    name: str
    parameters: Dict[str, str]  # key: value (as strings for UI)
    

class INIManager:
    """
    Manager for INI file operations.
    
    Handles:
    - Loading INI files
    - Tracking modifications
    - Saving changes with backup
    - Grouping parameters by section
    """
    
    def __init__(self, ini_path: Path):
        """Initialize INI manager."""
        self.ini_path = ini_path
        self.parser = MaxINIParser()
        self.backup_manager = MaxINIBackupManager(ini_path.parent / "backups")
        
        # Original data from file
        self.original_parameters: List[MaxINIParameter] = []
        self.original_sections: Dict[str, INISection] = {}
        
        # Current modified data (as strings for UI)
        self.current_sections: Dict[str, INISection] = {}
        
        # Track modifications
        self.modified_params: set[str] = set()  # Set of "section.key" strings
        
    def load_ini(self) -> bool:
        """
        Load INI file and parse into sections.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load with parser
            self.original_parameters = self.parser.load(self.ini_path)
            
            # Group by section
            self.original_sections = {}
            for param in self.original_parameters:
                if param.section not in self.original_sections:
                    self.original_sections[param.section] = INISection(
                        name=param.section,
                        parameters={}
                    )
                
                # Convert value to string for UI
                if isinstance(param.value, bool):
                    str_value = "1" if param.value else "0"
                elif isinstance(param.value, Path):
                    str_value = str(param.value)
                else:
                    str_value = str(param.value)
                    
                self.original_sections[param.section].parameters[param.key] = str_value
            
            # Copy to current (working copy)
            self.current_sections = {
                section_name: INISection(
                    name=section.name,
                    parameters=section.parameters.copy()
                )
                for section_name, section in self.original_sections.items()
            }
            
            return True
            
        except Exception as e:
            print(f"Error loading INI: {e}")
            return False
    
    def get_sections_for_category(self, category: str) -> List[str]:
        """
        Get section names for a specific category/tab.
        
        Args:
            category: Category name (e.g., 'Security', 'Performance')
            
        Returns:
            List of section names matching this category
        """
        # Map categories to section name patterns
        category_mapping = {
            'Security': ['Security', 'SecurityTools', 'SecurityMessages'],
            'Performance': ['Performance', 'Renderer', 'Nitrous', 'OpenImageIO'],
            'Renderer': ['Renderer', 'Gamma', 'NormalBump', 'RenderPresets', 'RenderOutput', 
                        'RenderProgress', 'RenderMessage', 'RenderVFB'],
            'Viewport': ['Selection', 'ObjectSnap', 'Nitrous', 'WindowState'],
            'Settings': ['Directories', 'Paths', 'Autobackup', 'FileList', 'MAXScript',
                        'CommandPanel', 'Modstack', 'CuiConfiguration'],
            'Interface': ['Material Editor', 'Materials', 'MtlEditor', 'LayerManager'],
            'Colors': ['CuiConfiguration'],
            'Layout': ['WindowState', 'Window Position Restore'],
            'Startup': ['MAXScript', 'Plugins', 'PluginSettings'],
            'Hotkeys': ['CuiConfiguration'],
            'Menus': ['CuiConfiguration'],
            'Toolbars': ['CuiConfiguration'],
            'Templates': ['Directories'],
            'Paths': ['Directories', 'Paths', 'BitmapDirs', 'XReferenceDirs'],
            'Structure': ['Directories'],
            'Presets': ['RenderPresets', 'ModifierSets', 'Utility Sets'],
        }
        
        # Get patterns for this category
        patterns = category_mapping.get(category, [])
        
        # Filter sections
        matching_sections = []
        for section_name in self.current_sections.keys():
            # Check if section name contains any of the patterns (case-insensitive)
            for pattern in patterns:
                if pattern.lower() in section_name.lower():
                    matching_sections.append(section_name)
                    break
        
        # If no matches, return empty list (not all sections)
        return matching_sections
    
    def get_section_parameters(self, section_name: str) -> Dict[str, str]:
        """
        Get all parameters for a section.
        
        Args:
            section_name: Section name
            
        Returns:
            Dict of parameter_name: value (as strings)
        """
        if section_name in self.current_sections:
            return self.current_sections[section_name].parameters.copy()
        return {}
    
    def update_parameter(self, section: str, key: str, value: str):
        """
        Update a parameter value.
        
        Args:
            section: Section name
            key: Parameter key
            value: New value (as string)
        """
        if section in self.current_sections:
            self.current_sections[section].parameters[key] = value
            
            # Track modification
            param_id = f"{section}.{key}"
            
            # Check if actually different from original
            original_value = self.original_sections.get(section, INISection("", {})).parameters.get(key, "")
            if value != original_value:
                self.modified_params.add(param_id)
            else:
                self.modified_params.discard(param_id)
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved modifications."""
        return len(self.modified_params) > 0
    
    def get_modified_count(self) -> int:
        """Get number of modified parameters."""
        return len(self.modified_params)
    
    def revert_all(self):
        """Revert all changes to original values."""
        self.current_sections = {
            section_name: INISection(
                name=section.name,
                parameters=section.parameters.copy()
            )
            for section_name, section in self.original_sections.items()
        }
        self.modified_params.clear()
    
    def revert_section(self, section_name: str):
        """Revert changes in a specific section."""
        if section_name in self.original_sections:
            self.current_sections[section_name] = INISection(
                name=self.original_sections[section_name].name,
                parameters=self.original_sections[section_name].parameters.copy()
            )
            
            # Remove from modified set
            to_remove = [p for p in self.modified_params if p.startswith(f"{section_name}.")]
            for param_id in to_remove:
                self.modified_params.discard(param_id)
    
    def save_ini(self, create_backup: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Save current values to INI file.
        
        Args:
            create_backup: Whether to create backup before saving
            
        Returns:
            (success, error_message)
        """
        try:
            # Create backup if requested
            if create_backup:
                backup_path = self.backup_manager.create_backup(self.ini_path)
                print(f"Backup created: {backup_path}")
            
            # Convert current sections back to MaxINIParameter objects
            parameters_to_save: List[MaxINIParameter] = []
            
            for param in self.original_parameters:
                # Get current value (might be modified)
                current_value = self.current_sections[param.section].parameters.get(param.key, str(param.value))
                
                # Create new parameter object with current value
                # Type conversion happens in parser.save()
                param_copy = MaxINIParameter(
                    key=param.key,
                    value=current_value,  # Keep as string, parser will handle conversion
                    type=param.type,
                    category=param.category,
                    section=param.section,
                    description_ru=param.description_ru,
                    description_en=param.description_en,
                    validation=param.validation,
                    default_value=param.default_value,
                    unit=param.unit
                )
                parameters_to_save.append(param_copy)
            
            # Save with parser
            self.parser.save(self.ini_path, parameters_to_save, create_backup=False)
            
            # Update original to match current (changes are now saved)
            self.original_sections = {
                section_name: INISection(
                    name=section.name,
                    parameters=section.parameters.copy()
                )
                for section_name, section in self.current_sections.items()
            }
            
            # Clear modifications
            self.modified_params.clear()
            
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to save INI: {e}"
            print(error_msg)
            return False, error_msg
    
    def get_parameter_help(self, section: str, key: str) -> str:
        """
        Get help text for a parameter.
        
        Args:
            section: Section name
            key: Parameter key
            
        Returns:
            Help text or default message
        """
        # Find parameter in original list
        for param in self.original_parameters:
            if param.section == section and param.key == key:
                # Build help text
                help_lines = [f"{key}\n"]
                
                if param.description_en:
                    help_lines.append(param.description_en)
                elif param.description_ru:
                    help_lines.append(param.description_ru)
                else:
                    help_lines.append("No description available.")
                
                # Add validation info
                if param.validation:
                    help_lines.append("")
                    if param.validation.min_value is not None or param.validation.max_value is not None:
                        min_v = param.validation.min_value if param.validation.min_value is not None else "—"
                        max_v = param.validation.max_value if param.validation.max_value is not None else "—"
                        help_lines.append(f"📊 Range: {min_v} to {max_v}")
                    
                    if param.validation.allowed_values:
                        help_lines.append(f"✅ Allowed: {', '.join(param.validation.allowed_values)}")
                
                # Add default value
                if param.default_value is not None:
                    help_lines.append(f"💡 Default: {param.default_value}")
                
                return "\n".join(help_lines)
        
        return f"{key}\n\nNo help available for this parameter."

