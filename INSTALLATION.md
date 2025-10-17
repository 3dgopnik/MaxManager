# MaxINI Editor - Установка

## 🚀 Быстрая установка

1. **Открой 3ds Max**
2. **Дропни файл** `MaxINI_Editor_Install.ms` в viewport (или запусти через MAXScript → Run Script)
3. **Дождись** сообщения "Installation Complete"
4. **Добавь кнопку** на панель:
   - Customize → Customize User Interface
   - Toolbars → Category: **MaxManager**
   - Перетащи **MaxINI Editor** на панель
5. **Готово!** Нажми кнопку для запуска

## 🔄 Обновление

Для обновления без переустановки:
- Дропни `MaxINI_Editor_Update.ms` в viewport
- Перезапусти 3ds Max

## 📁 Что устанавливается

- **Макрос**: `%LOCALAPPDATA%\Autodesk\3dsMax\2025 - 64bit\ENU\UI\macroscripts\MaxManager_INIEditor.mcr`
- **Advanced Editor**: `%LOCALAPPDATA%\Autodesk\3dsMax\2025 - 64bit\ENU\scripts\MaxManager\src\ui\maxini_editor_advanced.py`
- **Иконки**: `%LOCALAPPDATA%\Autodesk\3dsMax\2025 - 64bit\ENU\usericons\Dark\` и `Light\`
- **Данные**: `%LOCALAPPDATA%\Autodesk\3dsMax\2025 - 64bit\ENU\scripts\MaxManager\data\`

## ⚠️ Требования

- 3ds Max 2025 (или настрой пути для другой версии)
- Python 3.10+
- PySide6
- PySide6-Fluent-Widgets

## 🆘 Проблемы?

Проверь **MAXScript Listener** для деталей.

