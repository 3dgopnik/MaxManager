/*//////////////////////////////////////////////////////////////////////////////////////////////////////////*/
	/* Settings*/
/*//////////////////////////////////////////////////////////////////////////////////////////////////////////*/

global selfPath = getFileNamePath (getThisScriptFileName())
global iniFile = selfPath + @"\install.ini"
global self = getThisScriptFileName()
global encrFile = selfPath + getFilenameFile self + ".mse"
global uac_bat = "uac.bat"
global maxVer =  (maxVersion())[1]

fn getIni p t: #string = 
(	
	i = getIniSetting iniFile "INSTALL" p
	
	case t of 
	(
		#bool: if(i == "" or i == "false") then false else true
		default: return i
	)	
)

fn getIniLicense = 
(
	l = getIniSetting iniFile "LICENSE"
	t = ""
	
	n = "\r\n"
	s =  "                           _____________________________________________" + n + n
	
	for i in l where i != "" do
	(
		if(findString i "<hr>" != undefined) do 
		(
			t += s 
			continue
		)
		
		if(findString i "<br>" != undefined) do
		(
			t += n + n
			continue
		)
		
		t += i + n
	)
	
	return t
)

global MACRO = getIni "MACRO"
global CAT = getIni "CAT"
global TXT= getIni "TXT"
global HELP = getIni "HELP"
global ICONS = getIni "ICONS" t: #bool


/*//////////////////////////////////////////////////////////////////////////////////////////////////////////*/
	/* Paths */
/*//////////////////////////////////////////////////////////////////////////////////////////////////////////*/

