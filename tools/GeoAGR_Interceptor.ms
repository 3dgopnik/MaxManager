/*
GeoAGR Code Interceptor - MaxScript версия
Запускает GeoAGR и перехватывает код ПЕРЕД выполнением
*/

(
	clearListener()
	
	format "========================================\n"
	format "GeoAGR CODE INTERCEPTOR (MaxScript)\n"
	format "========================================\n\n"
	
	-- Путь к GeoAGR
	file_ini = GetDir #maxroot + "GeoScripts\\GeoAGR.ini"
	
	if not (doesfileexist file_ini) then
	(
		format "[ERROR] Not found: %\n" file_ini
		messageBox ("Check path to:\n" + file_ini + "\nfile and its existance.")
	)
	else
	(
		format "[OK] Found: %\n" file_ini
		format "[RUN] Starting GeoAGR.exe...\n\n"
		
		-- Запускаем GeoAGR.exe (как оригинальный скрипт)
		HiddenDOSCommand ("GeoAGR.exe " + "\"" + file_ini + "\"") startpath:(GetDir #maxroot + "GeoScripts\\") prompt:"Running GeoAGR" exitCode:&exe
		
		format "[OK] GeoAGR.exe finished (exit code: %)\n" exe
		format "[RUN] Reading clipboard...\n\n"
		
		-- Читаем из буфера обмена (то что положил GeoAGR.exe)
		clipboard_code = getclipboardText()
		
		if clipboard_code == undefined or clipboard_code.count < 10 then
		(
			format "[WARN] Clipboard is empty or too short\n"
			format "       Content: '%'\n" clipboard_code
		)
		else
		(
			format "[OK] Intercepted: % chars\n" clipboard_code.count
			
			-- Создаём папку если не существует
			analysis_dir = "C:\\MaxManager\\analysis"
			makeDir analysis_dir all:true
			
			-- Сохраняем в файл с UTF-8 BOM через .NET
			timestamp = substituteString (substituteString (localTime as string) ":" "") " " "_"
			timestamp = substituteString timestamp "." ""
			output_file = analysis_dir + "\\geoagr_intercepted_" + timestamp + ".ms"
			
			-- Используем .NET для сохранения в UTF-8 с BOM
			dotNet.loadAssembly "System"
			utf8WithBom = dotNetObject "System.Text.UTF8Encoding" true -- true = with BOM
			fileClass = dotNetClass "System.IO.File"
			fileClass.WriteAllText output_file clipboard_code utf8WithBom
			
			format "[SAVE] Saved to: %\n\n" output_file
			
			-- Показываем первые строки
			lines = filterString clipboard_code "\n"
			show_lines = if lines.count > 30 then 30 else lines.count
			
			format "[CODE] First % lines:\n" show_lines
			format "================================================================================\n"
			for i = 1 to show_lines do
			(
				format "%: %\n" i lines[i]
			)
			format "================================================================================\n\n"
			
			-- Спрашиваем выполнить ли код
			answer = queryBox "Code intercepted and saved!\n\nExecute GeoAGR UI now?" title:"GeoAGR Interceptor"
			
			if answer then
			(
				format "[RUN] Executing GeoAGR code...\n"
				try
				(
					execute clipboard_code
					format "[OK] GeoAGR UI launched\n"
				)
				catch
				(
					format "[ERROR] Failed to execute code\n"
				)
			)
			else
			(
				format "[SKIP] Code execution skipped by user\n"
			)
		)
	)
	
	format "\n[DONE] Check C:\\MaxManager\\analysis\\ folder\n"
)

