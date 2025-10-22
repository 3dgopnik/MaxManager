try(destroyDialog _rUpdater)catch()
rollout _rUpdater "Update" width: 300 height: 300
(
	dotNetControl lblTask "System.Windows.Forms.Label" height: 20
	
	button btnUpdate "Update To Latest Version" enabled: false height: 30 offset: [0, 10]
	dotNetControl edtNotes "System.Windows.Forms.Textbox" width: 298 height: 212 align:#center offset: [0, 10]
	
	fn getColor r g b = (dotnetclass "System.Drawing.Color").FromArgb r g b
	
	timer tmrCheckUpdates "" active: false interval: 500

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
	
	fn setTask msg:"" type: #grey =
	(
		t = #(67,67,67)
		b = #(183,183,183)
		
		if(type == #red) do 
		(
			t = #(153,0,0)
			b = #(224,102,102)
		)
		if(type == #green) do 
		(
			t = #(56,118,79)
			b = #(147,196,125)
		)
		if(type == #yellow) do 
		(
			t = #(205,144,0)
			b = #(255,229,153)
		)
				
		lblTask.BackColor = getColor b[1] b[2] b[3]
		lblTask.ForeColor = getColor t[1] t[2] t[3]
		
		lblTask.Font = dotNetObject "System.Drawing.Font" "Tahoma" 10 ((dotNetClass "System.Drawing.FontStyle").Bold)
		lblTask.TextAlign = lblTask.TextAlign.MiddleCenter
		lblTask.text = msg
	)
	
	fn initDotnet =
	(
		edtNotes.Font = dotNetObject "System.Drawing.Font" "MS Sans Serif" 8 ((dotNetClass "System.Drawing.FontStyle").Regular)
		edtNotes.BorderStyle = (dotNetClass "System.Windows.Forms.BorderStyle").FixedSingle
		edtNotes.BackColor = getBgColor()
		edtNotes.ForeColor = getTextColor()
		edtNotes.MultiLine = true
		edtNotes.WordWrap = true
		edtNotes.ScrollBars = (dotNetClass "System.Windows.Forms.ScrollBars").Vertical
		edtNotes.ReadOnly = true
		setTask msg: "Check for updates..."
	)
	
	struct updateClient (
		updFile = "",
		updPath = "",
		installFile = "",
		checkUrl = "",
		currVer = "",
		currScript = "",
		checkUpdMsg = #red,
		releaseNotes = "",
		mzpPackage = "",
		currPath = "",
				
		fn info v =
		(
			getIniSetting updFile "INFO" v
		),
		
		fn getNotes =
		(
			n = getIniSetting updFile "NOTES"
			t = info "TEXT"
			v = info "VER"
			s = info "SCRIPT"
			
			releaseNotes = "Release Notes \"" + s + " " + v + "\": \r\n\r\n"
			if(t != "") do releaseNotes += t + "\r\n\r\n"
			for note in n do releaseNotes += note + "\r\n"
		),
		
		fn downloadFile url dl=
		(
			deleteFile dl
			w = dotNetObject "System.Net.WebClient"			
			try(				
				w.DownloadFile (url + "?time=" + timestamp() as string) dl				
				return dl
			) catch(
				return #red
			)
		),
		
		fn downloadPackage =
		(			
			updPath = currPath + (filenameFromPath mzpPackage)
			return downloadFile mzpPackage updPath
		),
		
		fn init = 
		(
			currPath = getFilenamePath (getThisScriptFileName())
			updFile =  currPath + "update.ini"
			installFile =  currPath + "install.ini"
				
			checkUrl = getIniSetting installFile "UPDATE" "CHECK"
				
			currVer = getIniSetting installFile "UPDATE" "CURR_VER"
			currScript = getIniSetting installFile "INSTALL" "MACRO"	
									
						
			r = downloadFile checkUrl updFile
			if(r == #red) do return updFile = r
						
			v = info "VER"
			s = info "SCRIPT"
			mzpPackage = info "MZP_PACKAGE"

			if(s != currScript or v == "" or mzpPackage == "") do return updFile = #red
		), 
				
		fn checkNewVersion = (
			
			if(updFile == #red) do 
			(
				checkUpdMsg = "Can't connect to server :("
				return #red
			)
			v = info "VER"
					
			if(v > currVer) do 
			(
				checkUpdMsg = "Available new version: " + v
				getNotes()
				return #green
			)
			
			checkUpdMsg = "You are using the latest version!"
			return #yellow
		)
	)
	
	fn checkUpdates =
	(			
		upd = updateClient()
		upd.init()		
		isUpdate = upd.checkNewVersion()
					
		setTask	msg: upd.checkUpdMsg type: isUpdate
			
		if(isUpdate == #green) do
		(
			_rUpdater.height = 300
			btnUpdate.enabled = true
			edtNotes.text = upd.releaseNotes
		)
	)
	
	fn downloadAndInstallUpdates = 
	(
		btnUpdate.enabled = false
		
		setTask	msg: "Downloading Package..."
		
		upd = updateClient()
		upd.init()
		p = upd.downloadPackage()
		
		setTask	msg: "Unpack files..."
		
		isUnpack = msZip.unloadPackage p &extractDir &dropFile

		if(isUnpack) then (
			setTask	msg: "Updates have been installed!" type: #green
			
			m = "Updates have been installed!"
			m += "\n\nPlease restart the script!"
			messageBox m title: "Success!" beep: false
		) else (
			setTask	msg: "An error has occurred!" type: #red
		)
		
		btnUpdate.enabled = true
	)
	
	on btnUpdate pressed do
	(			
		downloadAndInstallUpdates()			
	)
	
	on _rUpdater open do
	(	
		initDotnet()		
		tmrCheckUpdates.active = true
		
		_rUpdater.height = 80
	)
		
	
	on tmrCheckUpdates tick do
	(
		checkUpdates()
		tmrCheckUpdates.active = false;
	)
)

createDialog _rUpdater modal:true