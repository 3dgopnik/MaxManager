# Module API: MaxINI Editor GUI

**Feature**: 001-maxini-editor-gui  
**Date**: 2025-10-17  
**Type**: Python Module Interfaces

## Overview

MaxINI Editor состоит из 4 Python модулей с чёткими контрактами:

1. **maxini_parser** - Парсинг и запись INI файлов
2. **maxini_presets** - Управление пресетами
3. **maxini_backup** - Резервное копирование
4. **maxini_editor** - Главный модуль + бизнес-логика

---

## Module: maxini_parser

**Purpose**: Парсинг, валидация и запись max.ini файлов

###

 API

```python
class MaxINIParser:
    """Parser for 3ds Max configuration files"""
    
    def __init__(self, validation_rules_path: Path | None = None):
        """
        Initialize parser with optional validation rules
        
        Args:
            validation_rules_path: Path to validation_rules.json
        """
        ...
    
    def load(self, ini_path: Path) -> List[MaxINIParameter]:
        """
        Load and parse max.ini file
        
        Args:
            ini_path: Path to 3dsMax.ini
            
        Returns:
            List of MaxINIParameter objects
            
        Raises:
            FileNotFoundError: If ini_path doesn't exist
            UnicodeDecodeError: If encoding is not UTF-16 LE
            ParsingError: If INI format is invalid
        """
        ...
    
    def save(self, 
             ini_path: Path, 
             parameters: List[MaxINIParameter],
             create_backup: bool = True) -> Path:
        """
        Save parameters to max.ini file
        
        Args:
            ini_path: Path to 3dsMax.ini
            parameters: List of parameters to save
            create_backup: Whether to backup before writing
            
        Returns:
            Path to backup file (if created)
            
        Raises:
            ValidationError: If parameters fail validation
            PermissionError: If no write access to ini_path
        """
        ...
    
    def validate(self, 
                 parameters: List[MaxINIParameter]) -> List[ValidationError]:
        """
        Validate parameters against rules
        
        Args:
            parameters: List of parameters to validate
            
        Returns:
            List of validation errors (empty if all valid)
        """
        ...
    
    def get_parameter(self, 
                      parameters: List[MaxINIParameter],
                      key: str) -> MaxINIParameter | None:
        """
        Find parameter by key
        
        Args:
            parameters: List to search
            key: Parameter key (e.g., "RenderThreads")
            
        Returns:
            Parameter or None if not found
        """
        ...
    
    def group_by_category(self,
                          parameters: List[MaxINIParameter]
                          ) -> Dict[ParamCategory, List[MaxINIParameter]]:
        """
        Group parameters by category for UI display
        
        Args:
            parameters: List of parameters
            
        Returns:
            Dict mapping category to parameters
        """
        ...
```

**Dependencies**: `configparser`, `pathlib`, `dataclasses`

**Example Usage**:

```python
parser = MaxINIParser(validation_rules_path=Path("data/validation/rules.json"))

# Load max.ini
parameters = parser.load(Path("C:/Users/user/AppData/Local/Autodesk/3dsMax/2025/3dsMax.ini"))

# Validate
errors = parser.validate(parameters)
if errors:
    for error in errors:
        print(f"Validation error: {error}")

# Group by category for UI
grouped = parser.group_by_category(parameters)
for category, params in grouped.items():
    print(f"{category}: {len(params)} parameters")

# Modify and save
param = parser.get_parameter(parameters, "RenderThreads")
if param:
    param.value = 16
    
backup_path = parser.save(
    Path("C:/Users/user/AppData/Local/Autodesk/3dsMax/2025/3dsMax.ini"),
    parameters,
    create_backup=True
)
print(f"Backup created: {backup_path}")
```

---

## Module: maxini_presets

**Purpose**: Управление встроенными и пользовательскими пресетами

### API