global DEST = getDir(#temp) + @"\" + MACRO + @"\"
global TEMP = getDir(#temp) + @"\" + MACRO + @"\"
global FULLNAME = MACRO + ".mse"
global ICO_PATH = #((GetDir(#ui) + @"icons\"), (GetDir(#userIcons)) + @"\")
global WIN_TEMP = @"c:\temp\"

/*//////////////////////////////////////////////////////////////////////////////////////////////////////////*/
	/* Stage variables */	
/*//////////////////////////////////////////////////////////////////////////////////////////////////////////*/

fn manualInstruction = 
(
	m = "Please add button manually:\n"
	m += "\n1. Go to Customize -> Customize User Interface -> Toolbars."
	m += "\n2. Select category \"[" + (getIni  "CAT") + "]\"."
	m += "\n3. Drag&Drop \"" + (getIni  "TXT") + "\" to the toolbar."
	return m
)

global ACTION = 1	
global QUAD = false
global TOOLBAR = false
	
fn createMacro =
(
	m = ""
	m += "\nmacroScript " + MACRO 
	m += "\ncategory:\"[" + CAT + "]\"" 
	m += "\ntoolTip:\"" + TXT + "\""
	m += "\nbuttontext:\"" + TXT + "\""
	if(ICONS) do m += "\nicon:#(\"" + MACRO + "\", 1)"
	m += "\n("
	m += "\n\ton execute do"
	m += "\n\t("
		m += "\n\t\tszScript =  getDir(#temp) + \"\\" + MACRO + @"\" + FULLNAME + "\""
		m += "\n\t\ttry(fileIn(szScript)) catch(messageBox \"Script not found! Please reinstall " + TXT + "!\" title: \"Warning!\")"
	m += "\n\t)"
	m += "\n)"
		
	execute(m)
)	

fn addToolBarButton macro cat txt remove: false =
(
	fn insertContent f data: "" find: "" rewrite: false =
	(						
		file = MemStreamMgr.openFile f
		size = file.size()
		MemStreamMgr.close file
				
		stream = openFile f mode:"r+"

		seek stream 0 
			
		mt = "\"Main Toolbar\""			
		skipToString stream mt
				
		exist = (skipToString stream find) == undefined
		
		previousContent = ""
		
		findPos = filePos stream
		
		if(not exist) do
		(							
			if(rewrite) do 
			(
				pos = findPos - find.count
				seek stream	0
				previousContent += readChars stream (pos)					
			)
			
			pos = findPos - (if(rewrite) then 0 else find.count)
		
			seek stream pos
			
			previousContent += readChars stream (size - pos)
									
			if(rewrite) do pos = 0
			
			seek stream pos
				
						
			format data to: stream
			format previousContent to: stream
		)
		
		close stream
		
		return not exist
	)
	
	try
	(
		f = cui.getConfigFile() 
		
		cui.loadConfig f
		cui.saveConfigAs f
		cui.loadConfig f
		
		l = "<Item typeID=\"2\" type=\"CTB_MACROBUTTON\" width=\"0\" height=\"0\" controlID=\"0\" macroTypeID=\"3\" macroType=\"MB_TYPE_ACTION\" actionTableID=\"647394\" imageID=\"-1\" imageName=\"\" actionID=\"" + macro + "`[" + cat + "]\" tip=\"" + txt + "\" label=\"" + txt + "\" />"
				
		if(remove) then
		(			
			insertContent f find: l rewrite: true
		)
		else
		(		
			insertContent f find: "</Items>" data: ("\t\t" + l + "\n")			
		)
				
		cui.loadConfig f
		--cui.setConfigFile f
		cui.saveConfigAs f
		--cui.loadConfig f
			
	) catch(messageBox "Error! ToolBar button not added!\nPlease add ToolBar button manually!" title: "Error!")
)

fn addQuadMenuButton macro cat txt remove: false =
(
	quadMenu = menuMan.getViewportRightClickMenu #nonePressed
	theMenu = quadMenu.getMenu 1

	fn findMenuItem theMenu menuName =
	(
		for i in 1 to theMenu.numItems() where (theMenu.getItem i).getTitle() == menuName do return i
		return 0
	)

	fn unregisterMenuItem theMenu menuName =
	(	
		try
		(
			for i in 1 to theMenu.numItems() do
			(
				if((theMenu.getItem i).getTitle() == menuName) do
				(
					theMenu.removeItemByPosition i 	

					if((theMenu.getItem (i - 1)).getIsSeparator()) do theMenu.removeItemByPosition (i - 1)
				)
			)
		)catch()
	)

	item = try(findMenuItem theMenu "Select &Similar")catch(6)

	unregisterMenuItem theMenu txt
	
	if(not remove) do
	(
		quadItem = menuMan.createActionItem macro ("[" + cat + "]")
		
		theMenu.addItem quadItem (item += 1)
	)
		
	menuMan.updateMenuBar()
)

fn writeFile f s =
(			
	f = createFile f --mode: "wt"

	format(s as string) to:f

	flush f
	close f
)
/*
fn removeDir d =
(
	cmd = "RD /S /Q \"" + d + "\""
	hiddenDosCommand cmd
)
*/
fn getColor r g b = (dotnetclass "System.Drawing.Color").FromArgb (r as integer) (g as integer) (b as integer)
	
fn getFont style: #regular font: #tahoma size: 10 =
(
	d = dotnetclass "System.Drawing.FontStyle"
	i = case style of
	(
		#italic: d.Italic
		#bold: d.Bold
		default: d.Regular
	)
		
	z = case font of
	(
		#tahoma: "Tahoma"
		default: "Arial"
	)
	
	return dotnetobject "System.Drawing.Font" z size i
)

fn getBorderStyle s: #none =
(
	d = dotnetclass "System.Windows.Forms.BorderStyle"
	i = case s of
	(
		#single: d.FixedSingle
		#solid: d.Solid
		#fixed3d: d.Fixed3D	
		default: d.None	
	)
	
	return i
)

fn getScroll s: #vertical =
(
	d = dotNetClass "System.Windows.Forms.ScrollBars"
	i = case s of
	(
		default: d.Vertical
	)	

	return i
)

fn getBgColor = 
(
	b = (colorman.getcolor #background) * 255
	c = getColor b[1] b[2] b[3]
	return c
)

fn getTextColor =
(
	t = (colorMan.getColor #text) * 255
	c = getColor t[1] t[2] t[3]
	return c
)

fn copyAssets a d altPath: "" =
(				
	makeDir WIN_TEMP
	
	ini = WIN_TEMP + "uac.ini"
	iconv = WIN_TEMP + "uac.txt"
	uac = WIN_TEMP + uac_bat
	
	deleteFile ini
		
	if(doesFileExist ini) do deleteFile ini
	if(doesFileExist uac) do deleteFile uac
	if(doesFileExist iconv) do deleteFile iconv
	
	s = ""
		
	for i in a do
	(
		setIniSetting ini "FILES" i d
		if(altPath != "") do setIniSetting ini "ALTFILES" i altPath
		--if(altPath != "") do s += "copy \"" + i + "\" \"" + altPath  + "\" /Y \n"
		
		--s += "copy \"" + i + "\" \"" + d  + "\" /Y \n"
		
	)
	
	s += "TYPE \"" + ini + "\" > \"" + iconv + "\""
	s += "\nFOR /F \"EOL=[  TOKENS=1,2* DELIMS==\" \%\%I IN (" + iconv + ") DO COPY \"\%\%I\" \"\%\%J\" /Y"
	s += "\nDEL /F /Q \"" + ini + "\"" 
	s += "\nDEL /F /Q \"" + iconv + "\"" 
	s += "\nSTART /B \"\" CMD /C DEL \"\%~F0\"&EXIT /B\n"
				
	writeFile uac s
	
	-- IMPORTANT link must exist!
	HiddenDOSCommand (TEMP + "uac.lnk")	
)

fn unistallScript =
(	
	makeDir WIN_TEMP
	
	uac = WIN_TEMP + uac_bat
	ini = WIN_TEMP + "uac.ini"
	iconv = WIN_TEMP + "uac.txt"
	
	if(doesFileExist ini) do deleteFile ini
	if(doesFileExist uac) do deleteFile uac
	if(doesFileExist iconv) do deleteFile iconv
			
	m = getDir(#userMacros) + @"\_" + CAT + "_-" + MACRO + ".mcr"
	
	setIniSetting ini "FILES" m "F"
	setIniSetting ini "FILES" TEMP "D"
	
	for a in ICO_PATH do
	(
		setIniSetting ini "FILES" (a + MACRO + "*.bmp\"") "F"
	)
	
	s = ""	
	s += "TYPE \"" + ini + "\" > \"" + iconv + "\""
	s += "\nFOR /F \"EOL=[  TOKENS=1,2* DELIMS==\" \%\%I IN (" + iconv + ") DO (IF \%\%J==F DEL /F/ Q \"\%\%I\" \n IF \%\%J==D RD /S/ Q \"\%\%I\")"
	s += "\nDEL /F /Q \"" + ini + "\"" 
	s += "\nDEL /F /Q \"" + iconv + "\"" 
	s += "\nSTART /B \"\" CMD /C DEL \"\%~F0\"&EXIT /B\n"		
	
	addQuadMenuButton MACRO CAT TXT remove: true
	addToolBarButton MACRO CAT TXT remove: true
		
			
	writeFile uac s
	
	HiddenDOSCommand (TEMP + "uac.lnk")
)

fn installScript = 
(	
	if(not doesFileExist (DEST + FULLNAME)) do
	(
		messageBox "Not found installtion files!\n\nPlease run 3Ds Max with Administrator rights and try again!" title: "Error!"						
		
		return  try(closeRolloutFloater fInstallWiard) catch()
	)
	
	t = (TEMP + FULLNAME) 
	d = (DEST + FULLNAME) 
	i = (TEMP + @"icons\*.*") 
	
		
	if(ICONS) do
	(
		copyAssets (getFiles i) ICO_PATH[1] altPath:ICO_PATH[2]
	)

	createMacro()
	
	addQuadMenuButton MACRO CAT TXT remove: true
	addToolBarButton MACRO CAT TXT remove: true
		
	
	if(TOOLBAR) do addToolBarButton MACRO CAT TXT
	if(QUAD) do addQuadMenuButton MACRO CAT TXT					
)

fn freezeUi =
(
  	source = ""
  	source += "using System;\n"
  	source += "using System.Runtime.InteropServices;\n"
  	source += "class WindowsGhosting\n"
  	source += "{\n"
  	source += " [DllImport(\"user32.dll\")]\n"
  	source += " public static extern void DisableProcessWindowsGhosting();\n"
  	source += "}\n"
  
  	csharpProvider = dotnetobject "Microsoft.CSharp.CSharpCodeProvider"
  	compilerParams = dotnetobject "System.CodeDom.Compiler.CompilerParameters"
  
  	compilerParams.GenerateInMemory = on
  	compilerResults = csharpProvider.CompileAssemblyFromSource compilerParams #(source)
  
  	assembly = compilerResults.CompiledAssembly
  	windowsGhosting = assembly.CreateInstance "WindowsGhosting"
  	windowsGhosting.DisableProcessWindowsGhosting()
)

global rTitle
global rStage1
global rStage2
global rStage3

try(closeRolloutFloater fInstallWiard) catch()
global fInstallWiard  = newRolloutFloater  "Istallation Wizard" 500 400

rollout rTitle "" category:1
(
	dotNetControl _lblTitle "System.Windows.Forms.label" align: #left height: 24
	dotNetControl _lblInfo "System.Windows.Forms.label" align: #left
	label empty1 "" height: 3
	label hr "" height: 1 style_sunkenedge: true width: 460
		
	fn initDotnet =
	(
		_lblTitle.Font = getFont size: 14
		_lblInfo.BorderStyle =_lblTitle.BorderStyle = getBorderStyle s: #none
		_lblInfo.BackColor = _lblTitle.BackColor = getBgColor()
		_lblInfo.ForeColor = _lblTitle.ForeColor = getTextColor()
	)
	
	on rTitle open do 
	(	
		initDotnet()
			
		if(getFilenameType self == ".ms") do 
		(
			deleteFile encrFile
			encryptScript self version: 1
		)
	)
)

rollout rStage1 "" category:2
(		
	dotNetControl textBox "System.Windows.Forms.Textbox" height: 230 align:#center 
	label empty3 "" height: 3
	checkbox cbxAgree "I accept the term in the license agreement"
		
	label hr "" height: 1 style_sunkenedge: true width: 460	pos: [12, 275]
	button btnCancel "Cancel" width: 80 align: #left  pos: [10, 290]
	button btnNext "Next" width: 80 align: #right enabled: false pos: [395, 290]
	
	fn initDotnet =
	(				
		rTitle._lblTitle.text = TXT
		rTitle._lblInfo.text = "Please read the following information and terms before continuing"
				
		textBox.BorderStyle = getBorderStyle s: #single
		textBox.BackColor = getBgColor()
		textBox.ForeColor = getTextColor()
		textBox.MultiLine = true
		textBox.WordWrap = true
		textBox.ScrollBars = getScroll()
		textBox.ReadOnly = true
		
		textBox.text = getIniLicense()
	)
	
	on rStage1 open do 
	(	
		initDotnet()
		freezeUi()
	)
	
	on cbxAgree changed v do btnNext.enabled = v
	on btnCancel pressed do try(closeRolloutFloater fInstallWiard) catch()
	on btnNext pressed do
	(
		removeRollout rStage1 fInstallWiard
		addRollout rStage2 fInstallWiard border: false
	)
)

rollout rStage2 "" category:2
(
	group "Register inteface menus:"
	(
		label lblMenus "This setting helps to create their own buttons in the interface." align: #left
		label empty1 "" height: 3
		checkbox cbxToolBar "Tool Bar (Recommended)" checked: true
		checkbox cbxQuadMenu "Quad Menu"		
		edittext edtManualInstruction "" height: (if(maxVer < 16000) then 80 else 0) readonly: true visible: false
	)
	
	group "Setup options"
	(
		label lblSetup "" align: #left
		label empty2 "" height: 3
		radiobuttons rdoSetup "" labels: #("Install", "Remove") columns: 1 align: #left
	)
	
	label hr "" height: 1 style_sunkenedge: true width: 460	pos: [12, 275]
	button btnBack "Back" width: 80 align: #left  pos: [10, 290]
	button btnNext "Next" width: 80 align: #right pos: [395, 290]
			
	
	on rStage2 open do
	(
		rTitle._lblInfo.text = "Installing options."
		
		lblSetup.caption = "Select whether you want to install or remove " + TXT
		
		if(maxVer < 16000) then
		(
			cbxToolBar.enabled = false
			cbxToolBar.checked = false
			cbxQuadMenu.enabled = false
			cbxQuadMenu.checked = false			
			
			edtManualInstruction.text = "Your 3Ds Max does not support this feature.\nAdd the button manually after installation!"		
			edtManualInstruction.visible = true
		) 
	)
	
	on btnNext pressed do
	(
		ACTION = rdoSetup.state
		QUAD = cbxQuadMenu.checked
		TOOLBAR = cbxToolBar.checked
		
		removeRollout rStage2 fInstallWiard
		addRollout rStage3 fInstallWiard border: false
	)
	
	on btnBack pressed do
	(		
		removeRollout rStage2 fInstallWiard
		addRollout rStage1 fInstallWiard border: false
		rStage1.cbxAgree.checked = true
		rStage1.btnNext.enabled = true
	)
)

rollout rStage3 "" category:2 
(
	dotNetControl pbInstall "Windows.Forms.Progressbar" width:460 height:30 align: #center pos:[20, 100]
	edittext edtManualInstruction "" readonly: true pos: [10, -1000] height: 80
	dotNetControl lblStatus "System.Windows.Forms.label" pos: [20, 140]
	
	label hr "" height: 1 style_sunkenedge: true width: 460	pos: [12, 275]	
	button btnRun "Run Script" width: 80 align: #left  pos: [250 - 40, -1000]
	button btnAbout "About" width: 80 align: #left  pos: [250 - 40, -1000]
	button btnHelp "Help" width: 80 align: #left  pos: [250 - 40, -1000]
	button btnBack "Back" width: 80 align: #left  pos: [10, 290] enabled: false
	button btnFinish "Finish" width: 80 align: #right pos: [395, 290] enabled: false

	timer tmrInstall active: false interval: 10
	timer tmrLoadCui active: false intercal: 300
	
	global progress = 0
	
	fn initDotnet =
	(
		lblStatus.BorderStyle = getBorderStyle s: #none
		lblStatus.BackColor = getBgColor()
		lblStatus.ForeColor = getTextColor()
		lblStatus.TextAlign =  (getProperty lblStatus.TextAlign "MiddleCenter") 
	)
	
	fn showAbout =
	(
		try(destroyDialog rAbout)catch()
		
		rollout rAbout "About"
		(
			label lbl1 "Universal Installer Wizard" offset: [0, 20]
			label lbl2 "1.0.2"
			
			global grayColor = color 200 200 200 
			
			hyperLink href1 "MastaMan" address: "http://3ddd.ru/users/mastaman" align: #center hoverColor: grayColor visitedColor: grayColor offset: [0, 20]	
			hyperLink href2 "http://3dground.net" address: "http://3dground.net" align: #center hoverColor: grayColor visitedColor: grayColor
		)
		
		createDialog rAbout 200 150 modal: true
	)
	
	on tmrLoadCui tick do
	(
		f = cui.getConfigFile() 		
		
		cui.loadConfig f
		cui.setConfigFile f
		cui.saveConfigAs f
		cui.loadConfig f
		
		tmrLoadCui.active = false
	)
	
	on tmrInstall tick do 
	(	
		v = mod tmrInstall.ticks 500.0
		
		if(v == 70.0) do
		(
			case ACTION of
			(
				2: unistallScript()
				1: installScript()
			)			
		)
				
		
		if(v <= 100.0) then
		(
			try(pbInstall.value = v)catch()
			lblStatus.text = (v as integer) as string + "%"
		)
		else
		(					
			pbInstall.pos.y = -1000
			lblStatus.pos.y = 125			
			
			btnRun.pos.y = 160
			btnAbout.pos.y = 185
			
			if(maxVer < 16000) do edtManualInstruction.pos.y = 10
			
			if(HELP != "") do btnHelp.pos.y = 210
			
						
			case ACTION of
			(
				1: 
				(
					lblStatus.text = "Installed success!"					
				)
				2: 
				(
					btnRun.pos.y = -1000
					lblStatus.text = "Uninstall failed!"
				)
			)
			 			
			if(not doesFileExist (DEST + FULLNAME) or not doesFileExist (TEMP + "uac.lnk")) do
			(																
				case ACTION of
				(
					1: 
					(
						btnRun.pos.y = -1000
						lblStatus.text = "Installation failed!"							
					)
					2: 
					(
						lblStatus.text = "Uninstall success!"						
					)
				)
			)	
			
			tmrLoadCui.active = true
						
			btnFinish.enabled = true
			--btnBack.enabled = true
			tmrInstall.active = false
			
			colorman.reInitIcons()
		)		
	)
	
	on rStage3 open do
	(
		if(HELP == "") do btnHelp.enabled = false
		a = if(ACTION == 1) then "Install script" else "Remove script"
		rTitle._lblInfo.text = a	
		
		initDotnet()

		tmrInstall.active = true	
		
		edtManualInstruction.text = manualInstruction()
	)
	
	on btnBack pressed do
	(		
		removeRollout rStage3 fInstallWiard
		addRollout rStage2 fInstallWiard border: false				
	)
	
	on btnHelp pressed do shellLaunch HELP ""

	on btnAbout pressed do showAbout()
	
	on btnFinish pressed do try(closeRolloutFloater fInstallWiard) catch()
	
	on btnRun pressed do 
	(	
		try
		(
			try(closeRolloutFloater fInstallWiard) catch()
			fileIn (DEST + FULLNAME)			
		)catch(messageBox "Can't run the script :(" title:"Error!")
	)
)


addRollout rTitle fInstallWiard border: false 
addRollout rStage1 fInstallWiard border: false
	