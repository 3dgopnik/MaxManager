# MaxManager Ultimate INI Parameters Database v2.0

## 📊 Статистика

- **Всего параметров**: 796
- **Schema версия**: 2.0.0
- **Создан**: 2025-10-29
- **Источники**:
  - maxini_master_verified.json (741 параметров)
  - Codex Internal Research (31 параметр)
  - Codex Plugin Parameters (24 параметра)

## 🎯 Покрытие

### INI файлы (10 типов):
- `3dsmax.ini`: 756 параметров
- `corona.ini`: 11 параметров
- `forestpack.ini`: 8 параметров
- `ArnoldRenderOptions.ini`: 5 параметров
- `vray.ini`: 4 параметра
- `phoenixfd.ini`: 3 параметра
- `fstorm.ini`: 2 параметра
- `octane.ini`: 2 параметра
- `railclone.ini`: 2 параметра
- `tyflow.ini`: 2 параметра
- `Arnold.ini`: 1 параметр

### Информация о версиях:
- **С версией**: 84 параметра (2015-2026)
- **Без версии**: 712 параметров (будут заполнены парсером)

### Tier распределение:
- **Free**: 384 параметра
- **Advanced**: 412 параметров

## 🏗️ Структура параметра

```json
{
  "Section.ParameterName": {
    "en": {
      "display_name": "Human-readable name",
      "description": "Short description",
      "help_text": "Detailed explanation"
    },
    "ru": {
      "display_name": "Человекочитаемое имя",
      "description": "Краткое описание",
      "help_text": "Детальное объяснение"
    },
    "type": "bool | int | float | string | path | enum",
    "default": "Default value",
    "recommended": {
      "en": "Recommendations in English",
      "ru": "Рекомендации на русском"
    },
    "impact": ["performance", "viewport", "render", "..."],
    "status": "core | undocumented | internal | legacy | deprecated | experimental",
    "source": ["https://..."],
    "section": "Section name in INI",
    "ini_file": "3dsmax.ini | pluginname.ini",
    "tier": "free | advanced",
    "introduced_in": "2024.1 | null"
  }
}
```

## ✨ Улучшения v2.0

1. ✅ **Добавлено поле `ini_file`** - для всех 796 параметров
2. ✅ **Добавлено поле `introduced_in`** - заполнено для 84 параметров
3. ✅ **Конвертировано `recommended`** - теперь объект `{en, ru}` для всех
4. ✅ **Конвертировано `impact`** - теперь список для всех
5. ✅ **Стандартизирована структура `en/ru`** - объекты для всех 796
6. ✅ **Добавлены опциональные поля** - `deprecated_in`, `removed_in`, `tags`, `warnings`, `examples`
7. ✅ **Мёрдж новых параметров** - 55 параметров из Codex research

## 📝 Использование

### Загрузка базы:
```python
import json

with open('docs/maxini_ultimate_master_v2.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

params = {k: v for k, v in db.items() if k != '_metadata'}
metadata = db['_metadata']

print(f"Total parameters: {metadata['total_parameters']}")
```

### Фильтрация по ini_file:
```python
plugin_params = {k: v for k, v in params.items() 
                 if v['ini_file'] != '3dsmax.ini'}
```

### Фильтрация по версии:
```python
new_params = {k: v for k, v in params.items() 
              if v['introduced_in'] and '2024' in str(v['introduced_in'])}
```

### Фильтрация по tier:
```python
free_params = {k: v for k, v in params.items() if v['tier'] == 'free'}
advanced_params = {k: v for k, v in params.items() if v['tier'] == 'advanced'}
```

## 🚀 Следующие шаги

1. **Парсер документации** - автоматическое заполнение `introduced_in` для 712 параметров
2. **Интеграция в UI** - использование базы в MaxManager плагине
3. **Парсер INI файлов** - чтение реальных значений из 3ds Max
4. **Авто-обновление** - периодическое обновление из официальных источников

## 📚 Ссылки

- **Schema**: `docs/param_schema_ultimate.json`
- **Конвертер**: `create_ultimate_master.py`
- **Валидатор**: `validate_ultimate.py`

## 🔧 Обслуживание

### Добавление нового параметра:
1. Следуйте структуре из `param_schema_ultimate.json`
2. Запустите `python validate_ultimate.py` для проверки
3. Обновите `_metadata.total_parameters`

### Обновление версии:
1. Измените `_metadata.schema_version`
2. Добавьте запись в `_metadata.improvements_vX`
3. Обновите дату в `_metadata.created_date`

---

**Created by**: Claude Sonnet 4.5 Ultimate Converter  
**Date**: 2025-10-29

