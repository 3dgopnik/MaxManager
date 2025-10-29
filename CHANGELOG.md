# Changelog

Все значимые изменения в проекте MaxManager документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed
- **Централизованное версионирование**
  - Создан `src/__version__.py` - единый источник истины для версии
  - Python файлы импортируют: `from src.__version__ import __version__`
  - MaxScript парсит `__version__.py` при запуске
  - Installer читает версию из файла при установке
  - `update_version.py` теперь меняет ТОЛЬКО 1 файл (было 7+)
  - Невозможна рассинхронизация версий
  - Best practice (Django, Flask, FastAPI подход)

### Fixed
- **Size Grip позиционирование**
  - Добавлен showEvent для начального размещения в правом нижнем углу
  - Теперь grip сразу на месте при запуске (не в центре)
  - position_size_grip() вызывается при show и resize

- **Пунктирные обводки на кнопках**
  - setFocusPolicy(Qt.NoFocus) для всех иконок (help, undo, browse, toggle)
  - Добавлен outline: none в CSS для :focus состояния
  - Полностью убраны пунктирные рамки при клике на элементы UI

### Fixed
- **README.md**: Убраны не реализованные фичи
  - Удалено упоминание Hot Reload System (не реализовано)
  - Удалено "Real-time изменения без перезапуска" (нужен перезапуск Max)
  - Удалено упоминание системы пресетов (планируется)
  - Обновлена структура проекта (фактическая)
  - Добавлено предупреждение о необходимости перезапуска 3ds Max
  - Обновлена инструкция использования с описанием Scrubby Sliders

## [0.6.0] - 2025-01-28

### Added
- **Scrubby Sliders для числовых полей** (Professional UI/UX)
  - `ScrubbyIntSpinBox`: Integer поля с drag-to-change функционалом
  - `ScrubbyFloatSpinBox`: Float поля с drag-to-change функционалом
  - Курсор меняется на ⟷ (SizeHorCursor) при наведении
  - **Shift**: медленное изменение (fine control) - 0.1x для int, 0.001x для float
  - **Ctrl**: быстрое изменение - 10x для int, 0.1x для float
  - Поддержка колеса мыши для изменения значений
  - Можно вводить значения вручную с клавиатуры
  - Вдохновлено Blender, Maya, Substance Designer, Figma, After Effects

