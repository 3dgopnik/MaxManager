# INI Parameters Parser

Автоматический парсер документации для базы параметров 3ds Max.

## Архитектура

### Файлы:
- `base_parser.py` - Базовый класс + ParameterInfo
- `autodesk_help_parser.py` - Парсер Autodesk Help
- `merger.py` - Мёрдж в базу данных
- `run_parser.py` - Запуск парсинга

### Источники (planned):
1. **Autodesk Help** (официал)
2. **Autodesk Forums** (community)
3. **Polycount/CGSociety** (профи)
4. **Reddit r/3dsmax** (кейсы)

## Логика работы

```
Parameter Query
   ↓
[Parser] → ParameterInfo (with confidence_score)
   ↓
[Validator] → Check quality (>0.3 confidence)
   ↓
[Merger] → Update database (add needs_review flag)
   ↓
Database with new params (ready for human review)
```

## ParameterInfo поля:

```python
- name, section, source_url, source_type
- description_en/ru, recommended_en/ru
- introduced_in, deprecated_in
- examples, warnings
- confidence_score (0.0-1.0)
- needs_review (True для новых)
```

## Использование:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск парсинга
python run_parser.py
```

## Текущий статус:

- ✅ Архитектура готова
- ✅ Мёрджер работает
- ⚠️  Autodesk parser - mock данные (нужен API access)
- ❌ Forum parsers - не реализованы
- ❌ Community parsers - не реализованы

## Следующие шаги:

1. **Ручная курация** топ-50 параметров
2. **Community-sourced база** (через Issue/PR)
3. **API парсер** (если Autodesk предоставит доступ)
4. **UI для review** параметров с needs_review=true

## Альтернатива:

Вместо автопарсинга сайтов (сложно, нестабильно):
1. Создать **Issue template** для добавления параметров
2. Community добавляет через PR с проверенной инфой
3. Мы review и апрувим
4. База растёт органично с качественной инфой

