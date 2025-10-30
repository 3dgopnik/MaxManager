"""
Comprehensive database cleanup:
1. Fix abbreviations (G F X -> GFX, H D A O -> HDAO, etc)
2. Translate all remaining untranslated parameters
3. Fix translation errors
"""

import json
import re
from pathlib import Path


# Fix common abbreviations that got split
ABBREVIATION_FIXES = {
    # Common tech terms
    "G F X": "GFX",
    "H D A O": "HDAO",
    "U V W": "UVW",
    "U V": "UV",
    "A A": "AA",
    "F P S": "FPS",
    "V F B": "VFB",
    "O S L": "OSL",
    "O C I O": "OCIO",
    "G I": "GI",
    "D O F": "DOF",
    "H D R I": "HDRI",
    "P B R": "PBR",
    "A O": "AO",
    "I D": "ID",
    "I Ds": "IDs",
    "U I": "UI",
    "A P I": "API",
    "S D K": "SDK",
    "R G B": "RGB",
    "M S O": "MSO",
    "M A X": "MAX",
    "F B X": "FBX",
    "A T F": "ATF",
    "D X": "DX",
    "V R": "VR",
    "A I": "AI",
    "M L": "ML",
    "J I T": "JIT",
    "G C": "GC",
    "I O": "IO",
    "U N C": "UNC",
    "U S": "US",
    "A C I": "ACI",
    "N T I S": "NTIS",
    "A T S": "ATS",
    "M X S": "MXS",
    "V M C": "VMC",
    "W I C": "WIC",
    "L U T": "LUT",
}

# Additional translations for common remaining patterns
COMMON_TRANSLATIONS = {
    # Numbers and measurements
    "Width": "Ширина",
    "Height": "Высота",
    "Radius": "Радиус",
    "Distance": "Расстояние",
    "Offset": "Смещение",
    "Margin": "Отступ",
    "Padding": "Отступ внутренний",
    "Spacing": "Расстояние",
    
    # Actions
    "Convert": "Конвертировать",
    "Collect": "Собирать",
    "Export": "Экспортировать",
    "Import": "Импортировать",
    "Generate": "Генерировать",
    "Create": "Создать",
    "Delete": "Удалить",
    "Remove": "Убрать",
    "Add": "Добавить",
    "Replace": "Заменить",
    "Override": "Переопределить",
    "Refresh": "Обновить",
    "Reset": "Сбросить",
    
    # States
    "Visible": "Видимый",
    "Hidden": "Скрытый",
    "Locked": "Заблокированный",
    "Frozen": "Замороженный",
    "Active": "Активный",
    "Inactive": "Неактивный",
    
    # Rendering
    "Renderer": "Рендерер",
    "Rendering": "Рендеринг",
    "Render": "Рендер",
    "Shader": "Шейдер",
    "Lighting": "Освещение",
    "Shadow": "Тень",
    "Shadows": "Тени",
    "Reflection": "Отражение",
    "Refraction": "Преломление",
    "Glossy": "Глянцевый",
    "Specular": "Зеркальность",
    "Diffuse": "Диффуз",
    "Ambient": "Ambient",
    
    # Common
    "Options": "Настройки",
    "Settings": "Настройки",
    "Preferences": "Предпочтения",
    "Configuration": "Конфигурация",
    "Advanced": "Продвинутые",
    "Basic": "Базовые",
    "General": "Общие",
    "Global": "Глобальные",
}


def fix_abbreviations(text):
    """Fix split abbreviations in text."""
    if not text:
        return text
    
    result = text
    for wrong, correct in ABBREVIATION_FIXES.items():
        result = result.replace(wrong, correct)
    
    return result


def process_database():
    """Process entire database."""
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    fixed_abbr = 0
    translated = 0
    
    for key, param_data in data.items():
        if 'en' not in param_data or 'ru' not in param_data:
            continue
        
        # Fix abbreviations in EN
        old_en = param_data['en'].get('display_name', '')
        new_en = fix_abbreviations(old_en)
        if new_en != old_en:
            param_data['en']['display_name'] = new_en
            fixed_abbr += 1
            if fixed_abbr <= 10:
                print(f"  [ABBR FIX EN] {key}: '{old_en}' -> '{new_en}'")
        
        # Fix abbreviations in RU
        old_ru = param_data['ru'].get('display_name', '')
        new_ru = fix_abbreviations(old_ru)
        if new_ru != old_ru:
            param_data['ru']['display_name'] = new_ru
            fixed_abbr += 1
            if fixed_abbr <= 20:
                print(f"  [ABBR FIX RU] {key}: '{old_ru}' -> '{new_ru}'")
        
        # Translate if RU == EN (still untranslated)
        en_name = param_data['en'].get('display_name', '')
        ru_name = param_data['ru'].get('display_name', '')
        
        if en_name and ru_name == en_name:
            # Try simple word-by-word translation
            words = en_name.split()
            translated_words = []
            
            for word in words:
                if word in COMMON_TRANSLATIONS:
                    translated_words.append(COMMON_TRANSLATIONS[word])
                else:
                    # Keep technical terms in English
                    translated_words.append(word)
            
            new_ru_name = " ".join(translated_words)
            
            # Only update if actually translated something
            if new_ru_name != en_name:
                param_data['ru']['display_name'] = new_ru_name
                translated += 1
                if translated <= 10:
                    print(f"  [TRANSLATED] {key}: '{en_name}' -> '{new_ru_name}'")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Fixed {fixed_abbr} abbreviations and translated {translated} parameters")
        metadata['total_parameters'] = len(data)
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone!")
    print(f"  Fixed abbreviations: {fixed_abbr}")
    print(f"  Translated: {translated}")
    print(f"  Total parameters: {len(data)}")

if __name__ == '__main__':
    process_database()

