# Changelog

Все значимые изменения в проекте MaxManager документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.5.0] - 2025-10-23

### Added
- **Centralized Version Management System**
  - `scripts/update_version.py` - Automatic version synchronization across all files
  - `docs/VERSION_MANAGEMENT.md` - Comprehensive version management guide
  - Updated project constitution with versioning rules
  - Semantic versioning (MAJOR.MINOR.PATCH) implementation

### Changed
- **Project Version**: v1.8.0 → v0.5.0 for proper semantic versioning
- Updated constitution with centralized versioning principles
- All version numbers synchronized across all project files
- Development workflow updated to include version management

### Fixed
- **Version Synchronization**: All versions now consistent across:
  - Python files (VERSION variable)
  - MaxScript files (headers, comments)
  - Installer messages
  - Test files
  - Documentation files

## [1.8.0] - 2025-10-23

### Added
- **Complete Modern UI Implementation** - Full redesign based on design templates
  - `ModernSidebar`: Collapsible sidebar (80px → 160px) with icon-centered layout
  - `ModernHeader`: Contextual tabs that change based on active sidebar button
  - Version label (v1.8.0) in top-right corner of header
  - QtAwesome icon integration (fa5s.* icons)
  - Individual color indicators for sidebar buttons and header tabs
  - Thin separators (1px, #222222) between all UI elements

### Changed
- **Sidebar Behavior**:
  - Icons stay centered at 40px during expansion (fixed containers)
  - Removed animation jitter, instant expand/collapse
  - Logo button acts as toggle for sidebar expansion
  - Button sizes: 80x80 (collapsed) → 160x80 (expanded)
  - Added individual colors for indicators: #9C823A, #4CAF50, #2196F3, #FF9800, #9C27B0
  
- **Header Behavior**:
  - Tabs positioned 40px from top (aligned with logo bottom)
  - Indicators as separate widgets to prevent text jitter
  - Removed font-weight changes to prevent text shifting
  - Individual indicator colors per tab
  - Increased font size to 18px for better readability
  
- **Interaction**:
  - Removed hover effects on sidebar buttons and header tabs
  - Only click reactions remain
  - Improved click debouncing to prevent double-clicks
  - Removed focus outlines from all buttons and tabs
  - Removed color changes on logo button interaction

### Fixed
- Fixed sidebar button sizing inconsistencies
- Fixed icon/logo movement during sidebar expansion
- Fixed text jitter on header tabs when switching
- Fixed tabs "moving away" when switching sidebar buttons
- Fixed separator uniformity between all elements
- Fixed version label positioning (centered at 20px from top)
- Fixed duplicate tabs issue by replacing QTabWidget with QStackedWidget
- Fixed SVG logo loading with multiple path fallbacks
- Fixed font consistency (all elements use Segoe UI)
- Fixed text flickering by removing thin font variants

## [1.1.3] - 2025-10-23

### Added
- **Modern UI Implementation** - Complete redesign based on design templates
  - `ModernSidebar`: Collapsible sidebar (80px → 160px) with icon-centered layout
  - `ModernHeader`: Contextual tabs that change based on active sidebar button
  - Version label (v1.1.3) in top-right corner of header
  - QtAwesome icon integration (fa5s.* icons)
  - Individual color indicators for sidebar buttons and header tabs
  - Thin separators (1px, #222222) between all UI elements

### Changed
- **Sidebar Behavior**:
  - Icons stay centered at 40px during expansion (fixed containers)
  - Removed animation jitter, instant expand/collapse
  - Logo button acts as toggle for sidebar expansion
  - Button sizes: 80x80 (collapsed) → 160x80 (expanded)
  - Added individual colors for indicators: #9C823A, #4CAF50, #2196F3, #FF9800, #9C27B0
  
- **Header Behavior**:
  - Tabs positioned 40px from top (aligned with logo bottom)
  - Indicators as separate widgets to prevent text jitter
  - Removed font-weight changes to prevent text shifting
  - Individual indicator colors per tab
  
- **Interaction**:
  - Removed hover effects on sidebar buttons and header tabs
  - Only click reactions remain
  - Improved click debouncing to prevent double-clicks

### Fixed
- Fixed sidebar button sizing inconsistencies
- Fixed icon/logo movement during sidebar expansion
- Fixed text jitter on header tabs when switching
- Fixed tabs "moving away" when switching sidebar buttons
- Fixed separator uniformity between all elements
- Fixed version label positioning (centered at 20px from top)

## [0.2.0] - 2025-10-22

### Changed
- **Project Cleanup & Restructure** (Issue #11)
  - Откат на чистое состояние `origin/main`
  - Удаление мусорной ветки `002-ini-viewer-knowledgebase`
  - Удаление устаревших файлов (Force_*.ms, Update_*.ms, specs/, tests/)
  - Обновление Constitution до v1.2.0 с чётким видением проекта
  - Создание нового README.md с описанием модулей
  - Определение архитектуры: MaxManager как набор независимых инструментов

### Removed
- Удалены старые installer скрипты (Force_*, Update_*, Hot_Reload_System.ms)
- Удалены устаревшие спецификации (specs/001-maxini-editor-gui/)
- Удалены старые тесты (tests/)
- Удалены устаревшие UI файлы (maxini_editor_modern.py, maxini_installer.py, simple_mvp.py)
- Удалены pyproject.toml, pytest.ini (будут пересозданы при необходимости)

## [0.1.1] - 2025-10-17

### Added
- **MaxINI Editor Advanced v1.1.1** - Production Ready
  - Custom Presets System (создание, сохранение, экспорт/импорт)
  - Real-time изменения настроек без перезапуска 3ds Max
  - Прямая интеграция с 3ds Max API (pymxs.runtime)
  - 8 основных категорий настроек
  - Hot Reload System для разработки

### Changed
- Улучшен UI дизайн (clean, без emoji)
- Обновлена документация (Constitution v1.1.0)

### Fixed
- Исправлены ошибки API интеграции
- Graceful fallback при недоступности API

## [0.1.0] - 2025-10-15

### Added
- **Seed v0.1** - базовая архитектура проекта
  - Структура проекта (src/, docs/, data/)
  - Core модули (application, config, logger)
  - Базовая MaxScript интеграция
  - Constitution v1.0.0 с core principles

### Added - MaxINI Parser
- Парсинг 3dsmax.ini (UTF-16 LE encoding)
- Валидация параметров
- Knowledge Base система

## [0.0.1] - 2025-10-15

### Added
- Инициализация репозитория
- Базовая структура проекта
- Requirements.txt

---

**Формат версий:** MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: Новые функции (backward compatible)
- **PATCH**: Bug fixes и мелкие улучшения

