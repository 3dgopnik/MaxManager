# Запуск валидации базы

## Текущий статус
**База**: 844 параметра  
**Проверено**: 5 параметров  
**Осталось**: 839 параметров

---

## Как запустить

### Малый батч (10-20 параметров, ~1 минута):
```bash
# Редактировать parsers/auto_validator.py, строка 214
# limit=20

python parsers/auto_validator.py
```

### Средний батч (50 параметров, ~3 минуты):
```bash
# limit=50
python parsers/auto_validator.py
```

### Полная валидация (844 параметра, ~60 минут):
```bash
# limit=844
python parsers/auto_validator.py
```

⚠️ **Внимание**: Google может заблокировать при слишком частых запросах!

---

## Рекомендуемая стратегия

### День 1: Security (12 параметров)
```bash
# Приоритет 1 - критичные параметры безопасности
# limit=12, только Security.*
```

### День 2: Performance (125 параметров)
```bash
# Приоритет 2 - производительность
# Батчами по 25
```

### День 3-7: Остальное
```bash
# По 100 параметров в день
```

---

## Автоматизация (будущее)

### GitHub Actions (еженедельно):
```yaml
name: Validate Database
on:
  schedule:
    - cron: '0 0 * * 0'  # Каждое воскресенье
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: python parsers/auto_validator.py
      - run: git add docs/ && git commit -m "auto: weekly validation"
```

---

## Результаты валидации

Каждый параметр получает:
- ✅ `last_verified` - дата проверки
- ✅ `status` - active/deprecated/removed
- ✅ `community_notes` - советы с форумов
- ✅ `warnings` - если устарел

---

**Текущая скорость**: ~4 сек на параметр  
**Полная валидация**: ~60 минут для 844 параметров