```python
class MaxINIPresetManager:
    """Manager for built-in and user presets"""
    
    def __init__(self, 
                 built_in_dir: Path,
                 user_presets_dir: Path):
        """
        Initialize preset manager
        
        Args:
            built_in_dir: Path to built-in presets (data/presets/built-in/)
            user_presets_dir: Path to user presets (~/.maxmanager/presets/)
        """
        ...
    
    def list_presets(self, 
                     author: PresetAuthor | None = None) -> List[MaxINIPreset]:
        """
        List available presets
        
        Args:
            author: Filter by BUILT_IN or USER (None = all)
            
        Returns:
            List of presets
        """
        ...
    
    def load_preset(self, name: str) -> MaxINIPreset:
        """
        Load preset by name
        
        Args:
            name: Preset name (e.g., "high_performance")
            
        Returns:
            Preset object
            
        Raises:
            PresetNotFoundError: If preset doesn't exist
        """
        ...
    
    def save_preset(self, preset: MaxINIPreset) -> Path:
        """
        Save user preset to file
        
        Args:
            preset: Preset to save (must be author=USER)
            
        Returns:
            Path to saved JSON file
            
        Raises:
            ValueError: If preset is BUILT_IN
            ValidationError: If preset validation fails
        """
        ...
    
    def delete_preset(self, name: str) -> bool:
        """
        Delete user preset
        
        Args:
            name: Preset name
            
        Returns:
            True if deleted, False if not found or BUILT_IN
        """
        ...
    
    def apply_preset(self,
                     preset: MaxINIPreset,
                     current_parameters: List[MaxINIParameter]
                     ) -> List[MaxINIParameter]:
        """
        Apply preset to current parameters
        
        Args:
            preset: Preset to apply
            current_parameters: Current parameter values
            
        Returns:
            Updated parameters list
        """
        ...
    
    def preview_changes(self,
                        preset: MaxINIPreset,
                        current_parameters: List[MaxINIParameter]
                        ) -> List[ParameterChange]:
        """
        Preview what will change if preset is applied
        
        Args:
            preset: Preset to preview
            current_parameters: Current values
            
        Returns:
            List of changes (old value → new value)
        """
        ...
    
    def create_from_current(self,
                            name: str,
                            description_ru: str,
                            description_en: str,
                            current_parameters: List[MaxINIParameter],
                            tags: List[str] | None = None
                            ) -> MaxINIPreset:
        """
        Create user preset from current parameter values
        
        Args:
            name: Preset name
            description_ru: Russian description
            description_en: English description
            current_parameters: Current values to save
            tags: Optional tags
            
        Returns:
            Created preset
        """
        ...
```

**Dependencies**: `json`, `pathlib`, `datetime`, `dataclasses`

**Example Usage**:

```python
manager = MaxINIPresetManager(
    built_in_dir=Path("data/presets/built-in"),
    user_presets_dir=Path.home() / ".maxmanager" / "presets"
)

# List all presets
all_presets = manager.list_presets()
for preset in all_presets:
    print(f"{preset.name} ({preset.author}): {preset.description_en}")

# Load and preview high performance preset
hp_preset = manager.load_preset("high_performance")
changes = manager.preview_changes(hp_preset, current_parameters)
print(f"Will change {len(changes)} parameters:")
for change in changes:
    print(f"  {change.key}: {change.old_value} → {change.new_value}")

# Apply preset
updated_params = manager.apply_preset(hp_preset, current_parameters)

# Create user preset from current settings
my_preset = manager.create_from_current(
    name="my_arnold_setup",
    description_ru="Моя настройка Arnold",
    description_en="My Arnold Setup",
    current_parameters=updated_params,
    tags=["arnold", "custom"]
)
manager.save_preset(my_preset)
```

---

## Module: maxini_backup

**Purpose**: Создание и управление резервными копиями max.ini

### API

