#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create ULTIMATE master database - best of all formats combined!
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

def convert_master_to_ultimate(master_param: Dict[str, Any]) -> Dict[str, Any]:
    """Convert old master format to ultimate format"""
    ultimate = {}
    
    # en/ru - check if objects or strings
    en_val = master_param.get('en', {})
    ru_val = master_param.get('ru', {})
    
    # If already objects, keep them
    if isinstance(en_val, dict):
        ultimate['en'] = en_val
    else:
        # Convert string to object (for old simplified params)
        ultimate['en'] = {
            'display_name': en_val,
            'description': en_val,
            'help_text': en_val
        }
    
    if isinstance(ru_val, dict):
        ultimate['ru'] = ru_val
    else:
        # Convert string to object (for old simplified params)
        ultimate['ru'] = {
            'display_name': ru_val,
            'description': ru_val,
            'help_text': ru_val
        }
    
    # type
    ultimate['type'] = master_param.get('type', 'unknown')
    
    # default
    ultimate['default'] = master_param.get('default', '')
    
    # recommended - convert string to object if needed
    rec = master_param.get('recommended', '')
    if isinstance(rec, str):
        ultimate['recommended'] = {
            'en': rec,
            'ru': rec  # TODO: better translation
        }
    elif isinstance(rec, dict):
        ultimate['recommended'] = rec
    else:
        ultimate['recommended'] = {'en': '', 'ru': ''}
    
    # impact - convert string to list if needed
    impact = master_param.get('impact', [])
    if isinstance(impact, str):
        ultimate['impact'] = [impact] if impact else []
    elif isinstance(impact, list):
        ultimate['impact'] = impact
    else:
        ultimate['impact'] = []
    
    # status
    ultimate['status'] = master_param.get('status', 'undocumented')
    
    # source
    ultimate['source'] = master_param.get('source', [])
    
    # section
    ultimate['section'] = master_param.get('section', 'Unknown')
    
    # ini_file - NEW! default to 3dsmax.ini
    ultimate['ini_file'] = master_param.get('ini_file', '3dsmax.ini')
    
    # tier
    ultimate['tier'] = master_param.get('tier', 'free')
    
    # introduced_in - NEW! default to null
    ultimate['introduced_in'] = master_param.get('introduced_in', None)
    
    # Optional fields (only if present)
    if 'deprecated_in' in master_param:
        ultimate['deprecated_in'] = master_param['deprecated_in']
    
    if 'removed_in' in master_param:
        ultimate['removed_in'] = master_param['removed_in']
    
    if 'tags' in master_param:
        ultimate['tags'] = master_param['tags']
    
    if 'related_parameters' in master_param:
        ultimate['related_parameters'] = master_param['related_parameters']
    
    if 'warnings' in master_param:
        ultimate['warnings'] = master_param['warnings']
    
    if 'examples' in master_param:
        ultimate['examples'] = master_param['examples']
    
    return ultimate


def convert_codex_to_ultimate(codex_param: Dict[str, Any], param_name: str) -> Dict[str, Any]:
    """Convert codex format to ultimate format"""
    ultimate = {}
    
    # en/ru - convert strings to objects OR keep objects
    en_val = codex_param.get('en', param_name)
    ru_val = codex_param.get('ru', param_name)
    
    # If already objects (from some codex sources), keep them
    if isinstance(en_val, dict):
        ultimate['en'] = en_val
    else:
        # Convert string to object
        desc_obj = codex_param.get('description', {})
        en_desc = desc_obj.get('en', '') if isinstance(desc_obj, dict) else str(desc_obj)
        
        ultimate['en'] = {
            'display_name': en_val,
            'description': en_desc,
            'help_text': en_desc  # Use same for now
        }
    
    if isinstance(ru_val, dict):
        ultimate['ru'] = ru_val
    else:
        # Convert string to object
        desc_obj = codex_param.get('description', {})
        ru_desc = desc_obj.get('ru', '') if isinstance(desc_obj, dict) else str(desc_obj)
        
        ultimate['ru'] = {
            'display_name': ru_val,
            'description': ru_desc,
            'help_text': ru_desc  # Use same for now
        }
    
    # type
    ultimate['type'] = codex_param.get('type', 'unknown')
    
    # default
    ultimate['default'] = codex_param.get('default', '')
    
    # recommended
    rec = codex_param.get('recommended', {})
    if isinstance(rec, dict):
        ultimate['recommended'] = rec
    elif isinstance(rec, str):
        ultimate['recommended'] = {'en': rec, 'ru': rec}
    else:
        ultimate['recommended'] = {'en': '', 'ru': ''}
    
    # impact
    impact = codex_param.get('impact', [])
    ultimate['impact'] = impact if isinstance(impact, list) else [impact] if impact else []
    
    # status
    ultimate['status'] = codex_param.get('status', 'undocumented')
    
    # source
    ultimate['source'] = codex_param.get('source', [])
    
    # section
    ultimate['section'] = codex_param.get('section', 'Unknown')
    
    # ini_file - from codex!
    ultimate['ini_file'] = codex_param.get('ini_file', '3dsmax.ini')
    
    # tier - determine based on status
    if codex_param.get('status') == 'internal':
        ultimate['tier'] = 'advanced'
    elif 'plugin' in codex_param.get('ini_file', '').lower():
        ultimate['tier'] = 'advanced'
    else:
        ultimate['tier'] = 'free'
    
    # introduced_in - from codex!
    ultimate['introduced_in'] = codex_param.get('introduced_in', None)
    
    # Special fields from internal_research
    if 'special' in codex_param:
        ultimate['tags'] = ultimate.get('tags', []) + [codex_param['special']]
    
    if 'risk' in codex_param:
        risk = codex_param['risk']
        if risk in ['high', 'medium']:
            ultimate['warnings'] = {
                'en': f'Risk level: {risk}',
                'ru': f'Уровень риска: {risk}'
            }
    
    return ultimate


