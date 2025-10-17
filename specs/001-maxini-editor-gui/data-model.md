# Data Model: MaxINI Editor GUI

**Feature**: 001-maxini-editor-gui  
**Date**: 2025-10-17  
**Source**: [spec.md Key Entities](./spec.md#key-entities)

## Overview

MaxINI Editor работает с 4 основными сущностями:
1. **MaxINIParameter** - отдельный параметр из max.ini
2. **MaxINIPreset** - набор параметров (встроенный или пользовательский)
3. **MaxINIBackup** - резервная копия файла
4. **Max3dsVersion** - установленная версия 3ds Max

## Entities

### 1. MaxINIParameter

**Purpose**: Представляет один параметр из max.ini с его метаданными и валидацией

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | `str` | ✅ Yes | Имя параметра (e.g., "RenderThreads") |
| `value` | `str \| int \| bool \| Path` | ✅ Yes | Текущее значение параметра |
| `type` | `ParamType` | ✅ Yes | Enum: `STRING \| INT \| BOOL \| PATH` |
| `category` | `ParamCategory` | ✅ Yes | Enum: `RENDERING \| MEMORY \| PATHS \| UI \| PLUGINS \| NETWORK \| PERFORMANCE` |
| `section` | `str` | ✅ Yes | INI section name (e.g., "[Rendering]") |
| `description_ru` | `str` | No | Описание параметра на русском |
| `description_en` | `str` | No | Описание параметра на английском |
| `validation` | `ValidationRule` | No | Правила валидации (min/max/regex) |
| `default_value` | `Any` | No | Значение по умолчанию |
| `unit` | `str` | No | Единица измерения (e.g., "MB", "threads") |

**Validation Rules**:

```python
@dataclass
class ValidationRule:
    min_value: Optional[int] = None          # For INT type
    max_value: Optional[int] = None          # For INT type
    regex_pattern: Optional[str] = None      # For STRING type
    must_exist: bool = False                 # For PATH type
    allowed_values: Optional[List[str]] = None  # Enum values
```

**Example**:

```python
parameter = MaxINIParameter(
    key="RenderThreads",
    value=8,
    type=ParamType.INT,
    category=ParamCategory.RENDERING,
    section="Rendering",
    description_ru="Количество потоков рендеринга",
    description_en="Number of render threads",
    validation=ValidationRule(min_value=1, max_value=128),
    default_value="auto",
    unit="threads"
)
```

**State Transitions**: 
- Immutable (параметры не меняют тип/категорию)
- Only `value` changes during editing

**Relationships**:
- Belongs to **MaxINIPreset** (many-to-many)
- Loaded from **Max3dsVersion**'s max.ini file

---

### 2. MaxINIPreset

**Purpose**: Набор параметров для быстрого применения конфигурации

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `str` | ✅ Yes | Уникальное имя пресета |
| `description_ru` | `str` | ✅ Yes | Описание на русском |
| `description_en` | `str` | ✅ Yes | Описание на английском |
| `author` | `PresetAuthor` | ✅ Yes | Enum: `BUILT_IN \| USER` |
| `parameters` | `List[PresetParameter]` | ✅ Yes | Список параметров (key + value) |
| `tags` | `List[str]` | No | Теги (e.g., ["renderer", "arnold", "performance"]) |
| `created_at` | `datetime` | No | Дата создания (for USER presets) |
| `modified_at` | `datetime` | No | Дата изменения (for USER presets) |
| `file_path` | `Path` | No | Путь к JSON файлу (for USER presets) |

**Nested Type**:

```python
@dataclass
class PresetParameter:
    key: str               # Parameter name (e.g., "RenderThreads")
    value: Any             # Value to set
    section: str           # INI section (e.g., "Rendering")
```

**Example (Built-in)**:

```python
preset = MaxINIPreset(
    name="high_performance",
    description_ru="Высокая производительность",
    description_en="High Performance",
    author=PresetAuthor.BUILT_IN,
    parameters=[
        PresetParameter("RenderThreads", "auto", "Rendering"),
        PresetParameter("UseAllCores", 1, "Performance"),
        PresetParameter("ViewportPerformanceMode", 1, "UI")
    ],
    tags=["performance", "viewport", "speed"]
)
```

**Example (User)**:

```python
preset = MaxINIPreset(
    name="my_arnold_setup",
    description_ru="Моя настройка Arnold",
    description_en="My Arnold Setup",
    author=PresetAuthor.USER,
    parameters=[...],
    tags=["arnold", "custom"],
    created_at=datetime.now(),
    file_path=Path("~/.maxmanager/presets/my_arnold_setup.json")
)
```

**State Transitions**:

```
BUILT_IN: Created (immutable) → Cannot be modified or deleted
USER:     Created → Modified → Deleted
```

**Relationships**:
- Contains **PresetParameter** (composition)
- Can be applied to **Max3dsVersion**

---

### 3. MaxINIBackup

**Purpose**: Резервная копия max.ini файла

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | `datetime` | ✅ Yes | Время создания бэкапа |
| `file_path` | `Path` | ✅ Yes | Путь к backup файлу |
| `original_path` | `Path` | ✅ Yes | Путь к оригинальному max.ini |
| `file_size` | `int` | ✅ Yes | Размер файла в байтах |
| `checksum` | `str` | ✅ Yes | SHA256 hash для проверки целостности |
| `created_by` | `str` | No | Причина создания (e.g., "preset_applied", "manual_edit") |

**Example**:

```python
backup = MaxINIBackup(
    timestamp=datetime(2025, 10, 17, 10, 30, 15),
    file_path=Path("3dsMax.ini.backup.20251017_103015"),
    original_path=Path("%LOCALAPPDATA%/Autodesk/3dsMax/2025/3dsMax.ini"),
    file_size=45678,
    checksum="a1b2c3d4...",
    created_by="preset_applied:high_performance"
)
```

**State Transitions**:

```
Created → (Aged) → Deleted (auto-cleanup when > 10 backups)
```

**Business Rules**:
- Maximum 10 backups per max.ini file
- Auto-cleanup deletes oldest backups
- Backups are read-only after creation

**Relationships**:
- Belongs to **Max3dsVersion** (one-to-many)

---

### 4. Max3dsVersion

**Purpose**: Установленная версия 3ds Max на машине пользователя

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | `int` | ✅ Yes | Год версии (2020-2025) |
| `ini_path` | `Path` | ✅ Yes | Полный путь к 3dsMax.ini |
| `bitness` | `Bitness` | ✅ Yes | Enum: `BIT_64` (only 64-bit supported) |
| `language` | `str` | ✅ Yes | Код языка (e.g., "ENU", "RUS") |
| `install_path` | `Path` | No | Путь к установке Max (e.g., "C:/Program Files/Autodesk/3ds Max 2025") |
| `is_running` | `bool` | No | Запущен ли Max сейчас (для conflict detection) |

**Example**:

```python
version = Max3dsVersion(
    year=2025,
    ini_path=Path("C:/Users/user/AppData/Local/Autodesk/3dsMax/2025 - 64bit/ENU/3dsMax.ini"),
    bitness=Bitness.BIT_64,
    language="ENU",
    install_path=Path("C:/Program Files/Autodesk/3ds Max 2025"),
    is_running=False
)
```

**State Transitions**: Immutable (detected from system)

**Business Rules**:
- Auto-detected via Windows Registry (`HKLM\SOFTWARE\Autodesk\3dsMax\<version>`)
- Only 64-bit versions supported
- Must have read/write access to `ini_path`

**Relationships**:
- Has many **MaxINIBackup** (one-to-many)
- Loads **MaxINIParameter** from its ini_path

---

## Relationships Diagram

```
Max3dsVersion (1) ──┬──> (N) MaxINIBackup
                    │
                    └──> (N) MaxINIParameter [loaded from ini]
                             ↑
                             │ (M:N)
                             │
                    MaxINIPreset (1) ──> (N) PresetParameter
```

**Legend**:
- `(1) ──> (N)` - One-to-Many
- `(M:N)` - Many-to-Many
- `[loaded from ini]` - Dynamically loaded, not persisted

---

## Data Flow

### 1. Loading max.ini

```
Max3dsVersion.ini_path
    ↓ read file (UTF-16 LE)
Parse with configparser
    ↓
Create MaxINIParameter for each key
    ↓ group by category
Display in UI (grouped tabs/sections)
```

### 2. Applying Preset

```
User selects MaxINIPreset
    ↓
Show preview (diff current vs preset)
    ↓ User confirms
Create MaxINIBackup (before changes)
    ↓
Update MaxINIParameter values from PresetParameter
    ↓
Validate all parameters
    ↓ if valid
Write to max.ini (UTF-16 LE)
    ↓
Log change to MaxManager logger
```

### 3. Creating User Preset

```
User edits parameters in UI
    ↓ clicks "Save as Preset"
Collect current MaxINIParameter values
    ↓
Convert to PresetParameter list
    ↓
Create MaxINIPreset (author=USER)
    ↓
Serialize to JSON
    ↓
Write to ~/.maxmanager/presets/<name>.json
```

---

## Validation Rules

### Parameter Validation

```python
def validate_parameter(param: MaxINIParameter) -> List[ValidationError]:
    errors = []
    
    # Type validation
    if param.type == ParamType.INT:
        if not isinstance(param.value, int):
            errors.append(f"{param.key}: must be integer")
    
    # Range validation
    if param.validation and param.validation.min_value:
        if param.value < param.validation.min_value:
            errors.append(f"{param.key}: min value is {param.validation.min_value}")
    
    # Path validation
    if param.type == ParamType.PATH:
        path = Path(param.value)
        if param.validation and param.validation.must_exist:
            if not path.exists():
                errors.append(f"{param.key}: path does not exist")
    
    return errors
```

### Preset Validation

```python
def validate_preset(preset: MaxINIPreset) -> List[ValidationError]:
    errors = []
    
    # Name validation
    if not preset.name or len(preset.name) < 3:
        errors.append("Preset name must be at least 3 characters")
    
    # Parameters validation
    if not preset.parameters:
        errors.append("Preset must have at least one parameter")
    
    # Duplicate keys check
    keys = [p.key for p in preset.parameters]
    if len(keys) != len(set(keys)):
        errors.append("Preset has duplicate parameter keys")
    
    return errors
```

---

## File Formats

### User Preset JSON

```json
{
  "name": "my_arnold_setup",
  "description_ru": "Моя настройка Arnold",
  "description_en": "My Arnold Setup",
  "author": "USER",
  "parameters": [
    {
      "key": "RenderThreads",
      "value": 16,
      "section": "Rendering"
    },
    {
      "key": "DefaultRenderer",
      "value": "Arnold",
      "section": "Rendering"
    }
  ],
  "tags": ["arnold", "custom"],
  "created_at": "2025-10-17T10:30:15",
  "modified_at": "2025-10-17T11:45:22"
}
```

### Validation Rules JSON

```json
{
  "RenderThreads": {
    "type": "INT",
    "min": 1,
    "max": 128,
    "default": "auto",
    "description_ru": "Количество потоков рендеринга",
    "description_en": "Number of render threads",
    "category": "RENDERING",
    "unit": "threads"
  },
  "MemoryPool": {
    "type": "INT",
    "min": 128,
    "max": 8192,
    "default": 512,
    "description_ru": "Размер пула памяти",
    "description_en": "Memory pool size",
    "category": "MEMORY",
    "unit": "MB"
  }
}
```

---

## Summary

**Total Entities**: 4  
**Total Relationships**: 3  
**File Formats**: 2 (JSON)  
**Validation Rules**: Extensible via JSON schema

**Design Decisions**:
- ✅ Immutable entities where possible (Max3dsVersion, built-in presets)
- ✅ Validation rules in separate JSON (extensible without code changes)
- ✅ Strong typing with Python dataclasses + type hints
- ✅ Clear separation: config (JSON) vs runtime (Python objects)


