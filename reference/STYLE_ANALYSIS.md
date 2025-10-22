# Qt StyleSheet Analysis

## Проанализированные репозитории

### 1. **QSS** (https://github.com/GTRONICK/QSS) ✅
**Статус**: Легковесные готовые стили  
**Что полезно**:
- `MaterialDark.qss` - Material Design темная тема (~400 строк)
- `ElegantDark.qss` - Элегантная темная тема
- `Aqua.qss` - Светлая тема в стиле macOS
- Простые, чистые CSS без зависимостей
- Можно использовать напрямую

**Рекомендация**: ⭐⭐⭐⭐⭐ **ИСПОЛЬЗОВАТЬ** - идеально для нашего случая!

---

### 2. **QDarkStyleSheet** (https://github.com/ColinDuquesnoy/QDarkStyleSheet) ✅
**Статус**: Профессиональная темная тема  
**Что полезно**:
- Очень детальный стиль (~2200 строк)
- Поддержка светлой и темной тем
- Генерация через SCSS
- Полный набор иконок (SVG)
- Цветовая палитра документирована

**Особенности**:
```python
# Использование
import qdarkstyle
app.setStyleSheet(qdarkstyle.load_stylesheet())
```

**Рекомендация**: ⭐⭐⭐⭐ **Можно использовать**, но слишком сложно для простого проекта

---

### 3. **qt-material** (https://github.com/UN-GCPDS/qt-material) ✅
**Статус**: Material Design с темами  
**Что полезно**:
- 27 готовых тем (dark/light варианты)
- Шаблоны на основе XML
- Material Design компоненты
- Динамическая генерация стилей

**Особенности**:
```python
# Использование
from qt_material import apply_stylesheet
apply_stylesheet(app, theme='dark_teal.xml')
```

**Темы**:
- `dark_teal.xml`, `dark_blue.xml`, `dark_amber.xml`
- `light_cyan.xml`, `light_blue.xml`, `light_pink.xml`

**Рекомендация**: ⭐⭐⭐ **Интересно**, но требует библиотеку

---

### 4. **qtawesome** (https://github.com/spyder-ide/qtawesome) ✅
**Статус**: Библиотека иконок  
**Что полезно**:
- FontAwesome иконки для Qt
- Material Design иконки
- Elusive иконки

**Особенности**:
```python
import qtawesome as qta
icon = qta.icon('fa5s.home', color='blue')
button.setIcon(icon)
```

**Рекомендация**: ⭐⭐⭐⭐ **Полезно для иконок**, но требует библиотеку

---

## Рекомендуемое решение для MaxManager

### Вариант 1: **QSS MaterialDark** (простой и эффективный) ⭐⭐⭐⭐⭐
**Преимущества**:
- ✅ Готовый CSS файл (~400 строк)
- ✅ Без внешних зависимостей
- ✅ Material Design стиль
- ✅ Легко модифицировать
- ✅ Поддержка темной/светлой темы

**Реализация**:
```python
# Загрузка стиля из файла
def load_stylesheet(theme='dark'):
    """Load stylesheet from file."""
    style_file = Path(__file__).parent / 'styles' / f'material_{theme}.qss'
    with open(style_file, 'r', encoding='utf-8') as f:
        return f.read()

# Применение
self.setStyleSheet(load_stylesheet('dark'))
```

**Файлы для добавления**:
```
src/
  ui/
    styles/
      material_dark.qss     # Темная тема
      material_light.qss    # Светлая тема
      fluent_dark.qss       # Fluent Design темная
      fluent_light.qss      # Fluent Design светлая
```

---

### Вариант 2: **Встроенный CSS в Python** (текущий) ⭐⭐⭐
**Преимущества**:
- ✅ Все в одном файле
- ✅ Без внешних зависимостей
- ❌ Труднее поддерживать
- ❌ Нельзя легко переключать темы

---

### Вариант 3: **QDarkStyleSheet** (профессиональный) ⭐⭐⭐⭐
**Преимущества**:
- ✅ Очень качественный стиль
- ✅ Поддержка светлой/темной темы
- ✅ Полный набор иконок
- ❌ Требует установку библиотеки
- ❌ Избыточно для простого проекта

---

## Итоговая рекомендация

### 🎯 Рекомендую: **QSS MaterialDark**

**Почему**:
1. **Простота** - один CSS файл без зависимостей
2. **Качество** - профессиональный Material Design
3. **Гибкость** - легко модифицировать и расширять
4. **Совместимость** - работает с любой версией Qt
5. **Производительность** - загружается мгновенно

**Что делаем**:
1. Копируем `MaterialDark.qss` в `src/ui/styles/material_dark.qss`
2. Адаптируем под Fluent Design (светлые акценты)
3. Создаем светлую тему `material_light.qss`
4. Добавляем автоопределение темы из 3ds Max
5. Храним стили в отдельных файлах для легкой модификации

**Структура**:
```
src/
  ui/
    styles/
      material_dark.qss       # Основная темная тема
      material_light.qss      # Основная светлая тема
      fluent_accents.qss      # Fluent акценты (яркие цвета)
      base_reset.qss          # Базовый сброс стилей
```

---

## Следующие шаги

1. ✅ Скопировать `MaterialDark.qss` из QSS
2. ✅ Адаптировать под наш дизайн (синие акценты #0078d4)
3. ✅ Создать светлую версию
4. ✅ Интегрировать в `maxini_editor_advanced.py`
5. ✅ Добавить автоопределение темы 3ds Max
6. ✅ Протестировать в 3ds Max 2025

---

## Цветовая палитра для MaxManager

### Темная тема (по умолчанию)
```css
/* Основные цвета */
--bg-primary: #1e1d23;          /* Основной фон */
--bg-secondary: #2b2a31;        /* Вторичный фон */
--text-primary: #ffffff;        /* Основной текст */
--text-secondary: #a9b7c6;      /* Вторичный текст */

/* Акценты (Fluent Design) */
--accent-primary: #0078d4;      /* Синий акцент */
--accent-hover: #106ebe;        /* Синий при наведении */
--accent-pressed: #005a9e;      /* Синий при нажатии */
--accent-disabled: #0078d440;   /* Синий неактивный */

/* Статусные цвета */
--success: #00aa00;             /* Успех */
--warning: #ffaa00;             /* Предупреждение */
--error: #e81123;               /* Ошибка */
--info: #0078d4;                /* Информация */
```

### Светлая тема
```css
/* Основные цвета */
--bg-primary: #f3f3f3;          /* Основной фон */
--bg-secondary: #ffffff;        /* Вторичный фон */
--text-primary: #000000;        /* Основной текст */
--text-secondary: #323130;      /* Вторичный текст */

/* Акценты (те же) */
--accent-primary: #0078d4;
--accent-hover: #106ebe;
--accent-pressed: #005a9e;
```

---

## Reference структура

```
reference/
  QSS/                          # ✅ Легковесные стили
    MaterialDark.qss
    ElegantDark.qss
    Aqua.qss
  
  QDarkStyleSheet/              # ✅ Профессиональная темная тема
    qdarkstyle/
      dark/darkstyle.qss
      light/lightstyle.qss
  
  qt-material/                  # ✅ Material Design темы
    qt_material/
      themes/
        dark_teal.xml
        light_cyan.xml
  
  qtawesome/                    # ✅ Библиотека иконок
  
  ps/                           # ? Photoshop файлы
  PruneScene_extracted/         # ? MaxScript плагин
```

