# Implementation Plan: MaxINI Editor GUI

**Branch**: `001-maxini-editor-gui` | **Date**: 2025-10-17 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-maxini-editor-gui/spec.md`  
**GitHub Issue**: [#10](https://github.com/3dgopnik/MaxManager/issues/10)

## Summary

MaxINI Editor GUI - графический редактор файла конфигурации 3ds Max (max.ini) с предустановленными пресетами и подсказками на русском/английском языках. Пользователь запускает макрос из 3ds Max, открывается Qt окно (PySide6) с параметрами сгруппированными по категориям. Может применять готовые пресеты (High Performance, Arnold, V-Ray, etc.) или создавать собственные. Все изменения валидируются и бэкапятся перед сохранением.

**Technical Approach**: MaxScript макрос → Python модуль с PySide6 Qt GUI → парсинг INI через configparser → валидация через JSON схему → сохранение с автоматическим бэкапом.

**Primary Value**: Сокращение времени настройки 3ds Max на 70% (5 минут vs 15+), 0 случаев повреждения файла, применение пресета за < 30 секунд.

## Technical Context

**Language/Version**: Python 3.10+ (встроен в 3ds Max 2025)  
**Primary Dependencies**: 
- PySide6 (встроен в 3ds Max 2025, qtmax module)
- configparser (Python stdlib)
- winreg (Python stdlib для реестра Windows)
- MaxManager existing: config, logger, theme_loader

**Storage**: File system (max.ini, пресеты в JSON, бэкапы с timestamp)  
**Testing**: 
- Python: pytest для бизнес-логики (парсинг, валидация, бэкапы)
- MaxScript: ручное тестирование пользователем (макрос, Qt GUI интеграция)

**Target Platform**: Windows 10/11 (3ds Max 2020-2025, focus на 2024-2025)  
**Project Type**: Single module (Python модуль + MaxScript entry point)  
**Performance Goals**: 
- Открытие редактора < 2 сек
- Парсинг max.ini (до 5MB) < 2 сек
- Применение пресета < 30 сек (включая сохранение + бэкап)
- UI отклик < 100ms на действия пользователя

**Constraints**: 
- max.ini читается 3ds Max при ЗАПУСКЕ → изменения требуют ПЕРЕЗАПУСКА Max (определится экспериментом)
- Encoding: UTF-16-LE (стандарт для max.ini)
- MaxScript single-threaded → Python Qt должен запускаться асинхронно
- Должен работать внутри 3ds Max (не standalone)

**Scale/Scope**: 
- ~50-100 параметров в max.ini для отображения
- 5 встроенных пресетов + unlimited пользовательских
- 10 бэкапов max (auto-cleanup старых)
- 2 языка интерфейса (RU/EN)
- Поддержка 6 версий 3ds Max (2020-2025)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Core Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Модульная архитектура** | ✅ PASS | Новый модуль `maxini_editor` в `src/modules/`, самодостаточный с четким назначением |
| **II. Python + MaxScript интеграция** | ✅ PASS | Python: Qt GUI + бизнес-логика, MaxScript: entry point макрос. Четкое разделение |
| **III. Test-First (TDD)** | ✅ PASS | Pytest для Python (парсинг, валидация, I/O), MaxScript тестируется пользователем |
| **IV. Интеграция с 3ds Max** | ✅ PASS | Макрос в категории MaxManager, авто-копирование в Scripts/MaxManager/, версионирование |
| **V. Качество кода** | ✅ PASS | Ruff + Mypy + pre-commit, type hints обязательны, docstrings для всех функций |
| **VI. Документация** | ✅ PASS | Документация на RU (docs/), код на EN, changelog + tasktracker обновляются |
| **VII. GitHub Integration** | ✅ PASS | Issue #10 создан, прогресс в комментариях, PR closes #10 |

### ✅ Tech Stack Compliance

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Python | 3.10+ | 3.10+ (Max 2025) | ✅ PASS |
| GUI | PySide6 | PySide6 (qtmax) | ✅ PASS |
| Logging | Structured | Переиспользуем MaxManager logger | ✅ PASS |
| Config | YAML/JSON | JSON для пресетов + validation rules | ✅ PASS |
| MaxScript | Category MaxManager | MaxManager_INIEditor макрос | ✅ PASS |

### ✅ Quality Gates

**Перед коммитом**:
- [x] Issue #10 создан
- [ ] Документация обновлена (после реализации)
- [ ] Type hints + docstrings (при реализации)
- [ ] Ruff/Mypy проходят (при реализации)

**Complexity Justification**: N/A - нет нарушений constitution

## Project Structure

### Documentation (this feature)

```
specs/001-maxini-editor-gui/
├── spec.md              # ✅ Created (feature specification)
├── checklists/          # ✅ Created
│   └── requirements.md  # ✅ Spec quality checklist (32/32 passed)
├── plan.md              # 🔄 This file (implementation plan)
├── research.md          # 📝 Phase 0 output (NEXT)
├── data-model.md        # 📝 Phase 1 output
├── quickstart.md        # 📝 Phase 1 output
├── contracts/           # 📝 Phase 1 output (API schemas)
└── tasks.md             # 📝 Phase 2 output (/MaxManager.tasks command)
```

### Source Code (repository root)

```
MaxManager/
├── src/
│   ├── modules/
│   │   ├── maxini_editor.py        # 🆕 Main editor module
│   │   ├── maxini_parser.py        # 🆕 INI parsing + validation
│   │   ├── maxini_presets.py       # 🆕 Preset management
│   │   └── maxini_backup.py        # 🆕 Backup management
│   ├── ui/
│   │   ├── maxini_editor_window.py # 🆕 Qt main window
│   │   ├── maxini_widgets.py       # 🆕 Custom Qt widgets
│   │   └── theme_loader.py         # ♻️ Reuse existing
│   ├── core/
│   │   ├── config.py               # ♻️ Reuse for user settings
│   │   └── logger.py               # ♻️ Reuse for logging
│   └── maxscript/
│       ├── MaxManager_INIEditor.ms # 🆕 Production macro
│       └── MaxManager_INIEditor_Test.ms # ✅ Test prototype (exists)
├── data/
│   ├── presets/
│   │   └── built-in/               # 🆕 High Performance, Arnold, V-Ray, etc.
│   ├── validation/
│   │   └── rules.json              # 🆕 Parameter validation schema
│   └── translations/
│       └── maxini_i18n.json        # 🆕 RU/EN translations
├── tests/
│   ├── unit/
│   │   ├── test_maxini_parser.py   # 🆕 INI parsing tests
│   │   ├── test_maxini_presets.py  # 🆕 Preset logic tests
│   │   └── test_maxini_backup.py   # 🆕 Backup management tests
│   └── integration/
│       └── test_maxini_editor_integration.py # 🆕 Full workflow test
└── docs/
    ├── maxini_editor_guide.md      # 🆕 User guide RU
    └── maxini_parameters_ref.md    # 🆕 Parameters reference

Legend:
🆕 New file/directory
♻️ Reuse existing
✅ Already exists
📝 To be created
🔄 Current file
```

**Structure Decision**: Single project structure выбран потому что:
1. MaxINI Editor - это модуль в составе MaxManager, не отдельное приложение
2. Переиспользуем существующую инфраструктуру (config, logger, theme_loader)
3. MaxScript макрос вызывает Python модуль напрямую через `python.Execute`
4. Нет backend/frontend разделения - всё работает локально

## Complexity Tracking

*No Constitution violations - table not needed*

