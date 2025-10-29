"""
Improve Russian translations in ini_parameters_database.json.

Make translations more natural and human-readable, not word-by-word.
"""

import json
from pathlib import Path


# Human-readable translations for common parameter patterns
TRANSLATIONS = {
    # Common full phrases (check these first)
    "Auto Backup Interval": "Интервал автосохранения",
    "Auto Backup Enabled": "Автосохранение включено",
    "Auto Backup Compress On Auto Backup": "Сжатие при автосохранении",
    "Auto Backup Final Countdown Interval": "Интервал обратного отсчёта",
    "Auto Backup Bailout Enabled": "Аварийное прерывание включено",
    "Auto Backup Show Countdown": "Показывать обратный отсчёт",
    "Auto Backup Prepend Scene Name": "Добавлять имя сцены",
    "Auto Backup Num Files": "Количество копий",
    "Auto Backup File Name": "Имя файла автосохранения",
    
    # Font related
    "Font": "Шрифт",
    "Font Size": "Размер шрифта",
    
    # Load/Save
    "Load Startup Scripts": "Загружать скрипты при запуске",
    "Load Save Scene Scripts": "Скрипты сохранения сцены",
    "Load Save Persistent Globals": "Сохранять глобальные переменные",
    
    # Display/Show
    "Display Update Notification": "Показывать уведомления об обновлении",
    "Display Script Editor On Error": "Открывать редактор при ошибке",
    "Show Command Panel Switch": "Показывать переключение панелей",
    "Show Tool Selections": "Показывать выбор инструментов",
    "Show Menu Selections": "Показывать выбор меню",
    "Show Editor Path": "Показывать путь в редакторе",
    "Show G C Status": "Показывать статус сборщика мусора",
    
    # Security
    "Safe Scene Script Execution Enabled": "Безопасное выполнение скриптов включено",
    "Embedded M A X Script System Commands Execution Blocked": "Блокировка системных команд",
    "Embedded Python Execution Blocked": "Блокировка Python",
    "Embedded Dot Net Execution Blocked": "Блокировка .NET",
    "Safe Script Asset Execution Enabled": "Безопасное выполнение ассетов",
    "Show Security Messages Window On Blocked Commands Enabled": "Показывать окно безопасности",
    "Show Script Editor On Blocked Commands Enabled": "Открывать редактор при блокировке",
    "Block Script Controllers": "Блокировать скриптовые контроллеры",
    "Scene Script Execution Policy": "Политика выполнения скриптов",
    "Last Security Log File": "Последний лог безопасности",
    
    # Paths
    "Install Path": "Путь установки",
    "Project Folder": "Папка проекта",
    "Temp Path": "Папка временных файлов",
    
    # Enable/Disable
    "Enabled": "Включено",
    "Disabled": "Отключено",
    "Enable": "Включить",
    "Disable": "Отключить",
    
    # Renderer
    "Thread Count": "Количество потоков",
    "Scan Band Height": "Высота полосы сканирования",
    "Use Environ Alpha": "Использовать альфа окружения",
    "Filter Background": "Фильтровать фон",
    "Open On Error": "Открывать при ошибке",
    "Dont Show Missing Maps Dlg": "Не показывать диалог отсутствующих текстур",
    "Dont Show Missing U V Warning": "Не показывать предупреждение об UV",
    
    # Viewport
    "Max Texture Size": "Максимальный размер текстуры",
    "Disable H Q Shadows": "Отключить высококачественные тени",
    "Legacy Driver": "Старый драйвер",
    "Ortho Pixel Snap": "Привязка к пикселям в орто",
    
    # Materials
    "Default Material Viewport Mode": "Режим материалов во вьюпорте",
    "Use Physical As Default": "Использовать Physical по умолчанию",
    "Default Map Gamma": "Гамма текстур по умолчанию",
    "Disable Bump Limit": "Отключить ограничение Bump",
    "Legacy Normal Invert Green": "Инвертировать зелёный в Normal (старый)",
    
    # Performance
    "Real Time Playback": "Воспроизведение в реальном времени",
    "Play Active Only": "Воспроизводить только активное",
    "Undo Levels": "Уровней отмены",
    "Backup": "Резервное копирование",
    "Write Compressed": "Сжатое сохранение",
    "Reload Textures": "Перезагружать текстуры",
    
    # Window/Dialog
    "Dimension": "Размеры окна",
    "Position": "Позиция окна",
    "Size": "Размер окна",
    "Maximized": "Развёрнуто",
    
    # Cache
    "Cache Enabled": "Кэш включён",
    "Cache Size": "Размер кэша",
    "Cache Limit M B": "Лимит кэша (МБ)",
    
    # History
    "Count": "Количество",
    "History_00": "История 1",
    "History_01": "История 2",
    "History_02": "История 3",
    "History_03": "История 4",
    "History_04": "История 5",
    "History_05": "История 6",
    
    # Animation
    "Animation": "Анимация",
    "Play Active Only": "Воспроизводить только активное",
    
    # Selection
    "Selection Outline": "Контур выделения",
    "Selection High Light": "Подсветка выделения",
    "Highlight Opacity": "Прозрачность подсветки",
    "Outline Thickness": "Толщина контура",
    "Outline Opacity": "Прозрачность контура",
    "Use Scene Depth": "Использовать глубину сцены",
    "Ignore Backfacing": "Игнорировать обратные грани",
    
    # Common technical terms (keep mixed)
    "H D A O Enabled": "HDAO включён",
    "G F X Type": "Тип GFX",
    "G F X Device": "Устройство GFX",
    "G F X Renderer": "Рендерер GFX",
    
    # Dir entries
    "Dir1": "Папка 1",
    "Dir11": "Папка 11",
    "Dir2": "Папка 2",
    "Dir21": "Папка 21",
}