def main():
    print("=" * 80)
    print("CREATING ULTIMATE MASTER DATABASE")
    print("=" * 80)
    
    # Load all sources
    print("\n[1/5] Loading source files...")
    master = json.load(open('docs/maxini_master_verified.json', 'r', encoding='utf-8'))
    codex_internal = json.load(open('temp_internal.json', 'r', encoding='utf-8'))
    codex_plugin = json.load(open('temp_plugin.json', 'r', encoding='utf-8'))
    
    master_params = {k: v for k, v in master.items() if k != '_metadata'}
    master_meta = master.get('_metadata', {})
    
    print(f"   Master: {len(master_params)} params")
    print(f"   Codex Internal: {len(codex_internal)} params")
    print(f"   Codex Plugin: {len(codex_plugin)} params")
    
    # Create ultimate database
    print("\n[2/5] Converting master parameters to ultimate format...")
    ultimate_db = {}
    
    for param_name, param_data in master_params.items():
        ultimate_db[param_name] = convert_master_to_ultimate(param_data)
    
    print(f"   Converted: {len(ultimate_db)} params")
    
    # Add codex internal
    print("\n[3/5] Adding Codex Internal parameters...")
    added_internal = 0
    for param_name, param_data in codex_internal.items():
        if param_name not in ultimate_db:
            ultimate_db[param_name] = convert_codex_to_ultimate(param_data, param_name)
            added_internal += 1
    print(f"   Added: {added_internal} new params")
    
    # Add codex plugin
    print("\n[4/5] Adding Codex Plugin parameters...")
    added_plugin = 0
    for param_name, param_data in codex_plugin.items():
        if param_name not in ultimate_db:
            ultimate_db[param_name] = convert_codex_to_ultimate(param_data, param_name)
            added_plugin += 1
    print(f"   Added: {added_plugin} new params")
    
    # Create metadata
    print("\n[5/5] Creating metadata...")
    metadata = {
        'schema_version': '2.0.0',
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'created_by': 'Claude Sonnet 4.5 Ultimate Converter',
        'total_parameters': len(ultimate_db),
        'previous_version': master_meta.get('version', '1.0.0'),
        'sources': [
            'maxini_master_verified.json (741 params)',
            'Codex Internal Research (31 params)',
            'Codex Plugin Parameters (24 params)'
        ],
        'improvements_v2': [
            'Added ini_file field to all parameters',
            'Added introduced_in field (filled for 55 params, null for others)',
            'Converted recommended: string -> object {en, ru}',
            'Converted impact: string -> list',
            'Standardized en/ru structure across all params',
            'Added optional fields: deprecated_in, removed_in, tags, warnings, examples',
            'Merged 55 new parameters from Codex research'
        ],
        'statistics': {
            'from_master': len(master_params),
            'from_codex_internal': added_internal,
            'from_codex_plugin': added_plugin,
            'total': len(ultimate_db)
        }
    }
    
    # Sort parameters alphabetically
    ultimate_db = dict(sorted(ultimate_db.items()))
    
    # Combine with metadata
    final_db = {
        '_metadata': metadata,
        **ultimate_db
    }
    
    # Save
    output_path = 'docs/maxini_ultimate_master_v2.json'
    print(f"\n[SAVING] Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_db, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print(f"\nCreated: {output_path}")
    print(f"Total parameters: {len(ultimate_db)}")
    print(f"  - From master: {len(master_params)}")
    print(f"  - New from Codex Internal: {added_internal}")
    print(f"  - New from Codex Plugin: {added_plugin}")
    print(f"\nSchema version: 2.0.0")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()

