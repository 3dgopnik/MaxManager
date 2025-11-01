/**
 * UDIMSlicer.cpp - Implementation
 */

#define NOMINMAX
#include "UDIMSlicer.h"

static UDIMSlicerClassDesc udimslicerDescInstance;
ClassDesc2* GetUDIMSlicerDesc() { return &udimslicerDescInstance; }

// Parameter block
static ParamBlockDesc2 udim_param_blk(
	pb_params, _T("params"), 0, GetUDIMSlicerDesc(),
	P_AUTO_CONSTRUCT, 0,
	
	pb_map_channel, _T("mapChannel"), TYPE_INT, P_ANIMATABLE, 0,
		p_default, 1,
		p_range, 1, 99,
		p_end,
	
	pb_flatten_w, _T("flattenW"), TYPE_BOOL, 0, 0,
		p_default, TRUE,
		p_end,
	
	pb_remove_errors, _T("removeErrors"), TYPE_BOOL, 0, 0,
		p_default, TRUE,
		p_end,
	
	pb_vertex_weld, _T("vertexWeld"), TYPE_BOOL, 0, 0,
		p_default, TRUE,
		p_end,
	
	pb_weld_threshold, _T("weldThreshold"), TYPE_FLOAT, P_ANIMATABLE, 0,
		p_default, 0.001f,
		p_range, 0.0001f, 1.0f,
		p_end,
	
	p_end
);

UDIMSlicer::UDIMSlicer() {
	pblock = nullptr;
	GetUDIMSlicerDesc()->MakeAutoParamBlocks(this);
}

RefTargetHandle UDIMSlicer::Clone(RemapDir& remap) {
	UDIMSlicer* newMod = new UDIMSlicer();
	newMod->ReplaceReference(0, remap.CloneRef(pblock));
	BaseClone(this, newMod, remap);
	return newMod;
}

Interval UDIMSlicer::LocalValidity(TimeValue t) {
	if (pblock == nullptr) return FOREVER;
	Interval valid = FOREVER;
	pblock->GetValidity(t, valid);
	return valid;
}

void UDIMSlicer::ModifyObject(TimeValue t, ModContext& mc, ObjectState* os, INode* node) {
	if (os->obj == nullptr) return;
	if (os->obj->SuperClassID() != GEOMOBJECT_CLASS_ID) return;
	
	PolyObject* polyObj = nullptr;
	if (os->obj->IsSubClassOf(polyObjectClassID)) {
		polyObj = (PolyObject*)os->obj;
	} else if (os->obj->CanConvertToType(polyObjectClassID)) {
		polyObj = (PolyObject*)os->obj->ConvertToType(t, polyObjectClassID);
	}
	
	if (polyObj == nullptr) return;
	
	SliceMeshByUDIM(polyObj, t);
	os->obj->UpdateValidity(GEOM_CHAN_NUM, LocalValidity(t));
}

void UDIMSlicer::SliceMeshByUDIM(PolyObject* polyObj, TimeValue t) {
	if (polyObj == nullptr || pblock == nullptr) return;
	
	// Get parameters
	int mapChannel = 1;
	pblock->GetValue(pb_map_channel, t, mapChannel, FOREVER);
	
	MNMesh& mesh = polyObj->GetMesh();
	
	// TODO: Implement slicing algorithm
	// For now do nothing
}