```python
class MaxINIBackupManager:
    """Manager for max.ini backups"""
    
    def __init__(self, max_backups: int = 10):
        """
        Initialize backup manager
        
        Args:
            max_backups: Maximum number of backups to keep (default: 10)
        """
        ...
    
    def create_backup(self, 
                      ini_path: Path,
                      reason: str | None = None) -> MaxINIBackup:
        """
        Create timestamped backup of max.ini
        
        Args:
            ini_path: Path to 3dsMax.ini
            reason: Optional reason (e.g., "preset_applied:high_performance")
            
        Returns:
            Backup object
            
        Raises:
            FileNotFoundError: If ini_path doesn't exist
            PermissionError: If can't write to backup location
        """
        ...
    
    def list_backups(self, ini_path: Path) -> List[MaxINIBackup]:
        """
        List all backups for given ini file
        
        Args:
            ini_path: Path to 3dsMax.ini
            
        Returns:
            List of backups (sorted by timestamp, newest first)
        """
        ...
    
    def restore_backup(self, backup: MaxINIBackup) -> Path:
        """
        Restore max.ini from backup
        
        Args:
            backup: Backup to restore
            
        Returns:
            Path to restored ini file
            
        Raises:
            FileNotFoundError: If backup file doesn't exist
            ChecksumError: If backup file is corrupted
        """
        ...
    
    def delete_backup(self, backup: MaxINIBackup) -> bool:
        """
        Delete specific backup
        
        Args:
            backup: Backup to delete
            
        Returns:
            True if deleted successfully
        """
        ...
    
    def cleanup_old_backups(self, ini_path: Path) -> int:
        """
        Auto-cleanup old backups (keep max_backups newest)
        
        Args:
            ini_path: Path to 3dsMax.ini
            
        Returns:
            Number of backups deleted
        """
        ...
    
    def verify_backup(self, backup: MaxINIBackup) -> bool:
        """
        Verify backup integrity using checksum
        
        Args:
            backup: Backup to verify
            
        Returns:
            True if backup is valid
        """
        ...
```

**Dependencies**: `pathlib`, `shutil`, `hashlib`, `datetime`

**Example Usage**:

```python
backup_manager = MaxINIBackupManager(max_backups=10)

ini_path = Path("C:/Users/user/AppData/Local/Autodesk/3dsMax/2025/3dsMax.ini")

# Create backup before editing
backup = backup_manager.create_backup(ini_path, reason="manual_edit")
print(f"Backup created: {backup.file_path}")

# List all backups
backups = backup_manager.list_backups(ini_path)
print(f"Total backups: {len(backups)}")
for b in backups:
    print(f"  {b.timestamp}: {b.created_by} ({b.file_size} bytes)")

# Restore from backup
restored_path = backup_manager.restore_backup(backups[0])
print(f"Restored to: {restored_path}")

# Cleanup old backups
deleted_count = backup_manager.cleanup_old_backups(ini_path)
print(f"Deleted {deleted_count} old backups")

# Verify backup integrity
if backup_manager.verify_backup(backups[0]):
    print("Backup is valid")
else:
    print("WARNING: Backup is corrupted!")
```

---

## Module: maxini_editor

**Purpose**: Главный модуль, координация между парсером, пресетами и UI

### API

```python
class MaxINIEditor:
    """Main editor facade"""
    
    def __init__(self,
                 parser: MaxINIParser,
                 preset_manager: MaxINIPresetManager,
                 backup_manager: MaxINIBackupManager,
                 i18n: I18n):
        """
        Initialize editor with dependencies
        
        Args:
            parser: INI parser instance
            preset_manager: Preset manager instance
            backup_manager: Backup manager instance
            i18n: Internationalization instance
        """
        ...
    
    def detect_max_versions(self) -> List[Max3dsVersion]:
        """
        Detect installed 3ds Max versions from Windows Registry
        
        Returns:
            List of detected versions (2020-2025)
        """
        ...
    
    def load_ini(self, version: Max3dsVersion) -> List[MaxINIParameter]:
        """
        Load max.ini for specific Max version
        
        Args:
            version: Max version to load
            
        Returns:
            List of parameters
        """
        ...
    
    def save_ini(self,
                 version: Max3dsVersion,
                 parameters: List[MaxINIParameter],
                 create_backup: bool = True) -> Path | None:
        """
        Save parameters to max.ini
        
        Args:
            version: Max version
            parameters: Parameters to save
            create_backup: Create backup before saving
            
        Returns:
            Backup path if created, None otherwise
        """
        ...
    
    def apply_preset(self,
                     preset: MaxINIPreset,
                     current_parameters: List[MaxINIParameter],
                     version: Max3dsVersion) -> ApplyResult:
        """
        Apply preset with backup and validation
        
        Args:
            preset: Preset to apply
            current_parameters: Current values
            version: Target Max version
            
        Returns:
            Result object with backup_path, updated_parameters, changes
        """
        ...
    
    def search_parameters(self,
                          parameters: List[MaxINIParameter],
                          query: str,
                          language: str = "en") -> List[MaxINIParameter]:
        """
        Search parameters by name or description
        
        Args:
            parameters: List to search
            query: Search query
            language: Search language ("en" or "ru")
            
        Returns:
            Matching parameters
        """
        ...
```

