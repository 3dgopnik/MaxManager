# 📋 MaxManager Version Management

## 🎯 Централизованное управление версиями

### Автоматический способ (рекомендуется)

```bash
# Обновить версию во всех файлах автоматически
python scripts/update_version.py [NEW_VERSION]

# Пример:
python scripts/update_version.py 1.9.0
```

### Ручной способ

При изменении версии нужно обновить **ВСЕ** следующие файлы:

## 📝 Файлы с версиями (обновлять ВСЕГДА)

### 1. **Python файлы**
- **`src/ui/maxini_editor_advanced.py`**
  ```python
  VERSION = "1.8.0"  # ← Изменить здесь
  ```

### 2. **MaxScript файлы**
- **`src/maxscript/maxmanager.mcr`**
  ```maxscript
  Version: 1.8.0  # ← В заголовке файла
  
  Features v1.8.0:  # ← В комментарии Features
  
  Launch MaxINI Editor v1.8.0  # ← В комментарии Launch
  ```

### 3. **Установщик**
- **`Install_MaxManager.ms`**
  ```maxscript
  local msg = "MaxManager v1.8.0 installed successfully!\n\n"  # ← В сообщении установки
  ```

### 4. **Тестовые файлы**
- **`maxmanager_test.py`**
  ```python
  version_label = QLabel("v1.8.0")  # ← В версии интерфейса
  ```

### 5. **Документация**
- **`README.md`**
  ```markdown
  ### ✅ MaxINI Editor v1.8.0 (Production Ready)  # ← В заголовке модуля
  **Текущая версия:** v1.8.0 (Complete Modern UI Implementation)  # ← В футере
  ```

- **`docs/Modern-UI-Guide.md`**
  ```markdown
  MaxManager v1.8.0 features...  # ← В описании
  **Version**: 1.8.0  # ← В футере
  ```

## 🔍 Как найти все упоминания версий

```bash
# Поиск всех упоминаний версий в проекте
grep -r "v[0-9]\+\.[0-9]\+\.[0-9]\+" . --include="*.py" --include="*.ms" --include="*.md"
grep -r "Version:" . --include="*.py" --include="*.ms" --include="*.md"
grep -r "VERSION" . --include="*.py"
```

## ✅ Чеклист обновления версии

- [ ] **Python**: `src/ui/maxini_editor_advanced.py` - переменная `VERSION`
- [ ] **MaxScript заголовок**: `src/maxscript/maxmanager.mcr` - `Version: X.X.X`
- [ ] **MaxScript Features**: `src/maxscript/maxmanager.mcr` - `Features vX.X.X:`
- [ ] **MaxScript Launch**: `src/maxscript/maxmanager.mcr` - `Launch MaxINI Editor vX.X.X`
- [ ] **Installer**: `Install_MaxManager.ms` - сообщение установки
- [ ] **Test UI**: `maxmanager_test.py` - `QLabel("vX.X.X")`
- [ ] **README**: `README.md` - заголовок модуля и футер
- [ ] **UI Guide**: `docs/Modern-UI-Guide.md` - описание и футер
- [ ] **CHANGELOG**: `CHANGELOG.md` - добавить новую запись

## 🚀 Процесс релиза

1. **Обновить версию**:
   ```bash
   python scripts/update_version.py 1.9.0
   ```

2. **Обновить CHANGELOG.md**:
   ```markdown
   ## [2025-XX-XX] - Описание изменений
   
   ### Добавлено
   * ...
   
   ### Изменено  
   * ...
   
   ### Исправлено
   * ...
   ```

3. **Закоммитить изменения**:
   ```bash
   git add .
   git commit -m "chore: update version to v1.9.0"
   git push origin main
   ```

4. **Создать Release в GitHub** (опционально)

## 🎯 Текущая версия

**v1.8.0** - Complete Modern UI Implementation

---

**Важно**: Всегда проверяйте, что версия обновлена во **ВСЕХ** файлах из списка выше!
