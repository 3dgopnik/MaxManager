#!/usr/bin/env python3
"""
SMART PARSER - извлекает РЕАЛЬНУЮ инфу из документации
Не тупой "найдено/не найдено", а конкретные descriptions, recommendations, versions
"""
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import time

class SmartParser:
    """Умный парсер - извлекает структурированную инфу"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def parse_autodesk_main_ini_page(self):
        """Парсит главную страницу про 3dsmax.ini"""
        url = "https://help.autodesk.com/cloudhelp/2026/ENU/3DSMax-Basics/files/GUID-AFC5FE94-8B39-4AB9-99DC-DF7AF309BF2A.htm"
        
        print(f"\n[Parsing] {url}")
        
        try:
            resp = self.session.get(url, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Сохраняем полный текст
            full_text = soup.get_text()
            
            # Извлекаем все упоминания параметров
            findings = {
                'url': url,
                'parameters': []
            }
            
            # Ищем паттерны: [Section] или Parameter=Value
            sections = re.findall(r'\[([^\]]+)\]', full_text)
            params_with_values = re.findall(r'(\w+)\s*=\s*([^\n]+)', full_text)
            
            print(f"  Sections found: {len(set(sections))}")
            print(f"  Parameters found: {len(params_with_values)}")
            
            # Сохраняем всю страницу для анализа
            with open('parsers/autodesk_main_page.txt', 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"  Saved to: parsers/autodesk_main_page.txt")
            
            return findings
            
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    def parse_gamma_documentation(self):
        """Парсит документацию по Gamma"""
        # Ищем страницы про Gamma
        queries = [
            "site:help.autodesk.com 3ds Max gamma correction settings",
            "site:help.autodesk.com 3ds Max bitmap gamma",
        ]
        
        findings = []
        
        for query in queries:
            print(f"\n[Searching] {query}")
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            try:
                time.sleep(0.5)
                resp = self.session.get(search_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Находим ссылки на Autodesk Help
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'help.autodesk.com' in href and 'gamma' in href.lower():
                        # Извлекаем чистый URL
                        if '/url?q=' in href:
                            clean_url = href.split('/url?q=')[1].split('&')[0]
                            links.append(clean_url)
                
                print(f"  Found {len(links)} relevant pages")
                
                # Парсим первую найденную страницу
                if links:
                    page_url = links[0]
                    print(f"  Parsing: {page_url[:80]}...")
                    
                    time.sleep(0.5)
                    page_resp = self.session.get(page_url, timeout=10)
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    # Извлекаем описания параметров
                    text = page_soup.get_text()
                    
                    # Ищем упоминания Gamma параметров
                    gamma_params = {
                        'DisplayGamma': None,
                        'BitmapInputGamma': None,
                        'BitmapOutputGamma': None,
                    }
                    
                    for param in gamma_params.keys():
                        if param.lower() in text.lower():
                            # Находим контекст вокруг параметра
                            lines = text.split('\n')
                            for i, line in enumerate(lines):
                                if param.lower() in line.lower():
                                    context = '\n'.join(lines[max(0,i-3):min(len(lines),i+4)])
                                    gamma_params[param] = context[:500]
                                    print(f"    Found context for: {param}")
                                    break
                    
                    findings.append({
                        'url': page_url,
                        'params': gamma_params
                    })
                    
            except Exception as e:
                print(f"  Error: {e}")
        
        return findings
    
    def extract_real_info(self):
        """Извлекает РЕАЛЬНУЮ инфу из документации"""
        print("=" * 80)
        print("SMART PARSER - Extracting real documentation")
        print("=" * 80)
        
        # Парсим главную страницу про ini
        main_page = self.parse_autodesk_main_ini_page()
        
        # Парсим документацию по Gamma
        gamma_docs = self.parse_gamma_documentation()
        
        # Сохраняем результаты
        results = {
            'main_ini_page': main_page,
            'gamma_documentation': gamma_docs,
        }
        
        with open('parsers/smart_parser_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("Results saved: parsers/smart_parser_results.json")
        print("Main page text: parsers/autodesk_main_page.txt")
        print("=" * 80)
        
        return results

if __name__ == '__main__':
    parser = SmartParser()
    parser.extract_real_info()

