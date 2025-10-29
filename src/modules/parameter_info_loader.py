"""
Parameter information loader for INI parameters.

Loads parameter metadata (display names, descriptions, help text) from JSON.
"""

import json
from pathlib import Path
from typing import Dict, Optional


class ParameterInfoLoader:
    """Loads and provides parameter information from JSON database."""
    
    def __init__(self, json_path: Path = None):
        # Use main database from docs folder (844 parameters)
        self.json_path = json_path or Path(__file__).parent.parent.parent / "docs" / "ini_parameters_database.json"
        self.parameters: Dict = {}
        self.load_parameters()
    
    def load_parameters(self) -> bool:
        """Load parameters from JSON file."""
        try:
            if not self.json_path.exists():
                print(f"WARN Parameter info file not found: {self.json_path}")
                return False
            
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.parameters = json.load(f)
            
            print(f"OK Loaded {len(self.parameters)} parameter descriptions")
            return True
            
        except Exception as e:
            print(f"FAIL Failed to load parameter info: {e}")
            return False
    
    def get_display_name(self, param_name: str, language: str = "ru") -> Optional[str]:
        """Get localized display name for a parameter."""
        # Try exact case-insensitive match first
        for key in self.parameters:
            if key.lower() == param_name.lower():
                param_info = self.parameters[key]
                # Primary language
                if language in param_info and "display_name" in param_info[language]:
                    return param_info[language]["display_name"]
                # Fallback to English
                if "en" in param_info and "display_name" in param_info["en"]:
                    return param_info["en"]["display_name"]
                # Fallback to raw key
                return key
        
        # Try matching with Section.Parameter format (e.g., Performance.UnitType)
        for key in self.parameters:
            # Extract parameter name after last dot
            param_only = key.split('.')[-1] if '.' in key else key
            if param_only.lower() == param_name.lower():
                param_info = self.parameters[key]
                # Primary language
                if language in param_info and "display_name" in param_info[language]:
                    return param_info[language]["display_name"]
                # Fallback to English
                if "en" in param_info and "display_name" in param_info["en"]:
                    return param_info["en"]["display_name"]
                # Fallback to raw key
                return key
        
        return None
    
    def get_description(self, param_name: str, language: str = "ru") -> Optional[str]:
        """Get localized description for a parameter."""
        if param_name not in self.parameters:
            return None
        
        param_info = self.parameters[param_name]
        if language in param_info:
            return param_info[language].get("description")
        
        return None
    
    def get_help_text(self, param_name: str, language: str = "ru") -> Optional[str]:
        """Get localized help text for a parameter."""
        # Try exact case-insensitive match
        for key in self.parameters:
            if key.lower() == param_name.lower():
                param_info = self.parameters[key]
                if language in param_info and "help_text" in param_info[language]:
                    return param_info[language]["help_text"]
        
        # Try matching with Section.Parameter format
        for key in self.parameters:
            param_only = key.split('.')[-1] if '.' in key else key
            if param_only.lower() == param_name.lower():
                param_info = self.parameters[key]
                if language in param_info and "help_text" in param_info[language]:
                    return param_info[language]["help_text"]
        
        return None
    
    def get_type(self, param_name: str) -> Optional[str]:
        """Get parameter type."""
        if param_name not in self.parameters:
            return None
        
        return self.parameters[param_name].get("type")
    
    def get_recommended(self, param_name: str) -> Optional[str]:
        """Get recommended value for a parameter."""
        if param_name not in self.parameters:
            return None
        
        return self.parameters[param_name].get("recommended")
    
    def has_info(self, param_name: str) -> bool:
        """Check if parameter has information available."""
        # Try exact case-insensitive match
        if any(key.lower() == param_name.lower() for key in self.parameters):
            return True
        # Try matching with Section.Parameter format
        for key in self.parameters:
            param_only = key.split('.')[-1] if '.' in key else key
            if param_only.lower() == param_name.lower():
                return True
        return False
