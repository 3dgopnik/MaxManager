import sys
import subprocess
import site

from . import logger


def ensure_import_docx():
    try:
        user_site_pkgs = site.getusersitepackages()
        if user_site_pkgs not in sys.path:
            sys.path.append(user_site_pkgs)
        import docx
        return True
    except Exception as e:
        try:
            logger.add('installing package docx')
            py_exec = sys.executable
            subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
            subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.run([str(py_exec), "-m", "pip", "install", "python-docx"])
            import docx
            return True
        
        except Exception as e:
            logger.add_error(e, f"Не удалось установить библиотеку docx (для создания отчета в MS Word)")
            return False

def ensure_import_openpyxl():
    try:
        user_site_pkgs = site.getusersitepackages()
        if user_site_pkgs not in sys.path:
            sys.path.append(user_site_pkgs)
        import openpyxl
        return True
    except Exception as e:
        try:
            logger.add('installing package openpyxl')
            py_exec = sys.executable
            subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
            subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.run([str(py_exec), "-m", "pip", "install", "openpyxl"])
            import openpyxl
            return True
        
        except Exception as e:
            logger.add_error(e, f"Не удалось установить библиотеку openpyxl (для чтения excel файлов)")
            return False

def ensure_import_pillow():
    try:
        user_site_pkgs = site.getusersitepackages()
        if user_site_pkgs not in sys.path:
            sys.path.append(user_site_pkgs)
        import PIL
        return True
    except Exception as e:
        try:
            logger.add('installing package pillow')
            py_exec = sys.executable
            subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
            subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.run([str(py_exec), "-m", "pip", "install", "pillow"])
            import PIL
            return True
        
        except Exception as e:
            logger.add_error(e, f"Не удалось установить библиотеку pillow (для работы с изображениями)")
            return False