(	
	file_ini = GetDir #maxroot + "GeoScripts\\GeoAGR.ini"
	if doesfileexist file_ini then 
	(
		HiddenDOSCommand ("GeoAGR.exe " + "\"" + file_ini + "\"") startpath:(GetDir #maxroot + "GeoScripts\\") prompt:"Running GeoAGR" exitCode:&exe
		try(execute (getclipboardText()))catch()
	)
	else messageBox ("Check path to:\n" + file_ini + "\nfile and its existance.\nCan not Startup script GeoAGR.")
)