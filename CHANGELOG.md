# Changelog

Все значимые изменения в проекте MaxManager документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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

