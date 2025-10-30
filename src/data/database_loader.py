"""
Database loader for INI parameters.

Loads and provides access to 844 parameters from ini_parameters_database.json
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ParameterDatabase:
    """INI Parameters Database"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database loader"""
        if db_path is None:
            # Default path relative to this file
            db_path = Path(__file__).parent.parent.parent / 'docs' / 'ini_parameters_database.json'
        
        self.db_path = db_path
        self.parameters: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.section_translations: Dict[str, Dict[str, str]] = {}
        self._loaded = False
    
    def load(self) -> bool:
        """Load database from JSON"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store metadata separately
            self.metadata = data.get('_metadata', {})
            
            # Remove metadata from parameters
            self.parameters = {k: v for k, v in data.items() if k != '_metadata'}
            self._loaded = True
            
            # Load section translations if available
            self.section_translations = self.metadata.get('section_translations', {})
            
            print(f"[DB] Loaded {len(self.parameters)} parameters from database")
            if self.section_translations:
                print(f"[DB] Loaded {len(self.section_translations)} section translations")
            return True
            
        except Exception as e:
            print(f"[DB] ERROR loading database: {e}")
            return False
    
    def get_parameter(self, name: str) -> Optional[Dict[str, Any]]:
        """Get parameter by name"""
        if not self._loaded:
            self.load()
        return self.parameters.get(name)
    
    def get_parameters_for_section(self, section: str) -> Dict[str, Any]:
        """Get all parameters for a section
        
        Example: section='Performance' returns all Performance.* parameters
        """
        if not self._loaded:
            self.load()
        
        result = {}
        prefix = f"{section}."
        
        for param_name, param_data in self.parameters.items():
            if param_name.startswith(prefix):
                result[param_name] = param_data
        
        return result
    
    def get_all_sections(self) -> Dict[str, int]:
        """Get all unique sections with parameter counts"""
        if not self._loaded:
            self.load()
        
        sections = {}
        for param_name in self.parameters.keys():
            if '.' in param_name:
                section = param_name.split('.')[0]
                sections[section] = sections.get(section, 0) + 1
        
        return sections
    
    def group_by_ini_file(self) -> Dict[str, Dict[str, list]]:
        """Group parameters by ini_file
        
        Returns:
            {
                '3dsmax.ini': {'Security': ['Security.SafeScript', ...], ...},
                'corona.ini': {'Corona': ['Corona.numThreads', ...], ...}
            }
        """
        if not self._loaded:
            self.load()
        
        result = {}
        
        for param_name, param_data in self.parameters.items():
            ini_file = param_data.get('ini_file', '3dsmax.ini')
            
            if '.' in param_name:
                section = param_name.split('.')[0]
            else:
                section = 'Unknown'
            
            if ini_file not in result:
                result[ini_file] = {}
            
            if section not in result[ini_file]:
                result[ini_file][section] = []
            
            result[ini_file][section].append(param_name)
        
        return result
    
    @property
    def total_parameters(self) -> int:
        """Total number of parameters in database"""
        if not self._loaded:
            self.load()
        return len(self.parameters)
    
    def get_section_translation(self, section_name: str, language: str = "en") -> str:
        """
        Get translated section name.
        
        Args:
            section_name: Section name (e.g., "Security", "OpenImageIO")
            language: "en" or "ru"
        
        Returns:
            Translated section name or original if not found
        """
        if not self._loaded:
            self.load()
        
        if section_name in self.section_translations:
            return self.section_translations[section_name].get(language, section_name)
        
        return section_name


# Global instance
_db_instance = None

def get_database() -> ParameterDatabase:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ParameterDatabase()
        _db_instance.load()
    return _db_instance