**Dependencies**: All other modules + `winreg`, `logging`

**Example Usage**:

```python
# Initialize dependencies
parser = MaxINIParser(validation_rules_path=Path("data/validation/rules.json"))
preset_mgr = MaxINIPresetManager(
    built_in_dir=Path("data/presets/built-in"),
    user_presets_dir=Path.home() / ".maxmanager" / "presets"
)
backup_mgr = MaxINIBackupManager(max_backups=10)
i18n = I18n(language="ru")

# Create editor
editor = MaxINIEditor(parser, preset_mgr, backup_mgr, i18n)

# Detect Max versions
versions = editor.detect_max_versions()
print(f"Found {len(versions)} 3ds Max installations")

# Load max.ini for Max 2025
max_2025 = next(v for v in versions if v.year == 2025)
parameters = editor.load_ini(max_2025)

# Search parameters
results = editor.search_parameters(parameters, "render", language="ru")
print(f"Found {len(results)} parameters matching 'render'")

# Apply high performance preset
hp_preset = preset_mgr.load_preset("high_performance")
result = editor.apply_preset(hp_preset, parameters, max_2025)
print(f"Applied preset, backup: {result.backup_path}")
print(f"Changed {len(result.changes)} parameters")

# Save changes
backup_path = editor.save_ini(max_2025, result.updated_parameters, create_backup=True)
print(f"Saved with backup: {backup_path}")
```

---

## Error Handling

### Exception Hierarchy

```python
class MaxINIEditorError(Exception):
    """Base exception for MaxINI Editor"""
    pass

class ParsingError(MaxINIEditorError):
    """INI file parsing error"""
    pass

class ValidationError(MaxINIEditorError):
    """Parameter validation error"""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation errors")

class PresetNotFoundError(MaxINIEditorError):
    """Preset not found"""
    pass

class ChecksumError(MaxINIEditorError):
    """Backup checksum mismatch (corrupted file)"""
    pass

class Max3dsNotFoundError(MaxINIEditorError):
    """No 3ds Max installations detected"""
    pass
```

---

## Data Transfer Objects

### ParameterChange

```python
@dataclass
class ParameterChange:
    """Represents a parameter value change"""
    key: str
    old_value: Any
    new_value: Any
    section: str
```

### ApplyResult

```python
@dataclass
class ApplyResult:
    """Result of applying a preset"""
    backup_path: Path
    updated_parameters: List[MaxINIParameter]
    changes: List[ParameterChange]
    timestamp: datetime
```

---

## Summary

**Total Modules**: 4  
**Total Public Methods**: 32  
**Exception Types**: 6  
**DTOs**: 2

**Design Principles**:
- ✅ Single Responsibility: Each module has ONE clear purpose
- ✅ Dependency Injection: All dependencies injected (testable)
- ✅ Type Safety: Full type hints, mypy strict mode
- ✅ Error Handling: Custom exceptions with clear hierarchy
- ✅ Immutability: Dataclasses frozen where possible


