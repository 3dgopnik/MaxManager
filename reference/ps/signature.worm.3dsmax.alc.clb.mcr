/*

	Signature for detect and remove ALC scripts.
	Detect: Worm.3dsmax.ALC.clb
	Prune: 
		- vrdematcleanbeta.mse
		- vrdematcleanbeta.msex
		- infected objects
		
	Vasily Lukyanenko
	http://3dground.net
		
*/

(
	struct signature_worm_3dsmax_alc_clb (
		name = "[Worm.3dsmax.ALC.clb]",
		signature = (substituteString (getFileNameFile (getThisScriptFileName())) "." "_"),		
		find = "cleanbeta",
		detect_events = #(#filePostOpen, #systemPostReset, #filePostMergeProcess),
		fn getGlobals =
		(
			vars = globalVars.gather()	
			found = for v in vars where (findString (toLower (v as string)) find != undefined) collect v
		),
			
		fn detect = (
			found = getGlobals()
			
			if(found == undefined) do return false
			return found.count != 0 
		),
		
		fn getInfectedFiles = (
			dirs = #(#userStartupScripts, #startupScripts)
			out = #()
			for d in dirs do 
			(		
				files = getFiles ((getDir d) + @"\*.*")
				for f in files where (findString (toLower f) find != undefined) do append out f
			)
			
			return out
		),

		fn dispose = (
			for i in 1 to detect_events.count do (
				id = i as string				
				execute ("callbacks.removeScripts id: #" + signature + id)								
			)	
		),
		
		fn run = (	
		
			progressStart ("Find " + name + "...")
			escapeEnable
			
			for i in 1 to detect_events.count do (
				id = i as string
				f = substituteString (getThisScriptFileName()) @"\" @"\\"
				f = substituteString f @"\\\\" @"\\\\\"
									
				execute ("callbacks.removeScripts id: #" + signature + id)
				execute ("callbacks.addScript #" + detect_events[i] as string + "  \" try(fileIn @\\\"" + f + "\\\") catch() \" id: #" + signature + id)
			)	
				
			
			if(detect() == false) do  
			(				
				for i in 1 to 100 by 3 do 
				(
					progressUpdate i
					sleep 0.001
				)
				
				progressEnd()
				
				displayTempPrompt  ("Success! " + name + " not detected!") 10000
				return false
			)
						
			for f in getInfectedFiles() do deleteFile f
				
			findAgain = getInfectedFiles()
			if(findAgain.count != 0) do (
				print "Files not deleted! Please delete manually next files:"
				for f in findAgain do print f		
			)
			
			events = #(#RenderLicCleanBeta,#PhysXCleanBetaRBKSysInfo, #AutodeskLicCleanBeta, #AutodeskLicences,#PhysXCreateRBKSysInfo,#RenderLicences,#AutodeskLicAlpha,#PhysXAlphaRBKSysInfo,#RenderLicAlpha,#AutodeskLicCleanAlpha,#PhysXCleanAlphaRBKSysInfo,#RenderLicCleanAlpha)	
			for ev in events do try(callbacks.removeScripts id: ev) catch()
					
			for o in objects where not isDeleted o and classOf o == Point and findString o.name "×" != undefined do
			(				
				o.name = "_____alc"
				try (delete o) catch()
			)	
				
			ini = ((getDir #plugcfg) + @"\ExplorerConfig\SceneExplorer\DefaultModalSceneExplorer.ini")
			setIniSetting ini "Explorer" "Hidden" "true"
			setIniSetting ini "Explorer" "Frozen" "true"
			
			globals = globalVars.gather filter: (fn test name val = (findString (toLower (name as string)) "cleanbeta" != undefined))​			
			if(globals != undefined) do for g in globals do globalVars.remove g
			
			messageBox (name + " virus detected and removed!") title: "Notification!"
				
			progressEnd()
		)
	)
	
	local signature = signature_worm_3dsmax_alc_clb()
	signature.run()
)



