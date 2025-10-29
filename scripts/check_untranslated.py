"""
Check which parameters are still not translated to Russian.
"""

import json
from pathlib import Path

repo_root = Path(__file__).parent.parent
db_path = repo_root / "docs" / "ini_parameters_database.json"

print("Loading database...")
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

data.pop('_metadata', None)

untranslated = []
total = 0

for key, param_data in data.items():
    if 'en' in param_data and 'ru' in param_data:
        en_name = param_data['en'].get('display_name', '')
        ru_name = param_data['ru'].get('display_name', '')
        
        if en_name and ru_name == en_name:
            untranslated.append((key, en_name))
        
        total += 1

print(f"\nTotal parameters: {total}")
print(f"Untranslated: {len(untranslated)}\n")

# Show first 50 untranslated
print("First 50 untranslated parameters:\n")
for i, (key, name) in enumerate(untranslated[:50], 1):
    print(f"{i:3}. {name:50} ({key})")

if len(untranslated) > 50:
    print(f"\n... and {len(untranslated) - 50} more")

