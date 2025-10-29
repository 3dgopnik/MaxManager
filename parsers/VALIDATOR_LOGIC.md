# Логика валидатора

## Пайплайн (3 этапа)

### ЭТАП 1: Валидация существующих (844 параметра)
**Файл**: `validator_daemon.py`

**Что делает**:
1. Проверяет каждый параметр из базы
2. Ищет на Autodesk Help
3. Ищет на форумах (Autodesk, Polycount, CGArchitect)
4. Определяет статус:
   - `core` - найден в официальной документации
   - `undocumented` - не найден в официальных доках
   - `deprecated` - устарел (есть упоминания)
   - `phantom` - НЕ НАЙДЕН НИГДЕ (возможно фантазия AI)

**Результат**:
```json
{
  "Parameter.Name": {
    "status": "core | undocumented | deprecated",
    "last_verified": "2025-10-29",
    "community_notes": [...],
    "warnings": {...},
    "phantom": true  // <-- Если не найден
  }
}
```

---

### ЭТАП 2: Поиск новых параметров
**Файл**: `new_parameter_finder.py`

**Что делает**:
1. Парсит Autodesk docs (ищет ВСЕ упоминания .ini параметров)
2. Парсит форумы (community findings)
3. Сравнивает с базой
4. Находит параметры которых у нас НЕТ

**Результат**: `new_parameters_report.json`
```json
{
  "found_total": 1200,
  "existing_in_db": 844,
  "new_parameters": [
    "Performance.NewParam2025",
    "Viewport.ExperimentalFeature",
    ...
  ],
  "count_new": 356
}
```

---

### ЭТАП 3: Очистка фантомов
**Логика**:
- Если `phantom: true` → помечаем для review
- НЕ удаляем автоматически (может быть редкий параметр)
- Пользователь вручную решает оставить/удалить

**Пометка**:
```json
{
  "phantom": true,
  "phantom_note": "Not found in any source - needs manual verification",
  "phantom_detected": "2025-10-29",
  "action_required": "review_or_delete"
}
```

---

## Сохранение состояния

### Файл `validation_state.json`:
```json
{
  "validated_params": [
    "Param1", "Param2", ...
  ],
  "last_index": 123,
  "total": 844,
  "status": "running | paused | completed | stopped",
  "started_at": "2025-10-29T10:00:00",
  "paused_at": "2025-10-29T11:00:00"
}
```

### Логика Resume:
1. Читает `validation_state.json`
2. Пропускает `validated_params` (уже проверены)
3. Продолжает с `last_index`
4. Сохраняет каждые 10 параметров

---

## Кнопки управления

### ▶️ START
```python
if state['status'] == 'idle':
    # Начать с начала
elif state['status'] == 'paused':
    # Продолжить с last_index
```

### ⏸️ PAUSE
```python
state['status'] = 'paused'
state['paused_at'] = now()
save_state()
# Процесс проверяет каждую итерацию и останавливается
```

### ⏹️ STOP
```python
state['status'] = 'stopped'
save_state()
# Процесс останавливается, но прогресс сохранён
```

### 🔄 RESET
```python
state = {
    'validated_params': [],
    'last_index': 0,
    'status': 'idle'
}
# Начать валидацию заново
```

---

## Checkpoint система

**Автосохранение каждые 10 параметров**:
- Обновляет базу данных
- Сохраняет состояние
- Пишет в лог

**При краше**:
- Состояние сохранено
- Можно продолжить с последнего checkpoint
- Потеря максимум 10 параметров

---

## Live Dashboard

### Показывает:
1. **Прогресс**: X/844 (Y%)
2. **Статус**: running/paused/completed
3. **Текущий**: Parameter.Name
4. **Кнопки**: Start/Pause/Stop
5. **Live лог** (последние 20):
   - ✅ Параметр проверен
   - 💡 Найдены советы (community_notes)
   - ⚠️ Предупреждения (warnings)
   - 👻 Фантом (phantom detected)

---

## Формат лога

```json
{
  "timestamp": "2025-10-29",
  "parameter": "Performance.ThreadCount",
  "status": "core",
  "verified": true,
  "phantom": false,
  "notes_count": 2,
  "warnings_count": 0,
  "community_notes": [
    {
      "source": "Autodesk Forums",
      "text": "Set to -1 for automatic..."
    }
  ],
  "warnings": []
}
```

---

## Workflow

```
[User] Открывает dashboard
  ↓
[User] Нажимает ▶️ Start
  ↓
[Daemon] Читает state → продолжает с last_index
  ↓
[Daemon] Проверяет параметры (каждые 2 сек)
  ↓
[Dashboard] Показывает live progress + log
  ↓
[User] Видит что находится (notes, warnings, phantoms)
  ↓
[User] Может Pause/Stop в любой момент
  ↓
[Daemon] Сохраняет state → можно Resume
```

---

**Автор**: Claude Sonnet 4.5  
**Дата**: 2025-10-29

