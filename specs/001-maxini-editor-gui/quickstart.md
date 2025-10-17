# Quickstart: MaxINI Editor GUI

**Feature**: 001-maxini-editor-gui  
**Date**: 2025-10-17  
**For**: Developers implementing this feature

## Overview

Этот guide поможет начать разработку MaxINI Editor GUI за 10 минут. Пройдёмся от setup до первого working prototype.

**Цель**: Запустить макрос в 3ds Max → открыть Qt окно → отобразить параметры из max.ini

---

## Prerequisites

### Required

- ✅ Python 3.10+ (встроен в 3ds Max 2025)
- ✅ 3ds Max 2024 или 2025 установлен
- ✅ MaxManager project cloned
- ✅ Git configured

### Optional (для development)

- pytest для юнит-тестов
- mypy для type checking
- ruff для linting

---

## Step 1: Environment Setup (2 minutes)

### 1.1 Verify Python in 3ds Max

Открой **3ds Max** → **F11** (MAXScript Listener) → выполни:

```maxscript
python.Execute "import sys; print(sys.version)"
python.Execute "from PySide6 import QtWidgets; print('PySide6 OK')"
```

**Expected output**:
```
3.10.11 (tags/v3.10.11:...) [MSC v.1934 64 bit (AMD64)]
PySide6 OK
```

### 1.2 Clone MaxManager (if not done)

```powershell
cd C:\
git clone https://github.com/3dgopnik/MaxManager.git
cd MaxManager
```

### 1.3 Verify directory structure

```powershell
ls src\modules        # Should exist
ls src\ui             # Should exist
ls src\maxscript      # Should exist
```

---

## Step 2: Create Module Files (3 minutes)

### 2.1 Create maxini_parser.py

```powershell
New-Item -ItemType File -Path src\modules\maxini_parser.py
```

Add minimal code:

```python
"""MaxINI Parser - Parse and validate 3ds Max configuration files"""
from pathlib import Path
from typing import List
import configparser

class MaxINIParser:
    """Parser for max.ini files"""
    
    def load(self, ini_path: Path) -> dict:
        """Load max.ini file"""
        config = configparser.ConfigParser()
        
        # max.ini uses UTF-16 LE encoding
        with open(ini_path, 'r', encoding='utf-16-le') as f:
            config.read_file(f)
        
        return {section: dict(config[section]) 
                for section in config.sections()}
    
    def get_parameter(self, data: dict, section: str, key: str) -> str | None:
        """Get parameter value"""
        return data.get(section, {}).get(key)
```

### 2.2 Create maxini_editor_window.py

```powershell
New-Item -ItemType File -Path src\ui\maxini_editor_window.py
```

Add minimal Qt window:

```python
"""MaxINI Editor GUI - Main Window"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.maxini_parser import MaxINIParser

class MaxINIEditorWindow(QDialog):
    """Main editor window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.parser = MaxINIParser()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle('MaxINI Editor - Quickstart Prototype')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('<h2>MaxINI Editor</h2>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Load button
        load_btn = QPushButton('Load max.ini')
        load_btn.clicked.connect(self.load_ini)
        layout.addWidget(load_btn)
        
        self.setLayout(layout)
        
    def log(self, message: str):
        """Add log message"""
        self.log_text.append(message)
        
    def load_ini(self):
        """Load max.ini file"""
        # Try to find max.ini
        possible_paths = [
            Path.home() / "AppData/Local/Autodesk/3dsMax/2025 - 64bit/ENU/3dsMax.ini",
            Path.home() / "AppData/Local/Autodesk/3dsMax/2024 - 64bit/ENU/3dsMax.ini"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.log(f"✓ Found: {path}")
                try:
                    data = self.parser.load(path)
                    self.log(f"✓ Loaded {len(data)} sections")
                    
                    # Show first 5 parameters
                    for section, params in list(data.items())[:3]:
                        self.log(f"\n[{section}]")
                        for key, value in list(params.items())[:5]:
                            self.log(f"  {key} = {value}")
                    
                    return
                except Exception as e:
                    self.log(f"✗ Error loading: {e}")
        
        self.log("✗ max.ini not found!")
```

---

## Step 3: Create MaxScript Macro (2 minutes)

### 3.1 Create launcher macro

```powershell
New-Item -ItemType File -Path src\maxscript\MaxManager_INIEditor_Quickstart.ms
```

Add macro code:

```maxscript
/*
 * MaxManager INI Editor - Quickstart Launcher
 * Version: 0.1.0
 */

macroScript MaxManager_INIEditor_Quickstart
category:"MaxManager"
buttonText:"INI Editor (QS)"
toolTip:"MaxINI Editor - Quickstart Prototype"
(
    -- Add MaxManager src to Python path
    local maxManagerPath = "C:\\MaxManager\\src"
    python.Execute ("import sys; sys.path.append(r'" + maxManagerPath + "')")
    
    -- Import and launch
    python.Execute "
from PySide6.QtWidgets import QApplication
import qtmax
from ui.maxini_editor_window import MaxINIEditorWindow

# Ensure QApplication exists
app = QApplication.instance()
if app is None:
    app = QApplication([])

# Get Max main window for proper parenting
try:
    max_window = qtmax.GetQMaxMainWindow()
except:
    max_window = None

# Create and show editor
editor = MaxINIEditorWindow(parent=max_window)
editor.show()

print('MaxINI Editor Quickstart launched')
"
    
    format "MaxINI Editor Quickstart macro executed\n"
)
```

