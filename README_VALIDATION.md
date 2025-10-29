# 🚀 Быстрый старт валидации

## Простые команды

### 1. Запуск валидатора с dashboard
```bash
run_validator.bat
```

**Что произойдёт**:
1. Откроется dashboard в браузере
2. Нажми кнопку ▶️ **Start**
3. Смотри live прогресс и лог
4. Можешь поставить на паузу ⏸️ или остановить ⏹️

**Dashboard**: http://localhost:8888/dashboard.html

---

### 2. Поиск новых параметров
```bash
run_find_new.bat
```

**Что делает**:
- Ищет параметры которых НЕТ в базе
- Парсит Autodesk docs + форумы
- Сохраняет отчёт: `parsers/new_parameters_report.json`

**Время**: ~10 минут

---

### 3. Ручное обогащение
```bash
run_enrich.bat
```

**Как использовать**:
1. Открой `parsers/community_enricher.py`
2. Добавь рекомендации в словарь `RECOMMENDATIONS`
3. Запусти `run_enrich.bat`

**Пример**:
```python
RECOMMENDATIONS = {
    "Performance.ThreadCount": {
        "en": "Set to -1 for auto, or manual for render farms",
        "ru": "Установите -1 для авто, или вручную для рендер-ферм",
        "introduced_in": "2009"
    },
}
```

---

## 📊 Файлы результатов

### `parsers/validation_state.json`
Состояние валидации:
- Сколько проверено
- На каком месте остановились
- Статус (running/paused/completed)

### `parsers/validation_log.jsonl`
Лог всех находок:
- Community notes (советы с форумов)
- Warnings (устаревшие параметры)
- Phantoms (фантазии AI)

### `parsers/new_parameters_report.json`
Отчёт о новых параметрах:
- Список найденных параметров
- Сколько уже есть в базе
- Сколько новых нужно добавить

---

## ⚙️ Для разработчиков

### Запуск вручную:
```bash
# Валидатор
python parsers/validator_daemon.py

# HTTP сервер для dashboard
python -m http.server 8888 --directory parsers

# Поиск новых
python parsers/new_parameter_finder.py

# Обогащение
python parsers/community_enricher.py
```

---

## 🎯 Workflow

1. **Запускаешь**: `run_validator.bat`
2. **Смотришь**: dashboard с live логом
3. **Видишь**: что находится (notes, warnings, phantoms)
4. **Ждёшь**: ~60 мин для всех 844 параметров
5. **Получаешь**: обновлённую базу с проверенными данными

**Прогресс сохраняется** - можешь остановить и продолжить в любой момент!

---

**Автор**: Claude Sonnet 4.5  
**Дата**: 2025-10-29