def get_better_translation(en_name: str, ru_desc: str) -> str:
    """
    Get better human-readable translation.
    
    Args:
        en_name: English parameter name
        ru_desc: Russian description (for context)
    
    Returns:
        Improved Russian translation
    """
    # Check exact match first
    if en_name in TRANSLATIONS:
        return TRANSLATIONS[en_name]
    
    # Keep original if it's technical abbreviation or already OK
    if len(en_name) <= 4 or en_name.isupper():
        return en_name
    
    # For unknown params, return English (better than bad translation)
    return en_name


def process_database(input_path: Path):
    """Process and improve Russian translations."""
    print(f"Loading: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    improved_count = 0
    kept_english_count = 0
    total_params = len(data)
    
    print(f"Processing {total_params} parameters...\n")
    
    for key, param_data in data.items():
        if 'en' in param_data and 'ru' in param_data:
            en_name = param_data['en'].get('display_name', '')
            current_ru_name = param_data['ru'].get('display_name', '')
            ru_desc = param_data['ru'].get('description', '')
            
            if not en_name:
                continue
            
            # Get better translation
            new_ru_name = get_better_translation(en_name, ru_desc)
            
            if new_ru_name != current_ru_name:
                param_data['ru']['display_name'] = new_ru_name
                improved_count += 1
                
                # Show samples
                if improved_count <= 20:
                    print(f"  {key}")
                    print(f"    EN: {en_name}")
                    print(f"    OLD RU: {current_ru_name}")
                    print(f"    NEW RU: {new_ru_name}")
                    print()
                
                if new_ru_name == en_name:
                    kept_english_count += 1
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append("Improved Russian translations to be more natural")
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone!")
    print(f"  Improved: {improved_count} translations")
    print(f"  Kept English (technical): {kept_english_count}")
    print(f"  Total params: {total_params}")


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    # Backup
    backup_path = db_path.parent / "ini_parameters_database_backup3.json"
    print(f"Creating backup: {backup_path}")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    process_database(db_path)