### 3.2 Copy to 3ds Max scripts folder

```powershell
$destPath = "$env:LOCALAPPDATA\Autodesk\3dsMax\2025 - 64bit\ENU\scripts\MaxManager\"
New-Item -ItemType Directory -Path $destPath -Force
Copy-Item src\maxscript\MaxManager_INIEditor_Quickstart.ms $destPath -Force
```

---

## Step 4: Test in 3ds Max (3 minutes)

### 4.1 Launch 3ds Max

1. Open **3ds Max 2025**
2. Wait for full load

### 4.2 Run the macro

**Method 1: MAXScript Listener** (F11)

```maxscript
fileIn "C:\\MaxManager\\src\\maxscript\\MaxManager_INIEditor_Quickstart.ms"
```

**Method 2: Search macro**

1. Press **F1** → **Search** → type `MaxManager`
2. Find "INI Editor (QS)"
3. Click to run

### 4.3 Expected result

✅ Qt window opens with title "MaxINI Editor - Quickstart Prototype"  
✅ Button "Load max.ini" visible  
✅ Click button → max.ini loads and displays parameters  
✅ Log shows sections like [Rendering], [Memory], etc.

**Screenshot example**:
```
✓ Found: C:\Users\user\AppData\Local\Autodesk\3dsMax\2025 - 64bit\ENU\3dsMax.ini
✓ Loaded 15 sections

[Rendering]
  RenderThreads = 8
  AutoBackup = 1
  BackupInterval = 10

[Memory]
  DynamicHeapSize = 1
  MemoryPool = 512
```

---

## Step 5: Verify Setup (1 minute)

### 5.1 Check logs

**3ds Max MAXScript Listener** (F11):
```
MaxINI Editor Quickstart launched
MaxINI Editor Quickstart macro executed
```

### 5.2 Troubleshooting

#### Error: "No module named 'modules'"

**Fix**: Check Python path in macro, ensure `C:\MaxManager\src` is added

```maxscript
python.Execute "import sys; print(sys.path)"
```

#### Error: "No module named 'PySide6'"

**Fix**: 3ds Max 2025 должен иметь PySide6 встроенный. Проверь:

```maxscript
python.Execute "from PySide6 import QtWidgets; print('OK')"
```

#### Error: "max.ini not found"

**Fix**: Проверь путь вручную:

```maxscript
python.Execute "
from pathlib import Path
path = Path.home() / 'AppData/Local/Autodesk/3dsMax/2025 - 64bit/ENU/3dsMax.ini'
print(f'Exists: {path.exists()}, Path: {path}')
"
```

---

## Next Steps

### Now you have:

✅ Python modules: `maxini_parser.py`  
✅ Qt GUI: `maxini_editor_window.py`  
✅ MaxScript launcher  
✅ Working prototype in 3ds Max

### What's next:

1. **Add validation** → `validation_rules.json` + validation logic
2. **Add presets** → `maxini_presets.py` + preset files
3. **Add backups** → `maxini_backup.py` + backup management
4. **Improve UI** → categories, search, tooltips
5. **Add i18n** → Russian/English translations
6. **Write tests** → pytest for parser, presets, backups

---

## Development Workflow

### Daily workflow:

1. Edit Python files in `src/modules/` and `src/ui/`
2. Copy MaxScript to Max scripts folder (if changed)
3. Restart 3ds Max (or re-run macro)
4. Test changes
5. Commit when working

### Testing workflow:

```powershell
# Run Python tests
pytest tests/unit/test_maxini_parser.py -v

# Run type checking
mypy src/modules/maxini_parser.py --strict

# Run linting
ruff check src/modules/maxini_parser.py
```

---

## Resources

### Documentation

- [spec.md](./spec.md) - Feature specification
- [data-model.md](./data-model.md) - Data entities
- [contracts/module-api.md](./contracts/module-api.md) - Module interfaces
- [research.md](./research.md) - Research findings

### Autodesk Docs

- [3ds Max Python Help](https://help.autodesk.com/cloudhelp/2025/ENU/MAXDEV-Python/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [MAXScript Reference](https://help.autodesk.com/cloudhelp/2025/ENU/3DSMax-MAXScript/)

### MaxManager

- [Constitution](../../../.specify/memory/constitution.md) - Development principles
- [GitHub Issue #10](https://github.com/3dgopnik/MaxManager/issues/10) - This feature

---

## Summary

**Time to working prototype**: ~10 minutes  
**Files created**: 3 (parser, window, macro)  
**Lines of code**: ~150  
**Result**: Qt window loading and displaying max.ini parameters in 3ds Max

**Next milestone**: Add preset application (button "Apply High Performance")  
**Estimated time**: +30 minutes

---

**Happy coding!** 🚀

Если что-то не работает - проверь [Troubleshooting](#step-5-verify-setup-1-minute) или создай comment в [Issue #10](https://github.com/3dgopnik/MaxManager/issues/10).


