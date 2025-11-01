/**
 * UDIMSlicer.h - UDIM Slicer Modifier
 */

#pragma once

#define NOMINMAX
#include "max.h"
#include "iparamb2.h"
#include "iparamm2.h"
#include "modstack.h"
#include "MNMesh.h"
#include "polyobj.h"

extern TCHAR* GetString(int id);
extern HINSTANCE hInstance;

#define UDIMSLICER_CLASS_ID	Class_ID(0x7a3e4f21, 0x6b2c1d90)

enum { pb_params };
enum { pb_map_channel, pb_flatten_w, pb_remove_errors, pb_vertex_weld, pb_weld_threshold };

class UDIMSlicer : public Modifier {
public:
	UDIMSlicer();
	~UDIMSlicer() {}
	
	// From Animatable
	void DeleteThis() override { delete this; }
	Class_ID ClassID() override { return UDIMSLICER_CLASS_ID; }
	void GetClassName(MSTR& s, bool localized) const override { s = _T("UDIM Slicer"); }
	const TCHAR* GetObjectName(bool localized) const override { return _T("UDIM Slicer"); }
	
	// From ReferenceMaker
	RefTargetHandle Clone(RemapDir& remap) override;
	int NumRefs() override { return 1; }
	RefTargetHandle GetReference(int i) override { return pblock; }
	void SetReference(int i, RefTargetHandle rtarg) override { pblock = (IParamBlock2*)rtarg; }
	RefResult NotifyRefChanged(const Interval& changeInt, RefTargetHandle hTarget, PartID& partID, RefMessage message, BOOL propagate) override { return REF_SUCCEED; }
	
	// From Modifier
	Interval LocalValidity(TimeValue t) override;
	ChannelMask ChannelsUsed() override { return GEOM_CHANNEL | TOPO_CHANNEL | TEXMAP_CHANNEL; }
	ChannelMask ChannelsChanged() override { return GEOM_CHANNEL | TOPO_CHANNEL; }
	Class_ID InputType() override { return polyObjectClassID; }
	void ModifyObject(TimeValue t, ModContext& mc, ObjectState* os, INode* node) override;
	CreateMouseCallBack* GetCreateMouseCallBack() override { return nullptr; }
	
	IParamBlock2* pblock;
private:
	void SliceMeshByUDIM(PolyObject* polyObj, TimeValue t);
};

class UDIMSlicerClassDesc : public ClassDesc2 {
public:
	int IsPublic() override { return TRUE; }
	void* Create(BOOL loading = FALSE) override { return new UDIMSlicer(); }
	const TCHAR* ClassName() override { return _T("UDIM Slicer"); }
	const TCHAR* NonLocalizedClassName() override { return _T("UDIM Slicer"); }
	SClass_ID SuperClassID() override { return OSM_CLASS_ID; }
	Class_ID ClassID() override { return UDIMSLICER_CLASS_ID; }
	const TCHAR* Category() override { return _T("MaxManager"); }
	const TCHAR* InternalName() override { return _T("UDIMSlicer"); }
	HINSTANCE HInstance() override { return hInstance; }
};

ClassDesc2* GetUDIMSlicerDesc();

