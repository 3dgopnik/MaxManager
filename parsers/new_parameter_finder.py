#!/usr/bin/env python3
"""
Find NEW parameters not in our database
Searches Autodesk docs, forums, community posts
"""
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Set
import re
import time
from pathlib import Path

class NewParameterFinder:
    """Find parameters we don't have yet"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.found_params = []
    
    def find_from_autodesk_docs(self) -> Set[str]:
        """Search Autodesk documentation for ini parameters"""
        print("Searching Autodesk Help for 3dsmax.ini parameters...")
        
        found = set()
        
        # Search strategies
        queries = [
            "3dsmax.ini parameters list",
            "3dsmax.ini configuration settings",
            "3ds Max ini file tweaks",
            "3ds Max performance ini settings",
            "3ds Max security ini parameters"
        ]
        
        for query in queries:
            print(f"\n  Query: {query}")
            time.sleep(2)
            
            # Google search
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            try:
                resp = self.session.get(search_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extract parameter names from snippets
                text = soup.get_text()
                
                # Pattern: word.word or [Section] then word=value
                params = re.findall(r'(\w+\.\w+)\s*=', text)
                params += re.findall(r'\[(\w+)\].*?(\w+)\s*=', text)
                
                for p in params:
                    if isinstance(p, tuple):
                        param_name = f"{p[0]}.{p[1]}"
                    else:
                        param_name = p
                    
                    found.add(param_name)
                    print(f"    Found: {param_name}")
                
            except Exception as e:
                print(f"    Error: {e}")
        
        return found
    
    def find_from_forums(self) -> Set[str]:
        """Search forums for ini parameters"""
        print("\nSearching forums...")
        
        found = set()
        
        forum_queries = [
            "site:forums.autodesk.com 3dsmax.ini tweaks",
            "site:polycount.com 3ds max ini settings",
            "site:cgarchitect.com 3ds max ini configuration"
        ]
        
        for query in forum_queries:
            print(f"\n  Query: {query}")
            time.sleep(2)
            
            try:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                resp = self.session.get(search_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                text = soup.get_text()
                params = re.findall(r'(\w+\.\w+)\s*=', text)
                
                for p in params:
                    found.add(p)
                    print(f"    Found: {p}")
                    
            except Exception as e:
                print(f"    Error: {e}")
        
        return found
    
    def compare_with_database(self, db_path: str) -> Dict:
        """Find parameters NOT in our database"""
        # Load database
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        existing = set(k for k in db.keys() if k != '_metadata')
        
        # Find new
        autodesk_params = self.find_from_autodesk_docs()
        forum_params = self.find_from_forums()
        
        all_found = autodesk_params | forum_params
        
        # Filter out existing
        new_params = all_found - existing
        
        # Also check case-insensitive
        existing_lower = {k.lower() for k in existing}
        truly_new = {p for p in new_params if p.lower() not in existing_lower}
        
        result = {
            'found_total': len(all_found),
            'existing_in_db': len(all_found - new_params),
            'new_parameters': sorted(truly_new),
            'count_new': len(truly_new)
        }
        
        return result
    
    def save_report(self, result: Dict):
        """Save report to file"""
        report_path = Path(__file__).parent / 'new_parameters_report.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("REPORT")
        print("=" * 80)
        print(f"\nTotal found: {result['found_total']}")
        print(f"Already in database: {result['existing_in_db']}")
        print(f"NEW parameters: {result['count_new']}")
        
        if result['new_parameters']:
            print(f"\nNEW parameters to add:")
            for p in result['new_parameters'][:20]:
                print(f"  - {p}")
            if len(result['new_parameters']) > 20:
                print(f"  ... and {len(result['new_parameters']) - 20} more")
        
        print(f"\nReport saved: {report_path}")
        print("=" * 80)

if __name__ == '__main__':
    finder = NewParameterFinder()
    db_path = Path(__file__).parent.parent / 'docs' / 'maxini_ultimate_master_v2.json'
    
    result = finder.compare_with_database(str(db_path))
    finder.save_report(result)

