"""MaxINI Presets - Predefined configurations for max.ini optimization."""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pathlib import Path
import json


@dataclass
class MaxINIPreset:
    """Represents a preset configuration for max.ini."""
    
    name: str
    description_en: str
    description_ru: str
    author: str
    parameters: Dict[str, Any]
    tags: List[str]
    version: str = "1.0"
    created_date: str = "2025-10-17"
    category: str = "General"


class MaxINIPresetManager:
    """Manager for max.ini presets."""
    
    def __init__(self, presets_path: Optional[Path] = None) -> None:
        """
        Initialize preset manager.
        
        Args:
            presets_path: Path to presets directory
        """
        if presets_path is None:
            presets_path = Path(__file__).parent.parent.parent / "data" / "presets"
        
        self.presets_path = presets_path
        self.built_in_presets = self._load_built_in_presets()
        self.user_presets = self._load_user_presets()
    
    def _load_built_in_presets(self) -> Dict[str, MaxINIPreset]:
        """Load built-in presets."""
        presets = {}
        
        # High Performance Preset
        presets["high_performance"] = MaxINIPreset(
            name="High Performance",
            description_en="Optimized for maximum rendering performance and speed",
            description_ru="Оптимизировано для максимальной производительности рендеринга",
            author="MaxManager",
            parameters={
                "RenderThreads": 16,
                "UseAllCores": True,
                "ThreadPriority": 3,  # High priority
                "MemoryPool": 2048,  # 2GB
                "DynamicHeapSize": True,
                "PageFileSize": 8192,  # 8GB
                "ViewportPerformanceMode": 1,  # Max performance
                "AutoBackup": True,
                "BackupInterval": 5,  # More frequent backups
            },
            tags=["performance", "rendering", "speed", "optimization"],
            category="Performance"
        )
        
        # Memory Optimized Preset
        presets["memory_optimized"] = MaxINIPreset(
            name="Memory Optimized",
            description_en="Optimized for large scenes with high memory usage",
            description_ru="Оптимизировано для больших сцен с высоким потреблением памяти",
            author="MaxManager",
            parameters={
                "RenderThreads": 8,
                "UseAllCores": True,
                "ThreadPriority": 2,  # Above normal
                "MemoryPool": 4096,  # 4GB
                "DynamicHeapSize": True,
                "PageFileSize": 16384,  # 16GB
                "ViewportPerformanceMode": 0,  # Balanced
                "AutoBackup": True,
                "BackupInterval": 15,
            },
            tags=["memory", "large_scenes", "optimization"],
            category="Memory"
        )
        
        # Arnold Renderer Preset
        presets["arnold_renderer"] = MaxINIPreset(
            name="Arnold Renderer",
            description_en="Optimized settings for Arnold rendering workflow",
            description_ru="Оптимизированные настройки для рабочего процесса Arnold",
            author="MaxManager",
            parameters={
                "RenderThreads": 12,
                "UseAllCores": True,
                "ThreadPriority": 2,
                "MemoryPool": 3072,  # 3GB
                "DynamicHeapSize": True,
                "PageFileSize": 12288,  # 12GB
                "ViewportPerformanceMode": 2,  # Max quality
                "AutoBackup": True,
                "BackupInterval": 10,
            },
            tags=["arnold", "renderer", "workflow"],
            category="Renderers"
        )
        
        # V-Ray Renderer Preset
        presets["vray_renderer"] = MaxINIPreset(
            name="V-Ray Renderer",
            description_en="Optimized settings for V-Ray rendering workflow",
            description_ru="Оптимизированные настройки для рабочего процесса V-Ray",
            author="MaxManager",
            parameters={
                "RenderThreads": 14,
                "UseAllCores": True,
                "ThreadPriority": 2,
                "MemoryPool": 2560,  # 2.5GB
                "DynamicHeapSize": True,
                "PageFileSize": 10240,  # 10GB
                "ViewportPerformanceMode": 1,  # Max performance
                "AutoBackup": True,
                "BackupInterval": 10,
            },
            tags=["vray", "renderer", "workflow"],
            category="Renderers"
        )
        
        # Minimal Preset
        presets["minimal"] = MaxINIPreset(
            name="Minimal",
            description_en="Minimal settings for basic 3ds Max functionality",
            description_ru="Минимальные настройки для базовой функциональности 3ds Max",
            author="MaxManager",
            parameters={
                "RenderThreads": 4,
                "UseAllCores": False,
                "ThreadPriority": 1,  # Normal
                "MemoryPool": 512,  # 512MB
                "DynamicHeapSize": False,
                "PageFileSize": 2048,  # 2GB
                "ViewportPerformanceMode": 0,  # Balanced
                "AutoBackup": False,
                "BackupInterval": 30,
            },
            tags=["minimal", "basic", "lightweight"],
            category="General"
        )
        
        return presets
    
    def _load_user_presets(self) -> Dict[str, MaxINIPreset]:
        """Load user-created presets from JSON files."""
        presets = {}
        
        if not self.presets_path.exists():
            return presets
        
        # Load from JSON files in presets directory
        for json_file in self.presets_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                preset = MaxINIPreset(
                    name=data["name"],
                    description_en=data.get("description_en", ""),
                    description_ru=data.get("description_ru", ""),
                    author=data.get("author", "User"),
                    parameters=data["parameters"],
                    tags=data.get("tags", []),
                    version=data.get("version", "1.0"),
                    created_date=data.get("created_date", ""),
                    category=data.get("category", "User"),
                )
                
                presets[json_file.stem] = preset
                
            except Exception as e:
                print(f"Failed to load preset {json_file}: {e}")
        
        return presets
    
    def get_all_presets(self) -> Dict[str, MaxINIPreset]:
        """Get all presets (built-in + user)."""
        all_presets = {}
        all_presets.update(self.built_in_presets)
        all_presets.update(self.user_presets)
        return all_presets
    
    def get_preset_by_name(self, name: str) -> Optional[MaxINIPreset]:
        """Get preset by name."""
        all_presets = self.get_all_presets()
        return all_presets.get(name)
    
    def get_presets_by_category(self, category: str) -> Dict[str, MaxINIPreset]:
        """Get presets by category."""
        all_presets = self.get_all_presets()
        return {k: v for k, v in all_presets.items() if v.category == category}
    
    def get_presets_by_tags(self, tags: List[str]) -> Dict[str, MaxINIPreset]:
        """Get presets that match any of the given tags."""
        all_presets = self.get_all_presets()
        matching = {}
        
        for key, preset in all_presets.items():
            if any(tag in preset.tags for tag in tags):
                matching[key] = preset
        
        return matching
    
    def save_user_preset(self, preset: MaxINIPreset) -> bool:
        """Save user preset to JSON file."""
        try:
            if not self.presets_path.exists():
                self.presets_path.mkdir(parents=True, exist_ok=True)
            
            # Create safe filename
            safe_name = "".join(c for c in preset.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            
            json_file = self.presets_path / f"{safe_name}.json"
            
            # Convert preset to dict
            preset_data = {
                "name": preset.name,
                "description_en": preset.description_en,
                "description_ru": preset.description_ru,
                "author": preset.author,
                "parameters": preset.parameters,
                "tags": preset.tags,
                "version": preset.version,
                "created_date": preset.created_date,
                "category": preset.category,
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            
            # Reload user presets
            self.user_presets = self._load_user_presets()
            
            return True
            
        except Exception as e:
            print(f"Failed to save preset {preset.name}: {e}")
            return False
    
    def delete_user_preset(self, preset_name: str) -> bool:
        """Delete user preset."""
        try:
            safe_name = "".join(c for c in preset_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            
            json_file = self.presets_path / f"{safe_name}.json"
            
            if json_file.exists():
                json_file.unlink()
                self.user_presets = self._load_user_presets()
                return True
            
            return False
            
        except Exception as e:
            print(f"Failed to delete preset {preset_name}: {e}")
            return False
    
    def apply_preset_to_parameters(self, preset: MaxINIPreset, parameters: List) -> List:
        """Apply preset values to parameter list."""
        from src.modules.maxini_parser import MaxINIParameter
        
        # Create lookup dict for parameters
        param_lookup = {}
        for param in parameters:
            param_lookup[param.key.lower()] = param
        
        # Apply preset values
        for key, value in preset.parameters.items():
            if key.lower() in param_lookup:
                param_lookup[key.lower()].value = value
        
        return parameters
    
    def get_categories(self) -> List[str]:
        """Get list of all preset categories."""
        all_presets = self.get_all_presets()
        categories = set()
        
        for preset in all_presets.values():
            categories.add(preset.category)
        
        return sorted(list(categories))
