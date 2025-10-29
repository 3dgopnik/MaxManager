# 📋 MaxManager Version Management

## 🎯 Единый источник истины для версии

С версии 0.6.0 используется **централизованное версионирование** через единственный файл.

### Где находится версия

**ЕДИНСТВЕННОЕ МЕСТО:**
```python
src/__version__.py
```

```python
"""
MaxManager Version
Single source of truth for version across all files.
"""

__version__ = "0.6.0"  # ← МЕНЯЙ ТОЛЬКО ЗДЕСЬ
```

### Как все файлы получают версию

**Python файлы** - импортируют:
```python
from src.__version__ import __version__

version_label = QLabel(f"v.{__version__}")
```

**MaxScript макрос** - читает при запуске:
```maxscript
python.Execute "from __version__ import __version__"
local version = python.getVar "MAXMANAGER_VERSION"
```

**Installer** - парсит файл при установке:
```maxscript
-- Reads __version__.py and extracts version string
```

## 🚀 Как обновить версию

### Автоматический способ (рекомендуется)

```bash
python scripts/update_version.py 0.7.0
```

Скрипт обновит **только** `src/__version__.py`.

### Ручной способ

1. Открой `src/__version__.py`
2. Измени `__version__ = "0.6.0"` на нужную версию
3. Сохрани
4. Готово! Все файлы автоматически получат новую версию

## ✅ Преимущества

- ✅ **Одно место** для изменения
- ✅ **Нет рассинхронизации** - невозможно забыть файл
- ✅ **Простой скрипт** - меняет только 1 файл
- ✅ **Best practice** - как в Django, Flask, FastAPI
- ✅ **Импорты всегда актуальны** - нет hardcoded версий

## 🔍 Где отображается версия

1. **UI Label** (правый верхний угол): `v.0.6.0`
2. **Installer Dialog**: `MaxManager v.0.6.0 installed successfully!`
3. **MaxScript Logs**: `Launching MaxManager Canvas Test v.0.6.0...`
4. **README.md**: Вручную обновляется в разделе "Текущая версия"

## 📜 История изменений

- **v0.6.0**: Переход на централизованное версионирование
- **v0.5.0**: Использовались множественные места и regex скрипт
- **v1.8.0**: Еще более распределенная система

## ⚠️ Важно

После изменения версии:
1. Коммит: `git commit -m "chore: bump version to X.Y.Z"`
2. Тест в 3ds Max
3. Push после подтверждения пользователя
