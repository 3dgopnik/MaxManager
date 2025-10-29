#!/usr/bin/env python3
"""
Fix phantom detection logic
Real INI parameters are NOT phantoms, just undocumented
"""
import json
from pathlib import Path

db_path = Path('docs/maxini_ultimate_master_v2.json')

with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

params = {k: v for k, v in db.items() if k != '_metadata'}

print("=" * 80)
print("FIXING PHANTOM LOGIC")
print("=" * 80)

# Parameters from real INI files have these markers
real_ini_markers = [
    'forestpack.ini',
    'corona.ini',
    'phoenixfd.ini',
    '3ds Max 2025 installation',
    'ForestPack',
    'Corona',
]

for param_name, param_data in params.items():
    sources = param_data.get('source', [])
    
    # Check if from real INI
    is_from_real_ini = any(
        marker in str(sources) 
        for marker in real_ini_markers
    )
    
    if is_from_real_ini:
        # Mark as verified real parameter
        param_data['verified_real_ini'] = True
        param_data['status'] = 'undocumented'  # Not in docs, but real
        
        # Remove phantom flag if exists
        if 'phantom' in param_data:
            del param_data['phantom']
        if 'phantom_note' in param_data:
            del param_data['phantom_note']

# Save
db_updated = {'_metadata': db['_metadata'], **dict(sorted(params.items()))}
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db_updated, f, indent=2, ensure_ascii=False)

# Stats
real_ini_count = sum(1 for v in params.values() if v.get('verified_real_ini'))
print(f"\nMarked as REAL INI parameters: {real_ini_count}")
print("=" * 80)

