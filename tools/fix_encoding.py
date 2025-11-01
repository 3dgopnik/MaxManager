"""
Фикс кодировки для перехваченного GeoAGR файла
Пробует разные варианты декодирования
"""

import sys
from pathlib import Path

def try_fix_encoding(file_path):
    """Пробуем разные кодировки"""
    
    encodings = [
        ('utf-8', 'cp1251'),
        ('latin1', 'cp1251'),
        ('cp1252', 'cp1251'),
        ('iso-8859-1', 'cp1251'),
    ]
    
    file_path = Path(file_path)
    
    print(f"Fixing: {file_path}")
    print()
    
    # Читаем бинарно
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    print(f"File size: {len(raw_data)} bytes")
    print()
    
    for read_enc, write_enc in encodings:
        try:
            print(f"Trying: read as {read_enc}, interpret as {write_enc}...")
            
            # Декодируем как read_enc
            text = raw_data.decode(read_enc)
            
            # Проверяем первые строки
            lines = text.split('\n')[:5]
            
            # Энкодим в bytes как write_enc, потом декодим обратно как utf-8
            reencoded = text.encode(read_enc).decode(write_enc)
            
            # Проверяем есть ли русские буквы
            if any('а' <= c <= 'я' or 'А' <= c <= 'Я' for c in reencoded[:1000]):
                print(f"  SUCCESS! Found Russian text")
                print(f"  Sample: {reencoded[:200]}")
                print()
                
                # Сохраняем
                output_file = file_path.parent / f"{file_path.stem}_fixed.ms"
                with open(output_file, 'w', encoding='utf-8-sig') as f:
                    f.write(reencoded)
                
                print(f"Saved: {output_file}")
                return str(output_file)
            
        except Exception as e:
            print(f"  Failed: {e}")
    
    print("\nCould not fix encoding automatically")
    return None

if __name__ == "__main__":
    file_path = r"C:\MaxManager\analysis\geoagr_intercepted_01.11.2025_95438.ms"
    result = try_fix_encoding(file_path)
    
    if result:
        print(f"\n✓ Fixed file: {result}")
    else:
        print("\n✗ Could not fix")

