#!/usr/bin/env python3
"""
Direct parser - parses known sources directly (no Google search)
More reliable and faster
"""
import requests
from bs4 import BeautifulSoup
from known_sources import get_all_sources
from typing import Dict, List
import time

class DirectSourceParser:
    """Parse known sources directly"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.cache = {}  # Cache parsed pages
    
    def parse_all_sources(self) -> Dict:
        """Parse all known sources and build parameter knowledge base"""
        print("=" * 80)
        print("DIRECT SOURCE PARSER - Parsing known documentation")
        print("=" * 80)
        
        sources = get_all_sources()
        findings = {
            'parameters_found': {},
            'sources_parsed': 0,
            'errors': []
        }
        
        for source in sources:
            print(f"\n[{source['type'].upper()}] {source['title']}")
            print(f"  URL: {source['url']}")
            
            try:
                time.sleep(0.5)
                resp = self.session.get(source['url'], timeout=15)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Cache the page
                self.cache[source['url']] = soup
                
                # Extract parameters
                params = self._extract_parameters(soup, source)
                
                if params:
                    print(f"  ✓ Found {len(params)} parameters")
                    for param_name, param_info in params.items():
                        if param_name not in findings['parameters_found']:
                            findings['parameters_found'][param_name] = []
                        findings['parameters_found'][param_name].append({
                            'source': source,
                            'info': param_info
                        })
                else:
                    print(f"  - No parameters found")
                
                findings['sources_parsed'] += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                findings['errors'].append({
                    'source': source['url'],
                    'error': str(e)
                })
        
        print("\n" + "=" * 80)
        print(f"Parsed: {findings['sources_parsed']} sources")
        print(f"Found: {len(findings['parameters_found'])} unique parameters")
        print(f"Errors: {len(findings['errors'])}")
        print("=" * 80)
        
        return findings
    
    def _extract_parameters(self, soup: BeautifulSoup, source: Dict) -> Dict:
        """Extract parameter names and info from page"""
        params = {}
        
        text = soup.get_text()
        
        # Pattern 1: Section.Parameter = value
        pattern1 = re.findall(r'(\w+)\.(\w+)\s*=\s*([^\n]+)', text)
        for section, param, value in pattern1:
            param_name = f"{section}.{param}"
            params[param_name] = {
                'default_value': value.strip(),
                'found_in': source['type']
            }
        
        # Pattern 2: [Section] followed by Parameter = value
        sections = re.findall(r'\[(\w+)\]([^\[]+)', text)
        for section, content in sections:
            param_matches = re.findall(r'(\w+)\s*=\s*([^\n]+)', content)
            for param, value in param_matches:
                param_name = f"{section}.{param}"
                params[param_name] = {
                    'default_value': value.strip(),
                    'found_in': source['type'],
                    'section': section
                }
        
        return params
    
    def search_parameter(self, param_name: str) -> List[Dict]:
        """Search for specific parameter in cached pages"""
        findings = []
        
        for url, soup in self.cache.items():
            text = soup.get_text().lower()
            if param_name.lower() in text:
                # Extract context
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if param_name.lower() in line:
                        context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                        findings.append({
                            'url': url,
                            'context': context[:500]
                        })
                        break
        
        return findings

if __name__ == '__main__':
    import json
    
    parser = DirectSourceParser()
    findings = parser.parse_all_sources()
    
    # Save report
    with open('direct_parser_findings.json', 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved: direct_parser_findings.json")

