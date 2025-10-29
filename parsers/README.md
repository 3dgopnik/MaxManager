# Parsers - Database Maintenance Tools

## Инструменты

### 1. `auto_validator.py` - Автоматический валидатор
**Что делает**:
- Проверяет параметры на Autodesk Help
- Ищет упоминания на форумах (Autodesk Forums, Polycount, CGArchitect)
- Находит community tips и советы
- Определяет статус: active | deprecated | removed | unknown
- Добавляет warnings если параметр устарел
- Обновляет базу с пометками

**Использование**:
```bash
python parsers/auto_validator.py
```

**Результат**: обновлённая база с:
- `status` - актуальность параметра
- `community_notes` - советы с форумов
- `warnings` - предупреждения об устаревании
- `last_verified` - дата проверки

---

### 2. `community_enricher.py` - Ручная курация
**Что делает**:
- Добавляет проверенные рекомендации вручную
- Указывает версии введения
- Детальные описания от экспертов

**Использование**:
1. Редактировать словарь `RECOMMENDATIONS`
2. Запустить: `python parsers/community_enricher.py`

---

### 3. `base_parser.py` + `merger.py` - Инфраструктура
Базовые классы для расширения парсеров

---

## Workflow обновления базы

### Еженедельно (автоматически):
```bash
# Валидация параметров
python parsers/auto_validator.py

# Проверка результата
git diff docs/maxini_ultimate_master_v2.json

# Коммит если всё ок
git add docs/maxini_ultimate_master_v2.json
git commit -m "auto: validated parameters"
```

### По необходимости (вручную):
```bash
# Добавление детальных рекомендаций
python parsers/community_enricher.py
```

---

## Источники данных

### Официальные:
- Autodesk Help (help.autodesk.com)
- Plugin documentation (iToo, Chaos, ChaosScatter...)

### Community:
- Autodesk Forums
- Polycount
- CGArchitect
- Reddit r/3dsmax
- CG Society

---

## Структура обогащённого параметра

```json
{
  "Performance.ThreadCount": {
    "status": "core",
    "last_verified": "2025-10-29",
    "community_notes": [
      {
        "source": "Autodesk Forums",
        "text": "For render farms, set manual thread count..."
      }
    ],
    "warnings": {
      "en": "No warnings"
    }
  }
}
```

---

## Приоритеты валидации

1. **Security параметры** - критично, проверять первыми
2. **Performance параметры** - высокая важность
3. **Plugin параметры** - могут устареть быстро
4. **UI параметры** - низкий приоритет

---

## Limits и Rate Limiting

**Google Search**: 2 сек между запросами
**Forums**: 2 сек между запросами

Не запускать на всех 844 параметрах сразу - делать батчами по 10-20.
