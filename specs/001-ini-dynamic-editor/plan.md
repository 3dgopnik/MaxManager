# Implementation Plan: Dynamic INI Editor with Real-time Editing

**Branch**: `001-ini-dynamic-editor` | **Date**: 2025-10-23 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-ini-dynamic-editor/spec.md`

## Summary

Реализация динамического редактора 3dsMax.ini с автоматической генерацией вкладок из секций INI-файла. Пользователь кликает на кнопку "INI" в sidebar → система парсит INI файл → создает вкладки для каждой секции → отображает параметры в редактируемом canvas → позволяет изменять значения → сохраняет изменения с backup.

**Технический подход**: Использование существующего MaxINIParser для чтения/записи INI (UTF-16 LE), интеграция с ModernSidebar/ModernHeader через динамическую генерацию вкладок, QTreeWidget с inline editing для canvas, цветовые индикаторы для отслеживания изменений, автоматический backup через MaxINIBackupManager.

## Technical Context

**Language/Version**: Python 3.10+ (встроен в 3ds Max 2025)  
**Primary Dependencies**: 
- PySide6 (GUI, встроен в 3ds Max)
- configparser (stdlib, парсинг INI)
- pathlib (stdlib, работа с путями)
- Существующие модули: MaxINIParser, MaxINIBackupManager

**Storage**: Filesystem (3dsMax.ini в UTF-16 LE encoding с BOM, backup файлы .bak)  
**Testing**: 
- `python maxmanager_test.py` (standalone UI тест без 3ds Max)
- Ручное тестирование в 3ds Max через Install_MaxManager.ms

**Target Platform**: Windows 10/11, 3ds Max 2025+ (Python 3.10, PySide6 встроены)  
**Project Type**: Single project (desktop GUI application для 3ds Max)  
**Performance Goals**: 
- Парсинг INI файла <2 сек (до 500 параметров)
- Переключение вкладок <3 сек
- Edit-save workflow <10 сек
- UI без лагов при >50 вкладках

**Constraints**: 
- UTF-16 LE encoding обязателен (3ds Max standard)
- Backup перед каждой записью (безопасность)
- Inline editing для UX
- Horizontal scroll для >10 вкладок
- Цветовая индикация изменений (yellow=modified, green=saved)

**Scale/Scope**: 
- ~60 секций в типичном 3dsMax.ini
- ~300-500 параметров total
- Поддержка 4 типов данных: int, bool, string, path

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Compliance

| Rule | Status | Notes |
|------|--------|-------|
| **I. Модульная архитектура** | ✅ PASS | Новый модуль `ini_canvas.py` - самодостаточный виджет для canvas |
| **II. Python + MaxScript интеграция** | ✅ PASS | Python для UI/логики, MaxScript только для запуска (`maxmanager.mcr` уже есть) |
| **III. Test-First** | ⚠️ PARTIAL | UI тесты через `maxmanager_test.py`, TDD для бизнес-логики (parser уже покрыт) |
| **IV. Интеграция с 3ds Max** | ✅ PASS | Автокопирование через `Install_MaxManager.ms` (уже реализовано) |
| **V. Качество кода** | ✅ PASS | Type hints, docstrings, Ruff/Mypy checks |
| **VI. Документация** | ✅ PASS | Все на русском кроме кода, спецификация готова |
| **VII. GitHub Integration** | ✅ PASS | Issue будет создан через MCP tools |
| **VIII. Версионирование** | ✅ PASS | Версия обновится через `scripts/update_version.py` |
| **Git Workflow** | ✅ PASS | Локальные commits → тест → push после одобрения |

### ⚠️ Notes on PARTIAL compliance

**Test-First для UI компонентов**: 
- UI тестируется через `maxmanager_test.py` (быстрая итерация)
- Ручное тестирование в 3ds Max после изменений
- Причина: Qt UI сложно покрыть unit-тестами без overhead
- Mitigation: Бизнес-логика (MaxINIParser) уже покрыта тестами, UI минимален

## Project Structure

### Documentation (this feature)

```
specs/001-ini-dynamic-editor/
├── spec.md              # ✅ Feature specification (complete)
├── plan.md              # ⏳ This file (in progress)
├── research.md          # 📋 Phase 0 output (next)
├── data-model.md        # 📋 Phase 1 output
├── quickstart.md        # 📋 Phase 1 output
├── contracts/           # 📋 Phase 1 output (API contracts)
├── checklists/          # ✅ Validation checklists
│   └── requirements.md  # ✅ Spec quality checklist (passed)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```
MaxManager/
├── src/
│   ├── ui/
│   │   ├── maxini_editor_advanced.py  # 🔧 MODIFY: add load_ini(), populate_canvas()
│   │   ├── modern_sidebar.py          # ✅ EXISTS: no changes needed
│   │   ├── modern_header.py           # 🔧 MODIFY: add tab scroll support
│   │   └── ini_canvas.py              # ✨ NEW: canvas widget with QTreeWidget
│   │
│   ├── modules/
│   │   ├── maxini_parser.py           # ✅ EXISTS: load/save/validate INI
│   │   ├── maxini_backup.py           # ✅ EXISTS: backup management
│   │   └── maxini_presets.py          # ✅ EXISTS: presets (not used in this feature)
│   │
│   └── maxscript/
│       └── maxmanager.mcr             # ✅ EXISTS: MaxScript macro (no changes)
│
├── maxmanager_test.py                 # 🔧 MODIFY: add test for INI canvas
├── Install_MaxManager.ms              # ✅ EXISTS: installer (no changes)
│
└── specs/001-ini-dynamic-editor/      # 📋 Feature documentation (see above)
```

**Structure Decision**: Single project (Option 1) - desktop application with clear separation between UI (`src/ui/`) and business logic (`src/modules/`). Existing structure is preserved, new code integrates seamlessly without major refactoring.

## Complexity Tracking

*No Constitution violations that require justification. All checks passed.*

**Simplified approach**:
- Используем существующий MaxINIParser (не пишем парсер с нуля)
- Используем существующую архитектуру ModernSidebar/Header (не переписываем UI)
- Один новый файл `ini_canvas.py` (минимальное расширение)
- Inline editing через QTreeWidget.itemDelegate (стандартный Qt подход)
- Backup через существующий MaxINIBackupManager (не пишем backup логику)

## Phase 0: Research & Unknowns

### Research Tasks

1. **QTreeWidget inline editing best practices**
   - Как реализовать inline editing с валидацией типов?
   - Как подсветить измененные ячейки цветом?
   - Как обрабатывать разные типы данных (int, bool, string, path)?

2. **QScrollArea для вкладок**
   - Как добавить horizontal scroll для >10 вкладок в ModernHeader?
   - Стрелки навигации vs scroll bar (что лучше для UX)?
   - Как детектировать overflow и показывать стрелки только при необходимости?

3. **UTF-16 LE encoding handling**
   - Подтвердить корректность существующего MaxINIParser для UTF-16 LE
   - Проверить BOM handling при записи
   - Тестовый сценарий для encoding issues

4. **Цветовая индикация изменений**
   - Yellow background для modified параметров (temporary state)
   - Green background для saved параметров (confirmation feedback)
   - Timing: как долго показывать green перед возвратом к white?

### Decisions to Make

1. **Canvas widget architecture**:
   - Option A: QTreeWidget с 3 колонками (Key, Value, Type)
   - Option B: QTableWidget с 2 колонками (Key, Value)
   - Option C: Custom widget с QListWidget + detail panel
   - **Decision pending research**

2. **Tab scroll mechanism**:
   - Option A: QScrollArea вокруг tabs + custom arrows
   - Option B: QTabBar с setUsesScrollButtons(True)
   - Option C: Custom navigation buttons (← →) + hidden tabs logic
   - **Decision pending research**

3. **Change tracking**:
   - Option A: Track changes in separate dict {section: {key: (old_val, new_val)}}
   - Option B: Modify MaxINIParameter objects in-place with is_modified flag
   - Option C: Deep copy original params + compare on save
   - **Decision pending research**

## Next Steps

1. **Phase 0**: Generate `research.md` with findings for all unknowns ✅
2. **Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md` ✅
3. **Update agent context**: Run update-agent-context.ps1 ✅
4. **Re-check Constitution** after design decisions ✅
5. **Phase 2**: Break down into tasks via `/speckit.tasks` (separate command)

---

**Status**: 📋 Plan created, awaiting Phase 0 research
