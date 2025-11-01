/**
 * DllEntry.cpp - Plugin DLL entry point
 */

#define NOMINMAX
#include "max.h"
#include "UDIMSlicer.h"

HINSTANCE hInstance;

BOOL WINAPI DllMain(HINSTANCE hinstDLL, ULONG fdwReason, LPVOID lpvReserved) {
	if (fdwReason == DLL_PROCESS_ATTACH) {
		hInstance = hinstDLL;
		DisableThreadLibraryCalls(hInstance);
	}
	return TRUE;
}

__declspec(dllexport) const TCHAR* LibDescription() {
	return _T("UDIM Slicer - MaxManager");
}

__declspec(dllexport) int LibNumberClasses() {
	return 1;
}

__declspec(dllexport) ClassDesc* LibClassDesc(int i) {
	switch (i) {
		case 0: return GetUDIMSlicerDesc();
		default: return nullptr;
	}
}

__declspec(dllexport) ULONG LibVersion() {
	return VERSION_3DSMAX;
}

