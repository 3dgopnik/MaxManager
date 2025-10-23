#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaxManager Version Synchronizer
Автоматически обновляет версии во всех файлах проекта
"""

import os
import re
import sys
from pathlib import Path

# Центральное место для версии
VERSION = "1.8.0"

def get_version_files(version):
    """Получить список файлов для обновления версии."""
    return [
        # Python файлы
        {
            "path": "src/ui/maxini_editor_advanced.py",
            "search": r'VERSION = "[^"]*"',
            "replace": f'VERSION = "{version}"'
        },
        
        # MaxScript файлы
        {
            "path": "src/maxscript/maxmanager.mcr", 
            "search": r'Version: \d+\.\d+\.\d+',
            "replace": f'Version: {version}'
        },
        {
            "path": "src/maxscript/maxmanager.mcr",
            "search": r'Features v\d+\.\d+\.\d+:',
            "replace": f'Features v{version}:'
        },
        {
            "path": "src/maxscript/maxmanager.mcr",
            "search": r'Launch MaxINI Editor v\d+\.\d+\.\d+',
            "replace": f'Launch MaxINI Editor v{version}'
        },
        {
            "path": "src/maxscript/maxmanager.mcr",
            "search": r'Launching MaxManager INI Editor v\d+\.\d+\.\d+',
            "replace": f'Launching MaxManager INI Editor v{version}'
        },
        
        # Installer
        {
            "path": "Install_MaxManager.ms",
            "search": r'MaxManager v\d+\.\d+\.\d+ installed successfully',
            "replace": f'MaxManager v{version} installed successfully'
        },
        
        # Test files
        {
            "path": "maxmanager_test.py",
            "search": r'QLabel\("v\d+\.\d+\.\d+"\)',
            "replace": f'QLabel("v{version}")'
        },
        {
            "path": "src/ui/maxini_editor_advanced.py",
            "search": r'version_label = QLabel\("v\d+\.\d+\.\d+"\)',
            "replace": f'version_label = QLabel("v{version}")'
        },
        
        # Documentation
        {
            "path": "README.md",
            "search": r'MaxINI Editor v\d+\.\d+\.\d+',
            "replace": f'MaxINI Editor v{version}'
        },
        {
            "path": "README.md",
            "search": r'Текущая версия:\*\* v\d+\.\d+\.\d+',
            "replace": f'Текущая версия:** v{version}'
        },
        {
            "path": "docs/Modern-UI-Guide.md",
            "search": r'MaxManager v\d+\.\d+\.\d+',
            "replace": f'MaxManager v{version}'
        },
        {
            "path": "docs/Modern-UI-Guide.md",
            "search": r'\*\*Version\*\*: \d+\.\d+\.\d+',
            "replace": f'**Version**: {version}'
        }
    ]

def update_version(version):
    """Обновить версию во всех файлах."""
    project_root = Path(__file__).parent.parent
    
    print(f"Updating version to {version}...")
    
    updated_files = []
    version_files = get_version_files(version)
    
    for file_config in version_files:
        file_path = project_root / file_config["path"]
        
        if not file_path.exists():
            print(f"WARNING: File not found: {file_path}")
            continue
            
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Применяем замену
            content = re.sub(file_config["search"], file_config["replace"], content)
            
            # Если что-то изменилось, записываем обратно
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(str(file_path))
                print(f"UPDATED: {file_path}")
            else:
                print(f"NO CHANGE: {file_path}")
                
        except Exception as e:
            print(f"ERROR updating {file_path}: {e}")
    
    print(f"\nFiles updated: {len(updated_files)}")
    if updated_files:
        print("Updated files:")
        for file_path in updated_files:
            print(f"   - {file_path}")
    
    return len(updated_files) > 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        VERSION = sys.argv[1]
        print(f"Setting version: {VERSION}")
    
    success = update_version(VERSION)
    
    if success:
        print(f"\nVersion {VERSION} successfully updated in all files!")
        print("Don't forget to commit changes:")
        print("   git add .")
        print(f"   git commit -m 'chore: update version to v{VERSION}'")
        print("   git push origin main")
    else:
        print("\nNo changes were made.")
