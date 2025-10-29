#!/usr/bin/env python3
"""Merge parsed parameters into ultimate database"""
import json
from typing import List, Dict
from base_parser import ParameterInfo

class DatabaseMerger:
    """Merge new parameters into existing database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        with open(db_path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)
        
        self.params = {k: v for k, v in self.db.items() if k != '_metadata'}
        self.meta = self.db.get('_metadata', {})
    
    def merge_parameter(self, param: ParameterInfo) -> bool:
        """
        Merge single parameter into database
        
        Rules:
        1. If exists -> check if new info is better
        2. If new -> add with needs_review flag
        3. Always prefer official sources over community
        4. Keep source history
        """
        param_name = f"{param.section}.{param.name}"
        
        # Check if exists
        existing = self.params.get(param_name)
        
        if existing:
            # Update only if new info is better
            updated = self._update_existing(existing, param)
            if updated:
                print(f"  Updated: {param_name}")
                return True
            return False
        else:
            # Add new parameter
            self.params[param_name] = self._create_parameter_entry(param)
            print(f"  Added: {param_name}")
            return True
    
    def _update_existing(self, existing: Dict, new: ParameterInfo) -> bool:
        """Update existing parameter with new info"""
        updated = False
        
        # Update description if empty or new is from official source
        if not existing['en'].get('description') or new.source_type == 'official':
            if new.description_en:
                existing['en']['description'] = new.description_en
                updated = True
        
        # Update recommendation
        if not existing['recommended'].get('en') or new.source_type == 'official':
            if new.recommended_en:
                existing['recommended']['en'] = new.recommended_en
                updated = True
        
        # Update version info
        if not existing.get('introduced_in') and new.introduced_in:
            existing['introduced_in'] = new.introduced_in
            updated = True
        
        # Add to sources
        if new.source_url not in existing.get('source', []):
            if 'source' not in existing:
                existing['source'] = []
            existing['source'].append(new.source_url)
            updated = True
        
        # Mark for review if updated
        if updated:
            existing['needs_review'] = True
            existing['last_updated_by_parser'] = new.parsed_date
        
        return updated
    
    def _create_parameter_entry(self, param: ParameterInfo) -> Dict:
        """Create new parameter entry"""
        return {
            "en": {
                "display_name": param.name,
                "description": param.description_en or f"Parameter {param.name}",
                "help_text": param.examples_en or param.description_en or ""
            },
            "ru": {
                "display_name": param.name,
                "description": param.description_ru or f"Параметр {param.name}",
                "help_text": ""
            },
            "type": "string",  # Will need to detect
            "default": "",
            "recommended": {
                "en": param.recommended_en or "",
                "ru": param.recommended_ru or ""
            },
            "impact": ["general"],
            "status": "undocumented" if param.source_type != 'official' else "core",
            "source": [param.source_url],
            "section": param.section,
            "ini_file": "3dsmax.ini",  # Will need to detect
            "tier": "free",
            "introduced_in": param.introduced_in,
            "needs_review": True,
            "confidence_score": param.confidence_score,
            "parsed_date": param.parsed_date
        }
    
    def save(self):
        """Save updated database"""
        self.meta['total_parameters'] = len(self.params)
        self.db = {'_metadata': self.meta, **dict(sorted(self.params.items()))}
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved: {len(self.params)} parameters")

