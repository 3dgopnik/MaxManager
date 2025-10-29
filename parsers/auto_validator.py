#!/usr/bin/env python3
"""
Automatic parameter validator and enricher
Checks multiple sources and updates database
"""
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
import re

class ParameterValidator:
    """Validates and enriches parameters from multiple sources"""
    
    SOURCES = {
        'autodesk_help': 'https://help.autodesk.com/view/3DSMAX/',
        'autodesk_forums': 'https://forums.autodesk.com/t5/3ds-max/bd-p/3ds-max-forum',
        'polycount': 'https://polycount.com/discussion/',
        'cgarchitect': 'https://www.cgarchitect.com/',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def validate_parameter(self, param_name: str, param_data: Dict) -> Dict:
        """
        Validate single parameter against multiple sources
        
        Returns updated parameter with:
        - status: active | deprecated | removed | unknown
        - community_notes: list of forum findings
        - last_verified: date
        """
        print(f"\n[Validating] {param_name}")
        
        result = {
            'status': param_data.get('status', 'unknown'),
            'status_verified': False,
            'community_notes': [],
            'warnings': [],
            'last_verified': None
        }
        
        # Check Autodesk Help
        autodesk_status = self._check_autodesk(param_name)
        if autodesk_status:
            result['status'] = autodesk_status['status']
            result['status_verified'] = True
            if autodesk_status.get('note'):
                result['community_notes'].append({
                    'source': 'Autodesk Help',
                    'text': autodesk_status['note']
                })
        
        # Check Forums
        forum_tips = self._check_forums(param_name)
        if forum_tips:
            result['community_notes'].extend(forum_tips)
        
        # Check for deprecation warnings
        warnings = self._check_deprecation(param_name, param_data)
        if warnings:
            result['warnings'] = warnings
        
        result['last_verified'] = self._get_current_date()
        
        return result
    
    def _check_autodesk(self, param_name: str) -> Optional[Dict]:
        """Check Autodesk documentation"""
        search_url = f"https://www.google.com/search?q=site:help.autodesk.com+3ds+Max+{param_name}"
        print(f"  [Autodesk Help] {search_url[:80]}...")
        
        try:
            time.sleep(0.5)  # Faster
            
            resp = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Check if any results
            results = soup.find_all('a', href=True)
            autodesk_links = [
                r['href'] for r in results 
                if 'help.autodesk.com' in r['href'] and '3DSMAX' in r['href']
            ]
            
            if autodesk_links:
                # Parameter is documented - likely active
                print(f"    ✓ FOUND in official docs ({len(autodesk_links)} links)")
                return {
                    'status': 'core',
                    'note': f'Found in Autodesk documentation ({len(autodesk_links)} pages)'
                }
            else:
                # Not found in docs - likely undocumented or deprecated
                print(f"    ✗ NOT found in official docs")
                return {
                    'status': 'undocumented',
                    'note': 'Not found in official documentation'
                }
                
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def _check_forums(self, param_name: str) -> List[Dict]:
        """Check forums for community tips"""
        search_url = f"https://www.google.com/search?q=site:forums.autodesk.com+3ds+max+{param_name}"
        print(f"  [Forums] {search_url[:80]}...")
        
        tips = []
        
        # Autodesk Forums
        try:
            time.sleep(0.5)  # Faster
            
            resp = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract snippets
            snippets = soup.find_all('div', class_='BNeawe')
            found_count = 0
            for snippet in snippets[:3]:  # Top 3 results
                text = snippet.get_text(strip=True)
                if len(text) > 50 and param_name.lower() in text.lower():
                    tips.append({
                        'source': 'Autodesk Forums',
                        'text': text[:300]
                    })
                    found_count += 1
            
            if found_count > 0:
                print(f"    ✓ Found {found_count} forum mentions")
            else:
                print(f"    ✗ No forum mentions")
                    
        except Exception as e:
            print(f"    Forum check error: {e}")
        
        return tips
    
    def _check_deprecation(self, param_name: str, param_data: Dict) -> List[str]:
        """Check if parameter is deprecated"""
        warnings = []
        
        # Check for version info
        intro = param_data.get('introduced_in')
        depr = param_data.get('deprecated_in')
        
        if depr:
            warnings.append(f"Deprecated in 3ds Max {depr}")
        
        # Check description for deprecation keywords
        desc = param_data.get('en', {}).get('description', '')
        if any(kw in desc.lower() for kw in ['deprecated', 'obsolete', 'legacy', 'removed']):
            warnings.append("May be deprecated (check description)")
        
        return warnings
    
    def _get_current_date(self) -> str:
        """Get current date"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def validate_database(self, db_path: str, limit: int = 10):
        """Validate entire database (or subset)"""
        print("=" * 80)
        print("AUTO VALIDATOR - Checking parameters against sources")
        print("=" * 80)
        
        # Progress tracking
        progress_file = Path(__file__).parent / 'progress.json'
        
        # Load database
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        params = {k: v for k, v in db.items() if k != '_metadata'}
        meta = db['_metadata']
        
        # Select parameters to validate
        param_list = list(params.items())[:limit]
        
        updated = 0
        log_file = progress_file.parent / 'validation_log.jsonl'
        
        for idx, (param_name, param_data) in enumerate(param_list, 1):
            # Update progress
            progress = {
                'total': limit,
                'validated': idx,
                'current': param_name,
                'status': 'running',
                'percent': round(idx / limit * 100, 1)
            }
            with open(progress_file, 'w') as f:
                json.dump(progress, f)
            validation = self.validate_parameter(param_name, param_data)
            
            # Update parameter
            if validation['status_verified']:
                param_data['status'] = validation['status']
            
            if validation['community_notes']:
                param_data['community_notes'] = validation['community_notes']
            
            if validation['warnings']:
                if 'warnings' not in param_data:
                    param_data['warnings'] = {}
                param_data['warnings']['en'] = ' | '.join(validation['warnings'])
            
            param_data['last_verified'] = validation['last_verified']
            
            # Log findings
            log_entry = {
                'timestamp': validation['last_verified'],
                'parameter': param_name,
                'status': validation['status'],
                'verified': validation['status_verified'],
                'notes_count': len(validation['community_notes']),
                'warnings_count': len(validation['warnings']),
                'community_notes': validation['community_notes'],
                'warnings': validation['warnings']
            }
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            updated += 1
            print(f"  [UPDATED]")
        
        # Save
        db_updated = {'_metadata': meta, **dict(sorted(params.items()))}
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db_updated, f, indent=2, ensure_ascii=False)
        
        print(f"\n{updated}/{limit} parameters validated and updated")
        print("=" * 80)

if __name__ == '__main__':
    from pathlib import Path
    
    db_path = Path(__file__).parent.parent / 'docs' / 'maxini_ultimate_master_v2.json'
    
    validator = ParameterValidator()
    
    # Validate ALL parameters
    validator.validate_database(str(db_path), limit=844)