- **Per-Parameter Undo Buttons**
  - Бордовая иконка ⟲ (#990000) появляется при изменении параметра
  - Кликабельная - откатывает параметр к оригинальному значению
  - Место под кнопку зарезервировано всегда (нет сдвигов layout)
  - Скрыта по умолчанию (прозрачная), видна только при изменении

- **ElidedLabel Widget**
  - Кастомный QLabel с автоматическим обрезанием длинного текста
  - Добавляет "..." в конце если текст не помещается
  - Tooltip показывает полное название параметра

### Fixed
- **Column Width on Resize**: Исправлена проблема обрезки правой колонки
  - Уменьшены минимальные ширины виджетов: label 150→100px, value 80→60px
  - Виджеты теперь могут сжиматься при ресайзе окна
  - Контент адаптируется к доступной ширине

- **Language Switching (EN/RU)**: Исправлен баг переключения языка в UI
  - Проблема: модуль `i18n` импортировался дважды из-за `sys.path.insert`
  - Решение: использованы relative imports (`from ..i18n`)
  - Глобальная переменная `_current_language` синхронизируется между модулями
  - Названия параметров корректно переключаются между языками

- **UI Flickering on Language Change**: Убрано мигание при смене языка
  - `setUpdatesEnabled(False/True)` - один repaint вместо множественных

- **Text Overlap on Path Icons**: Текст не наползает на иконку папки
  - `setTextMargins(3, 0, 34, 0)` для path LineEdit

- **Header Tab Tooltip**: Убран черный прямоугольник при наведении на вкладки

### Changed
- **Vertical Alignment** - "Рваный флаг" исправлен
  - Все лейблы фиксированной ширины **180px** (`LABEL_FIXED_WIDTH`)
  - Текстовые поля выровнены вертикально - чистая линия
  - Длинные названия обрезаются с "..." (ElidedLabel)
  - Tooltip показывает полное название при наведении

- **Unified Numeric Field Width** (Best Practice от Blender/Figma/Unreal)
  - Int поля: 80px → **100px**
  - Float поля: **100px** (было уже)
  - **Все числовые поля одинаковой ширины** для визуальной консистентности

- **Text Fields Stretch** (Best Practice от VS Code/Figma/Adobe)
  - String поля растягиваются до доступной ширины (как path поля)
  - Убраны минимальные ширины - максимальное использование пространства
  - Path поля тоже без minWidth - полное заполнение

- **Scrollbar Styling** - минималистичный дизайн
  - Ширина: 10px → **5px** (как цветовые индикаторы)
  - Цвет: #666666 → **#353535** (очень темный, едва светлее фона #333333)
  - **Всегда видимый** (`ScrollBarAlwaysOn`) - нет скачков контента
  - Прижат к правому краю окна (0px margin)
  - 10px отступ от scrollbar до контента свитков

- **Smart Column Balancing**
  - Вместо простого чередования (0,1,0,1...) используется балансировка по высоте
  - Каждая секция добавляется в более короткую колонку
  - Колонки примерно равной высоты - нет эффекта "потом одна колонка"

- **Footer Button Alignment**
  - Refresh: начинается на 10px (начало левой колонки)
  - Apply: заканчивается на 20px от края (конец правой колонки + scrollbar)
  - Size grip (⤡) в правом нижнем углу для визуальной красоты

- **Search Toggle**
  - Повторное нажатие на иконку 🔍 закрывает поиск (toggle)
  - Убрана дублирующая иконка лупы из окна поиска
  - Только текстовое поле с placeholder и кнопка ✕

- **No Visual Highlights** - чистый минималистичный стиль
  - Убрана желтая подсветка измененных параметров
  - Убрана золотистая обводка при focus (#9C823A → #555555)
  - Изменение показывается только бордовой иконкой ⟲
  - Нет анимаций, нет декораций - профессиональный вид

- **Toggle Alignment**: Все boolean/int/float контролы выровнены справа
  - Layout: `[label] [stretch] [control]` для компактных типов
  - Path/string: `[label] [field with stretch=1]`

- **UI Layout Constants**:
  - `LABEL_FIXED_WIDTH = 180` - фиксированная ширина всех лейблов
  - `PATH_TEXT_RIGHT_MARGIN = 34` - отступ для иконки папки
  - `NUMERIC_FIELD_WIDTH = 100` - унифицированная ширина числовых полей

### Removed
- Старые SpinBox виджеты с кнопками +/- (заменены на Scrubby Sliders)
- Slider для float значений (заменен на Scrubby Float)
- Минимальные ширины для string/path полей (теперь растягиваются)
- Желтая подсветка и золотистая обводка (минимализм)

### Technical
- Новые классы: `ScrubbyIntSpinBox`, `ScrubbyFloatSpinBox`, `ElidedLabel`
- Убраны зависимости от `QSpinBox`, `QDoubleSpinBox`, `QSlider` для числовых полей
- Улучшена обработка mouse events для drag-to-change функционала
- Добавлена поддержка keyboard modifiers (Shift/Ctrl) для precision control

## [0.5.0] - 2025-10-23

### Added
- **Centralized Version Management System**
  - `scripts/update_version.py` - Automatic version synchronization across all files
  - `docs/VERSION_MANAGEMENT.md` - Comprehensive version management guide
  - Updated project constitution with versioning rules
  - Semantic versioning (MAJOR.MINOR.PATCH) implementation

### Changed
- **Project Version**: v1.8.0 → v0.5.0 for proper semantic versioning
- **Application Naming**: "MaxINI Editor" → "MaxManager" throughout all files
- **Version Format**: v0.5.0 → v.0.5.0 (added dot after 'v')
- **Window Title**: Removed version from title, now shows "Advanced MaxManager"
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

### UI Improvements
- **Version Label Positioning**: Moved version label above header tabs with absolute positioning
- **Hover Effect**: Version label can now hover over sidebar button when collapsed
- **Responsive Design**: Version position updates automatically when window resizes
- **Clean Interface**: Removed version from window title for cleaner appearance

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

