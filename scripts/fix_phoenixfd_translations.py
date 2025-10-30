"""
Fix Phoenix FD parameter translations - copy from description to display_name.
"""

import json
from pathlib import Path

# Proper Russian display names for Phoenix FD
FIXES = {
    "Cache compression mode": "Режим сжатия кэша",
    "Auto-resize extra margin": "Запас при автоматическом ресайзе",
    "Phoenix FD Pumps": "Насосы Phoenix FD",
}

def fix_translations():
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    fixed = 0
    for key, param_data in data.items():
        if 'en' in param_data and 'ru' in param_data:
            en_name = param_data['en'].get('display_name', '')
            ru_name = param_data['ru'].get('display_name', '')
            
            # If RU name needs fixing
            if en_name in FIXES and ru_name == en_name:
                param_data['ru']['display_name'] = FIXES[en_name]
                fixed += 1
                print(f"  [FIXED] {key}")
                print(f"    EN: {en_name}")
                print(f"    RU: {ru_name} -> {FIXES[en_name]}")
    
    if metadata:
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Fixed {fixed} translations")

if __name__ == '__main__':
    fix_translations()

