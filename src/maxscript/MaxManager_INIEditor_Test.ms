/*
 * MaxManager INI Editor - Test Prototype
 * Version: 0.1.0 (Experimental)
 * Description: Test script to verify max.ini editing workflow
 * Author: MaxManager
 * Created: 2025-10-17
 */

macroScript MaxManager_INIEditor_Test
category:"MaxManager"
buttonText:"INI Editor (TEST)"
toolTip:"Test MaxINI Editor - Experiment with max.ini editing"
(
    -- Log function
    fn logMsg msg = (
        local timestamp = localTime as string
        format "[%] MaxINI Test: %\n" timestamp msg
    )
    
    logMsg "=== Starting MaxINI Editor Test ==="
    
    -- Get max.ini path
    local maxIniPath = (getDir #maxroot) + "3dsMax.ini"
    local userIniPath = (getDir #plugcfg) + "\\..\\3dsMax.ini"
    
    logMsg ("Max Root INI: " + maxIniPath)
    logMsg ("User INI: " + userIniPath)
    
    -- Check if files exist
    if (doesFileExist maxIniPath) then
        logMsg "✓ Max root INI exists"
    else
        logMsg "✗ Max root INI NOT found"
    
    if (doesFileExist userIniPath) then
        logMsg "✓ User INI exists"
    else
        logMsg "✗ User INI NOT found"
    
    -- Get actual INI path (user profile)
    local actualIniPath = substituteString userIniPath "\\..\\" "\\"
    logMsg ("Actual INI path: " + actualIniPath)
    
    -- Launch Python Qt GUI
    logMsg "Launching Python Qt GUI..."
    
    -- Python script path
    local pythonScriptPath = (getDir #scripts) + "MaxManager\\test_ini_editor.py"
    
    -- Check if Python script exists, if not - create embedded version
    if not (doesFileExist pythonScriptPath) then
    (
        logMsg "Python script not found, executing inline..."
        
        -- Inline Python code for testing
        python.Execute ("
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QMessageBox
from PySide6.QtCore import Qt
from pymxs import runtime as rt
import os
import datetime

class MaxINIEditorTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.log_messages = []
        
    def log(self, msg):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        log_msg = f'[{timestamp}] {msg}'
        self.log_messages.append(log_msg)
        self.log_text.append(log_msg)
        print(log_msg)
        
    def initUI(self):
        self.setWindowTitle('MaxINI Editor - TEST PROTOTYPE')
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('<h2>MaxINI Editor Test</h2>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info label
        info = QLabel('Это тестовый прототип для эксперимента с max.ini')
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Log area
        log_label = QLabel('<b>Лог операций:</b>')
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Buttons
        btn_find_ini = QPushButton('1. Найти max.ini')
        btn_find_ini.clicked.connect(self.find_ini)
        layout.addWidget(btn_find_ini)
        
        btn_read_ini = QPushButton('2. Прочитать max.ini')
        btn_read_ini.clicked.connect(self.read_ini)
        layout.addWidget(btn_read_ini)
        
        btn_test_edit = QPushButton('3. Тестовое изменение (добавить комментарий)')
        btn_test_edit.clicked.connect(self.test_edit)
        layout.addWidget(btn_test_edit)
        
        btn_check_reload = QPushButton('4. Проверить: перезагрузился ли файл?')
        btn_check_reload.clicked.connect(self.check_reload)
        layout.addWidget(btn_check_reload)
        
        central_widget.setLayout(layout)
        
        self.ini_path = None
        self.original_content = None
        
        self.log('GUI инициализирован')
        
    def find_ini(self):
        self.log('=== Поиск max.ini ===')
        
        # Try different paths
        possible_paths = [
            os.path.expandvars(r'%LOCALAPPDATA%\\Autodesk\\3dsMax\\2025 - 64bit\\ENU\\3dsMax.ini'),
            os.path.expandvars(r'%LOCALAPPDATA%\\Autodesk\\3dsMax\\2024 - 64bit\\ENU\\3dsMax.ini'),
            os.path.join(os.path.dirname(sys.executable), '3dsMax.ini')
        ]
        
        for path in possible_paths:
            self.log(f'Проверяем: {path}')
            if os.path.exists(path):
                self.ini_path = path
                self.log(f'✓ НАЙДЕН: {path}')
                size = os.path.getsize(path) / 1024
                self.log(f'  Размер: {size:.2f} KB')
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                self.log(f'  Изменён: {mtime}')
                return
            else:
                self.log(f'✗ Не найден: {path}')
        
        self.log('⚠️ max.ini НЕ НАЙДЕН!')
        QMessageBox.warning(self, 'Ошибка', 'max.ini не найден!')
        
    def read_ini(self):
        if not self.ini_path:
            QMessageBox.warning(self, 'Ошибка', 'Сначала найдите max.ini (кнопка 1)')
            return
            
        self.log('=== Чтение max.ini ===')
        try:
            with open(self.ini_path, 'r', encoding='utf-16-le') as f:
                self.original_content = f.read()
            
            lines = len(self.original_content.split('\\n'))
            self.log(f'✓ Прочитано {lines} строк')
            self.log(f'Первые 200 символов:')
            self.log(self.original_content[:200])
        except Exception as e:
            self.log(f'✗ Ошибка чтения: {e}')
            QMessageBox.critical(self, 'Ошибка', f'Не удалось прочитать файл: {e}')
            
    def test_edit(self):
        if not self.ini_path or not self.original_content:
            QMessageBox.warning(self, 'Ошибка', 'Сначала прочитайте max.ini (кнопки 1-2)')
            return
            
        self.log('=== Тестовое изменение ===')
        
        reply = QMessageBox.question(
            self, 
            'Подтверждение', 
            'Добавить тестовый комментарий в начало max.ini?\\n\\nБудет создан бэкап!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            self.log('Отменено пользователем')
            return
        
        try:
            # Create backup
            backup_path = self.ini_path + '.backup.' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(backup_path, 'w', encoding='utf-16-le') as f:
                f.write(self.original_content)
            self.log(f'✓ Бэкап создан: {backup_path}')
            
            # Add test comment
            test_comment = f'; MaxManager Test - {datetime.datetime.now()}\\n; This is a test edit\\n\\n'
            new_content = test_comment + self.original_content
            
            # Write modified file
            with open(self.ini_path, 'w', encoding='utf-16-le') as f:
                f.write(new_content)
            
            self.log('✓ Файл изменён! Добавлен тестовый комментарий')
            self.log('')
            self.log('⚠️ ТЕПЕРЬ ВАЖНО:')
            self.log('1. НЕ ЗАКРЫВАЙТЕ 3ds Max!')
            self.log('2. Нажмите кнопку 4 через 5 секунд')
            self.log('3. Мы проверим изменился ли файл обратно')
            
            QMessageBox.information(
                self,
                'Успех',
                'Файл изменён!\\n\\nТеперь подождите 5 секунд и нажмите кнопку 4'
            )
            
        except Exception as e:
            self.log(f'✗ Ошибка записи: {e}')
            QMessageBox.critical(self, 'Ошибка', f'Не удалось записать файл: {e}')
            
    def check_reload(self):
        if not self.ini_path:
            QMessageBox.warning(self, 'Ошибка', 'Сначала найдите max.ini')
            return
            
        self.log('=== Проверка перезагрузки файла ===')
        
        try:
            with open(self.ini_path, 'r', encoding='utf-16-le') as f:
                current_content = f.read()
            
            if current_content == self.original_content:
                self.log('⚠️ ФАЙЛ ВЕРНУЛСЯ К ОРИГИНАЛУ!')
                self.log('3ds Max перезаписал наши изменения!')
                QMessageBox.warning(
                    self,
                    'Результат',
                    '❌ 3ds Max ПЕРЕЗАПИСАЛ наши изменения!\\n\\nВывод: Нужен перезапуск Max для применения изменений'
                )
            elif 'MaxManager Test' in current_content:
                self.log('✓ Наши изменения ещё присутствуют')
                self.log('Max пока не перезаписал файл')
                QMessageBox.information(
                    self,
                    'Результат',
                    '✓ Изменения пока на месте\\n\\nЗакройте Max и проверим что будет'
                )
            else:
                self.log('? Неожиданное содержимое файла')
                
        except Exception as e:
            self.log(f'✗ Ошибка проверки: {e}')

# Create and show window
try:
    # Get Max main window
    from pymxs import runtime as rt
    main_window_hwnd = rt.windows.getMAXHWND()
    
    # Create Qt application if needed
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create and show test window
    window = MaxINIEditorTest()
    window.show()
    
    print('MaxINI Editor Test window opened')
    
except Exception as e:
    print(f'Error creating test window: {e}')
    import traceback
    traceback.print_exc()
")
    )
    else
    (
        logMsg ("Executing Python script: " + pythonScriptPath)
        python.ExecuteFile pythonScriptPath
    )
    
    logMsg "=== Test script finished ==="
)

