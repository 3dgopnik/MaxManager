"""
Add missing plugin parameters to database.
"""

import json
from pathlib import Path

# New plugin parameters to add
NEW_PARAMS = {
    # PhoenixFD
    "Pflow.numbercachedframes": {
        "en": {
            "display_name": "Number of Cached Frames",
            "description": "Number of cached frames for particle flow.",
            "help_text": "Defines how many frames are cached for Phoenix FD particle flow simulation."
        },
        "ru": {
            "display_name": "Количество кэшированных кадров",
            "description": "Количество кэшированных кадров для частиц.",
            "help_text": "Определяет сколько кадров кэшируется для симуляции частиц Phoenix FD."
        },
        "type": "integer",
        "default": "50",
        "recommended": {"en": "50-100", "ru": "50-100"},
        "impact": ["performance"],
        "status": "documented",
        "source": "vendor",
        "section": "Pflow",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Preview.billboardedicons": {
        "en": {
            "display_name": "Billboarded Icons",
            "description": "Use billboarded icons in preview.",
            "help_text": "Icons always face camera in viewport preview."
        },
        "ru": {
            "display_name": "Иконки-билборды",
            "description": "Использовать билборд-иконки в превью.",
            "help_text": "Иконки всегда повёрнуты к камере во вьюпорте."
        },
        "type": "boolean",
        "default": "1",
        "recommended": {"en": "1", "ru": "1"},
        "impact": ["viewport"],
        "status": "documented",
        "source": "vendor",
        "section": "Preview",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Logging.logverbosity": {
        "en": {
            "display_name": "Log Verbosity Level",
            "description": "Level of detail in Phoenix FD logs.",
            "help_text": "0=Errors only, 1=Warnings, 2=Info, 3=Debug, 4=Trace"
        },
        "ru": {
            "display_name": "Уровень детализации логов",
            "description": "Уровень детализации в логах Phoenix FD.",
            "help_text": "0=Только ошибки, 1=Предупреждения, 2=Информация, 3=Отладка, 4=Трассировка"
        },
        "type": "integer",
        "default": "2",
        "recommended": {"en": "2 (normal), 3 (debug)", "ru": "2 (обычный), 3 (отладка)"},
        "impact": ["performance", "debugging"],
        "status": "documented",
        "source": "vendor",
        "section": "Logging",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Logging.writelogpresets": {
        "en": {
            "display_name": "Write Log Presets",
            "description": "Write preset operations to log.",
            "help_text": "Enable to log all preset load/save operations for debugging."
        },
        "ru": {
            "display_name": "Записывать пресеты в лог",
            "description": "Записывать операции с пресетами в лог.",
            "help_text": "Включите для логирования всех операций загрузки/сохранения пресетов."
        },
        "type": "boolean",
        "default": "0",
        "recommended": {"en": "0 (off)", "ru": "0 (выкл)"},
        "impact": ["debugging"],
        "status": "documented",
        "source": "vendor",
        "section": "Logging",
        "ini_file": "phoenixfd.ini",
        "tier": "advanced"
    },
    "Keyboard.esctostopthesim": {
        "en": {
            "display_name": "ESC to Stop Simulation",
            "description": "Allow ESC key to stop simulation.",
            "help_text": "Press ESC during simulation to stop it."
        },
        "ru": {
            "display_name": "ESC для остановки симуляции",
            "description": "Разрешить ESC для остановки симуляции.",
            "help_text": "Нажмите ESC во время симуляции чтобы остановить её."
        },
        "type": "boolean",
        "default": "1",
        "recommended": {"en": "1", "ru": "1"},
        "impact": ["usability"],
        "status": "documented",
        "source": "vendor",
        "section": "Keyboard",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Gui.pinvolumetricsettingsbydefault": {
        "en": {
            "display_name": "Pin Volumetric Settings by Default",
            "description": "Pin volumetric settings rollup.",
            "help_text": "Keep volumetric settings rollup pinned by default."
        },
        "ru": {
            "display_name": "Закреплять настройки объёма",
            "description": "Закреплять свиток настроек объёма.",
            "help_text": "Держать свиток настроек объёма закреплённым по умолчанию."
        },
        "type": "boolean",
        "default": "1",
        "recommended": {"en": "1", "ru": "1"},
        "impact": ["ui"],
        "status": "documented",
        "source": "vendor",
        "section": "Gui",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Gui.highlightmodifiedcolor": {
        "en": {
            "display_name": "Highlight Modified Color",
            "description": "Color for highlighting modified parameters.",
            "help_text": "Hex color code for modified parameter highlighting."
        },
        "ru": {
            "display_name": "Цвет подсветки изменённых",
            "description": "Цвет для подсветки изменённых параметров.",
            "help_text": "Hex-код цвета для подсветки изменённых параметров."
        },
        "type": "color",
        "default": "#008080",
        "recommended": {"en": "#008080 (teal)", "ru": "#008080 (бирюзовый)"},
        "impact": ["ui"],
        "status": "documented",
        "source": "vendor",
        "section": "Gui",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Gui.highlightmodifiedinputs": {
        "en": {
            "display_name": "Highlight Modified Inputs",
            "description": "Highlight modified input fields.",
            "help_text": "Show visual highlight on parameters that differ from default."
        },
        "ru": {
            "display_name": "Подсвечивать изменённые",
            "description": "Подсвечивать изменённые поля ввода.",
            "help_text": "Показывать визуальную подсветку на параметрах отличающихся от умолчания."
        },
        "type": "boolean",
        "default": "1",
        "recommended": {"en": "1", "ru": "1"},
        "impact": ["ui"],
        "status": "documented",
        "source": "vendor",
        "section": "Gui",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    "Cache.defaultcachedir": {
        "en": {
            "display_name": "Default Cache Directory",
            "description": "Default directory for Phoenix FD cache files.",
            "help_text": "Use $(dir) for scene directory or specify custom path."
        },
        "ru": {
            "display_name": "Папка кэша по умолчанию",
            "description": "Папка по умолчанию для кэш-файлов Phoenix FD.",
            "help_text": "Используйте $(dir) для папки сцены или укажите свой путь."
        },
        "type": "path",
        "default": "$(dir)",
        "recommended": {"en": "$(dir)", "ru": "$(dir)"},
        "impact": ["storage"],
        "status": "documented",
        "source": "vendor",
        "section": "Cache",
        "ini_file": "phoenixfd.ini",
        "tier": "standard"
    },
    
    # V-Ray
    "Global Options.vmcversion": {
        "en": {
            "display_name": "VMC Version",
            "description": "V-Ray Material Converter version.",
            "help_text": "Version number of V-Ray Material Converter."
        },
        "ru": {
            "display_name": "Версия VMC",
            "description": "Версия V-Ray Material Converter.",
            "help_text": "Номер версии конвертера материалов V-Ray."
        },
        "type": "string",
        "default": "",
        "recommended": {"en": "", "ru": ""},
        "impact": ["general"],
        "status": "documented",
        "source": "vendor",
        "section": "Global Options",
        "ini_file": "vray.ini",
        "tier": "advanced"
    },
    "Global Options.vmcdialogpos": {
        "en": {
            "display_name": "VMC Dialog Position",
            "description": "Window position for VMC dialog.",
            "help_text": "Stored window position and size for V-Ray Material Converter."
        },
        "ru": {
            "display_name": "Позиция диалога VMC",
            "description": "Позиция окна диалога VMC.",
            "help_text": "Сохранённая позиция и размер окна конвертера материалов V-Ray."
        },
        "type": "string",
        "default": "",
        "recommended": {"en": "", "ru": ""},
        "impact": ["ui"],
        "status": "documented",
        "source": "vendor",
        "section": "Global Options",
        "ini_file": "vray.ini",
        "tier": "advanced"
    },
    "Global Options.checkupdonstartup": {
        "en": {
            "display_name": "Check Updates on Startup",
            "description": "Check for V-Ray updates when starting 3ds Max.",
            "help_text": "Enable to automatically check for V-Ray updates on startup."
        },
        "ru": {
            "display_name": "Проверять обновления при запуске",
            "description": "Проверять обновления V-Ray при запуске 3ds Max.",
            "help_text": "Включите для автоматической проверки обновлений V-Ray при запуске."
        },
        "type": "boolean",
        "default": "true",
        "recommended": {"en": "true", "ru": "true"},
        "impact": ["general"],
        "status": "documented",
        "source": "vendor",
        "section": "Global Options",
        "ini_file": "vray.ini",
        "tier": "standard"
    },
}


def add_new_params():
    """Add new parameters to database."""
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    added = 0
    for param_key, param_data in NEW_PARAMS.items():
        if param_key not in data:
            data[param_key] = param_data
            added += 1
            print(f"  [ADDED] {param_key}: {param_data['en']['display_name']}")
        else:
            print(f"  [EXISTS] {param_key}")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Added {added} missing plugin parameters (PhoenixFD, V-Ray)")
        metadata['total_parameters'] = len(data)
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Added {added} new parameters")

if __name__ == '__main__':
    add_new_params()

