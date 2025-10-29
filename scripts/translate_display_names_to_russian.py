"""
Translate display_name fields to Russian in ini_parameters_database.json.

Uses description field (which is already in Russian) to create Russian display_name.
"""

import json
from pathlib import Path


def translate_display_name(en_name: str, ru_description: str) -> str:
    """
    Create Russian display_name from English name and Russian description.
    
    Simple mapping of common technical terms.
    """
    # Common translations
    translations = {
        # Common words
        "Enable": "Включить",
        "Disable": "Отключить",
        "Show": "Показать",
        "Hide": "Скрыть",
        "Display": "Отображение",
        "Load": "Загрузка",
        "Save": "Сохранение",
        "Font": "Шрифт",
        "Size": "Размер",
        "Color": "Цвет",
        "Path": "Путь",
        "File": "Файл",
        "Directory": "Каталог",
        "Mode": "Режим",
        "Type": "Тип",
        "Count": "Количество",
        "Enabled": "Включено",
        "Disabled": "Отключено",
        "Width": "Ширина",
        "Height": "Высота",
        "Position": "Позиция",
        "Dimension": "Размер",
        "Auto": "Авто",
        "Backup": "Резервная копия",
        "Interval": "Интервал",
        "Threshold": "Порог",
        "Limit": "Лимит",
        "Cache": "Кэш",
        "Memory": "Память",
        "Thread": "Поток",
        "Quality": "Качество",
        "Scale": "Масштаб",
        "Default": "По умолчанию",
        "Custom": "Пользовательский",
        "Current": "Текущий",
        "Preview": "Предпросмотр",
        "Texture": "Текстура",
        "Material": "Материал",
        "Render": "Рендер",
        "Output": "Вывод",
        "Resolution": "Разрешение",
        "Format": "Формат",
        "Log": "Лог",
        "Security": "Безопасность",
        "Script": "Скрипт",
        "Editor": "Редактор",
        "Window": "Окно",
        "Dialog": "Диалог",
        "Button": "Кнопка",
        "Startup": "Запуск",
        "Templates": "Шаблоны",
        "History": "История",
        "Recent": "Недавние",
        "Last": "Последний",
        "First": "Первый",
        "Maximum": "Максимум",
        "Minimum": "Минимум",
        "Opacity": "Непрозрачность",
        "Outline": "Контур",
        "Selection": "Выделение",
        "Animation": "Анимация",
        "Viewport": "Вьюпорт",
        "Listener": "Listener",
        "Recorder": "Рекордер",
        "Macro": "Макрос",
        "Command": "Команда",
        "Panel": "Панель",
        "Tool": "Инструмент",
        "Menu": "Меню",
        "Update": "Обновление",
        "Notification": "Уведомление",
    }
    
    # Try simple word-by-word translation
    words = en_name.split()
    translated_words = []
    
    for word in words:
        if word in translations:
            translated_words.append(translations[word])
        else:
            # Keep technical terms in English
            translated_words.append(word)
    
    return " ".join(translated_words)


def process_database(input_path: Path):
    """Process database and translate RU display names."""
    print(f"Loading: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    translated_count = 0
    total_params = len(data)
    
    print(f"Processing {total_params} parameters...")
    
    for key, param_data in data.items():
        if 'en' in param_data and 'ru' in param_data:
            en_name = param_data['en'].get('display_name', '')
            ru_name = param_data['ru'].get('display_name', '')
            ru_desc = param_data['ru'].get('description', '')
            
            # Translate only if RU name is same as EN (not translated yet)
            if en_name and ru_name == en_name:
                new_ru_name = translate_display_name(en_name, ru_desc)
                param_data['ru']['display_name'] = new_ru_name
                translated_count += 1
                
                if translated_count <= 10:  # Show first 10
                    print(f"  {key}: '{en_name}' -> '{new_ru_name}'")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append("Translated display_name to Russian")
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Translated {translated_count} display names")


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    # Backup
    backup_path = db_path.parent / "ini_parameters_database_backup2.json"
    print(f"Creating backup: {backup_path}")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    process_database(db_path)
    print("\nAll done!")

