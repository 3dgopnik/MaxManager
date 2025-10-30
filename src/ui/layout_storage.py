"""
Layout Storage for MaxManager Canvas.

Handles saving and loading canvas layout configurations to/from JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class LayoutStorage:
    """
    Manages persistent storage of canvas layout configurations.
    
    Stores canvas positions, spans, and other layout metadata in JSON format.
    Default storage location: ~/.maxmanager/canvas_layout.json
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize layout storage.
        
        Args:
            storage_path: Optional custom path for storage file.
                         Defaults to ~/.maxmanager/canvas_layout.json
        """
        if storage_path is None:
            # Default to user home directory
            home = Path.home()
            storage_dir = home / ".maxmanager"
            storage_dir.mkdir(parents=True, exist_ok=True)
            self.storage_path = storage_dir / "canvas_layout.json"
        else:
            self.storage_path = Path(storage_path)
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"[LayoutStorage] Using storage: {self.storage_path}")
    
    def save_layout(self, layout_data: Dict[str, Dict], layout_name: str = "default") -> bool:
        """
        Save layout configuration to file.
        
        Args:
            layout_data: Dictionary with canvas positions (from GridLayoutManager.to_dict())
            layout_name: Name of the layout (for multiple layout support)
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Load existing layouts
            all_layouts = self._load_all_layouts()
            
            # Update with new layout
            all_layouts[layout_name] = {
                "data": layout_data,
                "updated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Save to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(all_layouts, f, indent=2, ensure_ascii=False)
            
            print(f"[LayoutStorage] Saved layout '{layout_name}' with {len(layout_data)} items")
            return True
            
        except Exception as e:
            print(f"[LayoutStorage] ERROR saving layout: {e}")
            return False
    
    def load_layout(self, layout_name: str = "default") -> Optional[Dict[str, Dict]]:
        """
        Load layout configuration from file.
        
        Args:
            layout_name: Name of the layout to load
        
        Returns:
            Dictionary with canvas positions or None if not found
        """
        try:
            all_layouts = self._load_all_layouts()
            
            if layout_name not in all_layouts:
                print(f"[LayoutStorage] Layout '{layout_name}' not found")
                return None
            
            layout_info = all_layouts[layout_name]
            data = layout_info.get("data", {})
            
            print(f"[LayoutStorage] Loaded layout '{layout_name}' with {len(data)} items")
            return data
            
        except Exception as e:
            print(f"[LayoutStorage] ERROR loading layout: {e}")
            return None
    
    def delete_layout(self, layout_name: str) -> bool:
        """
        Delete a saved layout.
        
        Args:
            layout_name: Name of layout to delete
        
        Returns:
            True if deleted, False if not found or error
        """
        try:
            all_layouts = self._load_all_layouts()
            
            if layout_name not in all_layouts:
                print(f"[LayoutStorage] Layout '{layout_name}' not found")
                return False
            
            del all_layouts[layout_name]
            
            # Save updated layouts
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(all_layouts, f, indent=2, ensure_ascii=False)
            
            print(f"[LayoutStorage] Deleted layout '{layout_name}'")
            return True
            
        except Exception as e:
            print(f"[LayoutStorage] ERROR deleting layout: {e}")
            return False
    
    def list_layouts(self) -> Dict[str, Dict]:
        """
        Get list of all saved layouts with metadata.
        
        Returns:
            Dictionary mapping layout names to their metadata
        """
        all_layouts = self._load_all_layouts()
        
        # Return only metadata (without full data)
        result = {}
        for name, info in all_layouts.items():
            result[name] = {
                "updated_at": info.get("updated_at", "unknown"),
                "version": info.get("version", "unknown"),
                "item_count": len(info.get("data", {}))
            }
        
        return result
    
    def has_saved_layout(self, layout_name: str = "default") -> bool:
        """
        Check if a layout exists in storage.
        
        Args:
            layout_name: Name of layout to check
        
        Returns:
            True if layout exists, False otherwise
        """
        all_layouts = self._load_all_layouts()
        return layout_name in all_layouts
    
    def _load_all_layouts(self) -> Dict:
        """
        Load all layouts from storage file.
        
        Returns:
            Dictionary of all layouts or empty dict if file doesn't exist
        """
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[LayoutStorage] ERROR: Corrupt JSON file: {e}")
            # Backup corrupt file
            backup_path = self.storage_path.with_suffix('.json.backup')
            if self.storage_path.exists():
                self.storage_path.rename(backup_path)
                print(f"[LayoutStorage] Backed up corrupt file to {backup_path}")
            return {}
        except Exception as e:
            print(f"[LayoutStorage] ERROR reading file: {e}")
            return {}
    
    def export_layout(self, layout_name: str, export_path: Path) -> bool:
        """
        Export layout to external file (for sharing/backup).
        
        Args:
            layout_name: Name of layout to export
            export_path: Path where to export
        
        Returns:
            True if exported successfully
        """
        layout_data = self.load_layout(layout_name)
        if layout_data is None:
            return False
        
        try:
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "layout_name": layout_name,
                    "exported_at": datetime.now().isoformat(),
                    "data": layout_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"[LayoutStorage] Exported layout '{layout_name}' to {export_path}")
            return True
            
        except Exception as e:
            print(f"[LayoutStorage] ERROR exporting layout: {e}")
            return False
    
    def import_layout(self, import_path: Path, layout_name: Optional[str] = None) -> bool:
        """
        Import layout from external file.
        
        Args:
            import_path: Path to import from
            layout_name: Optional new name for imported layout
        
        Returns:
            True if imported successfully
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Use provided name or original name
            name = layout_name or imported.get("layout_name", "imported")
            data = imported.get("data", {})
            
            return self.save_layout(data, name)
            
        except Exception as e:
            print(f"[LayoutStorage] ERROR importing layout: {e}")
            return False

