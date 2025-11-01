"""
GeoAGR Code Interceptor
Запускает GeoAGR.exe и перехватывает сгенерированный MaxScript из буфера обмена
"""

import subprocess
import time
import pyperclip
from pathlib import Path
from datetime import datetime

def intercept_geoagr_code():
    """Запускает GeoAGR.exe и перехватывает код из буфера обмена"""
    
    # Путь к GeoAGR
    geoagr_dir = Path("C:/MaxManager/GeoAGR13.40/GeoScripts")
    geoagr_exe = geoagr_dir / "GeoAGR.exe"
    geoagr_ini = geoagr_dir / "GeoAGR.ini"
    
    # Проверка
    if not geoagr_exe.exists():
        print(f"[ERROR] Not found: {geoagr_exe}")
        return None
    
    if not geoagr_ini.exists():
        print(f"[ERROR] Not found: {geoagr_ini}")
        return None
    
    print(f"[OK] Found GeoAGR.exe: {geoagr_exe}")
    print(f"[OK] Found GeoAGR.ini: {geoagr_ini}")
    print()
    
    # Очистить буфер обмена перед запуском
    pyperclip.copy("")
    print("[OK] Clipboard cleared")
    print()
    
    # Запуск GeoAGR.exe
    print("[RUN] Starting GeoAGR.exe...")
    print(f"      Command: {geoagr_exe} \"{geoagr_ini}\"")
    print()
    
    try:
        # Запускаем процесс
        result = subprocess.run(
            [str(geoagr_exe), str(geoagr_ini)],
            cwd=str(geoagr_dir),
            capture_output=True,
            text=True,
            timeout=30  # 30 секунд таймаут
        )
        
        print(f"[OK] GeoAGR.exe finished")
        print(f"     Exit code: {result.returncode}")
        
        # Небольшая задержка для буфера обмена
        time.sleep(0.5)
        
        # Читаем из буфера обмена
        clipboard_content = pyperclip.paste()
        
        if not clipboard_content or len(clipboard_content) < 10:
            print("[WARN] Clipboard is empty or too short")
            print(f"       Content: '{clipboard_content}'")
            return None
        
        print(f"[OK] Intercepted from clipboard: {len(clipboard_content)} chars")
        print()
        
        # Сохранить в файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"C:/MaxManager/analysis/geoagr_intercepted_{timestamp}.ms")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_file.write_text(clipboard_content, encoding='utf-8')
        print(f"[SAVE] Saved to: {output_file}")
        print()
        
        # Показать первые строки
        lines = clipboard_content.split('\n')[:20]
        print("[CODE] First 20 lines:")
        print("=" * 80)
        for i, line in enumerate(lines, 1):
            print(f"{i:3d} | {line}")
        print("=" * 80)
        print()
        
        return str(output_file)
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout! GeoAGR.exe did not finish in 30 seconds")
        return None
    
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return None

if __name__ == "__main__":
    print("=" * 80)
    print("GeoAGR CODE INTERCEPTOR")
    print("=" * 80)
    print()
    
    result = intercept_geoagr_code()
    
    if result:
        print(f"[SUCCESS] File: {result}")
    else:
        print("[FAIL] Could not intercept code")

