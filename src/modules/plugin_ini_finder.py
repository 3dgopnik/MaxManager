"""
Plugin INI Finder - finds and loads plugin INI files.

Searches common plugin locations and loads real plugin INI files.
"""

from pathlib import Path
from typing import Dict, List
import os


class PluginINIFinder:
    """Finds plugin INI files in common locations."""
    
    def __init__(self):
        self.plugin_ini_files: Dict[str, Path] = {}
        
    def find_plugin_inis(self) -> Dict[str, Path]:
        """
        Find all plugin INI files in common locations.
        
        Returns:
            Dict[plugin_name, ini_path] - e.g., {'vray.ini': Path('C:/ProgramData/.../vray.ini')}
        """
        search_locations = self._get_search_locations()
        
        print(f"[Plugin Finder] Searching in {len(search_locations)} locations...")
        
        found_inis = {}
        
        # Known plugin INI files to search for
        known_plugins = {
            'vray': ['vray.ini', 'vraymax', 'v-ray'],
            'corona': ['corona.ini', 'coronarenderer'],
            'forestpack': ['forestpack.ini', 'forest pack', 'itoo'],
            'arnold': ['arnold.ini', 'maxtoa', 'solidangle'],
            'redshift': ['redshift.ini'],
            'phoenixfd': ['phoenixfd.ini', 'phoenix'],
            'railclone': ['railclone.ini'],
            'tyflow': ['tyflow.ini'],
        }
        
        for location in search_locations:
            if not location.exists():
                continue
            
            try:
                # Search for .ini files with limited depth to avoid thousands of files
                for ini_file in location.glob('**/*.ini'):
                    # Skip deep paths (signs, models, etc.)
                    relative = ini_file.relative_to(location)
                    if len(relative.parts) > 4:
                        continue
                    
                    # Skip 3dsmax.ini itself
                    if ini_file.name.lower() == '3dsmax.ini':
                        continue
                    
                    # Skip backup/temp files
                    if any(x in ini_file.name.lower() for x in ['backup', 'temp', 'old', '~', 'default']):
                        continue
                    
                    # Skip object/sign/model config files
                    parent_lower = str(ini_file.parent).lower()
                    if any(x in parent_lower for x in ['signs', 'objlibs', 'models', 'kits', 'presets']):
                        continue
                    
                    # Check against known plugins
                    file_lower = ini_file.name.lower()
                    path_lower = str(ini_file).lower()
                    
                    matched = False
                    for plugin_key, patterns in known_plugins.items():
                        if any(pattern in file_lower or pattern in path_lower for pattern in patterns):
                            found_inis[f'{plugin_key}.ini'] = ini_file
                            matched = True
                            break
                    
                    # Also accept main plugin config files in plugcfg folder
                    if not matched and 'plugcfg' in path_lower:
                        # Only specific well-known plugin configs
                        if file_lower in ['forestpack.ini', 'vray.ini', 'corona.ini', 'phoenixfd.ini']:
                            found_inis[file_lower] = ini_file
                        
            except Exception as e:
                print(f"[Plugin Finder] Error searching {location}: {e}")
                continue
        
        self.plugin_ini_files = found_inis
        print(f"[Plugin Finder] Found {len(found_inis)} plugin INI files:")
        for name, path in found_inis.items():
            print(f"  - {name}: {path}")
        
        return found_inis
    
    def _get_search_locations(self) -> List[Path]:
        """Get common plugin INI locations."""
        locations = []
        
        # Get username
        username = os.environ.get('USERNAME', 'acherednikov')
        
        # Common plugin locations
        common_paths = [
            # ProgramData - V-Ray, Corona, etc.
            Path(r"C:\ProgramData\Autodesk\ApplicationPlugins"),
            Path(r"C:\ProgramData\Chaos Group"),
            Path(r"C:\ProgramData\Corona"),
            
            # AppData Local - 3ds Max user settings
            Path(rf"C:\Users\{username}\AppData\Local\Autodesk\3dsMax\2025 - 64bit\ENU"),
            Path(rf"C:\Users\{username}\AppData\Local\Autodesk\3dsMax\2024 - 64bit\ENU"),
            
            # Program Files - plugin installations
            Path(r"C:\Program Files\Chaos Group"),
            Path(r"C:\Program Files\Autodesk\3ds Max 2025"),
            Path(r"C:\Program Files (x86)\Chaos Group"),
            
            # IToo Software (ForestPack)
            Path(rf"C:\Users\{username}\AppData\Local\Itoo Software"),
            Path(r"C:\Program Files\Itoo Software"),
            
            # Arnold
            Path(r"C:\ProgramData\Autodesk\ApplicationPlugins\MAXtoA"),
            
            # Redshift
            Path(r"C:\ProgramData\Redshift"),
        ]
        
        # Add to locations if exist
        for path in common_paths:
            if path.exists():
                locations.append(path)
        
        return locations
    
    def get_ini_path(self, ini_filename: str) -> Path:
        """Get path for specific plugin INI."""
        return self.plugin_ini_files.get(ini_filename.lower())


# Test
if __name__ == '__main__':
    finder = PluginINIFinder()
    found = finder.find_plugin_inis()
    
    print("\n" + "=" * 80)
    print(f"TOTAL FOUND: {len(found)} plugin INI files")
    print("=" * 80)

