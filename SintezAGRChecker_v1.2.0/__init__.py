bl_info = {
    "name": "AGR Model Checker",
    "author": "SINTEZ.SPACE",
    "version": (1, 1, 4),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > AGR Checker",
    "description": "AGR Model Checker",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import os
import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import FloatVectorProperty, StringProperty, PointerProperty, IntProperty, FloatProperty, BoolProperty, CollectionProperty, EnumProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import addon_utils
from bpy.utils import previews

from .scripts import model_preparer
from .scripts import selection
from .scripts import ui_utills
from .scripts import properties
from .scripts import operators
from .scripts import logger
from .scripts import os_utils
from .scripts import utills
from .scripts import export_models


class VIEW3D_PT_Parent:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SINTEZ AGR"
    # bl_options = {"DEFAULT_CLOSED"}

class VIEW3D_PT_Main(VIEW3D_PT_Parent, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_Main'
    # bl_space_type = 'VIEW_3D'
    # bl_region_type = 'UI'
    # bl_category = 'AGR Checker'
    bl_label = 'SINTEZ AGR Checker'

    def draw(self, context):
        scene = context.scene
        scene_properties = scene.agr_scene_properties
        layout = self.layout
        
        row = layout.row()
        row.template_icon(icon_value=ui_utills.plugin_icons['sintez_alpha.png'].icon_id, scale=2.2)

        col = row.column()
        col.scale_x = 0.45
        help_op = col.operator('wm.url_open', text='Инструкция', icon='HELP')
        help_op.url = 'https://docs.google.com/document/d/1VxtQ8otPxo6o2OmFUX0WOyl8yOaw9vqSFpaFBZsPG1c/edit?usp=sharing'
        dev_row = col.row(align=True)
        sintez_op = dev_row.operator('wm.url_open', text='Разработчик', icon='URL')
        sintez_op.url = 'https://sintez.space/plugins'
        donate_op = dev_row.operator('wm.url_open', text='Поддержать', icon_value=ui_utills.plugin_icons['red_heart_icon.png'].icon_id) # red_heart_icon.png
        donate_op.url = 'https://boosty.to/synthesismoscow'
        layout.separator(type='LINE')
        
        layout.label(text="Подготовка моделей")
        layout.prop(scene_properties, "path", text="Архивы АГР")
        # layout.separator(type='LINE')
        row = layout.row()
        row.operator(operator="agr.run_calculate_all", icon='PLAY', text="Проверить все файлы АГР (очищает blender файл)")
        row.scale_y = 1.5
        import_row = layout.row()
        import_row.operator(operator="agr.clear_blender_file_button", icon='TRASH', text="Очистить файл")
        import_row.operator(operator="agr.import_models_button", icon='IMPORT', text="Импортировать модели")

        layout.separator(type='LINE')

        layout.label(text="Экспорт моделей")
        export_row = layout.row()
        export_settings = context.scene.agr_collection_settings
        export_row.operator(operator="agr.export_run", icon='EXPORT', text="Экспортировать модели")
        export_row.prop(export_settings, "save_old_archives", text="Сохранять старые архивы")
        # row = layout.row()
        # row.label(text=f"Старые версии ({export_settings.saves_size_info})")

        # layout.operator(operator="agr.run_calculate_all_collections", icon_value=ui_utills.icons['test_icon_2.png'].icon_id)
        # layout.operator(operator="agr.run_calculate_all_collections", icon='OUTLINER_COLLECTION')
        layout.separator(type='LINE')
        layout.label(text="Отображение модели")
        layout.prop(scene_properties, "view_mode", expand=True)
        row = layout.row()

        small_row = row.row(align=True)
        show_lp_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_lp else 'HIDE_ON'
        small_row.prop(context.scene.agr_scene_properties, "show_lp", text="НПМ", icon=show_lp_icon)
        zoom_op = small_row.operator(operator="agr.zoom_model", icon='VIEWZOOM', text="")
        zoom_op.is_highpoly = False

        small_row = row.row(align=True)
        show_hp_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_hp else 'HIDE_ON'
        small_row.prop(context.scene.agr_scene_properties, "show_hp", text="ВПМ", icon=show_hp_icon)
        zoom_op = small_row.operator(operator="agr.zoom_model", icon='VIEWZOOM', text="")
        zoom_op.is_highpoly = True

        add_row = layout.row()
        show_ucx_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_ucx else 'HIDE_ON'
        add_row.prop(context.scene.agr_scene_properties, "show_ucx", text="UCX", icon=show_ucx_icon)

        show_glass_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_glass else 'HIDE_ON'
        add_row.prop(context.scene.agr_scene_properties, "show_glass", text="Glass", icon=show_glass_icon)

        show_lights_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_lights else 'HIDE_ON'
        add_row.prop(context.scene.agr_scene_properties, "show_lights", text="Light", icon=show_lights_icon)

        # show_glass_grid_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_glass_grid else 'HIDE_ON'
        # layout.prop(context.scene.agr_scene_properties, "show_glass_grid", text="Стекло сетка", icon=show_glass_grid_icon)

        # row = layout.row()
        # row.operator(operator="agr.glass_all_gray", text="Все стекла белые")
        # show_glass_grid_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_glass_grid else 'HIDE_ON'
        # row.prop(context.scene.agr_scene_properties, "show_glass_grid", text="Стекла UV Color grid", icon=show_glass_grid_icon)
        # layout.operator(operator="agr.test_debug", text="import fbx")

        layout.separator(type='LINE')
        # layout.prop(scene_properties, "check_author", text="Проверяющий")
        layout.label(text="Отчет об ошибках")
        row = layout.row()
        row.operator(operator="agr.save_report_button_operator", text="Сохранить отчет")
        # row.operator(operator="agr.load_report_button_operator")
        row.operator(operator="agr.show_project_folder_button_operator", text="Показать папку")
        # layout.prop(scene_properties, "load_report_path", text="Load report")
        layout.separator(type='LINE')

class VIEW3D_PT_Checklist_Settings(VIEW3D_PT_Parent, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_Main"
    bl_label = 'Настройки чеклиста'
    bl_options = {"DEFAULT_CLOSED"}
 
    def draw(self, context):
        scene = context.scene
        scene_properties = scene.agr_scene_properties
        layout = self.layout
        
        # layout.prop(scene_properties, "Address")
        # row = layout.row()
        # layout.prop(context.scene.agr_scene_properties, "experimental_checks", text="Экспериментальные проверки")
        layout.prop(context.scene.agr_scene_properties, "unlock_auto_checks", text="Разблокировать автопроверки", icon='AUTO')
        show_req_nums_icon = 'HIDE_OFF' if context.scene.agr_scene_properties.show_req_nums else 'HIDE_ON'
        layout.prop(context.scene.agr_scene_properties, "show_req_nums", text="Отображать номера проверок", icon=show_req_nums_icon)

class VIEW3D_PT_Checklist_Lowpoly(VIEW3D_PT_Parent, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_Main"
    bl_label = 'НПМ Чеклист'

    def draw(self, context):
        if os_utils.check_models_path():
            ui_utills.drow_checklist(False, context, self.layout)
        else:
            ui_utills.drow_label_multiline(context, "Укажите путь к архивам, чтобы начать работу с чеклистом!", self.layout, width=250)

class VIEW3D_PT_Checklist_Highpoly(VIEW3D_PT_Parent, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_Main"
    bl_label = 'ВПМ Чеклист'
 
    def draw(self, context):
        if os_utils.check_models_path():
            ui_utills.drow_checklist(True, context, self.layout)
        else:
            ui_utills.drow_label_multiline(context, "Укажите путь к архивам, чтобы начать работу с чеклистом!", self.layout, width=250)

class VIEW3D_PT_Check_Geojson(VIEW3D_PT_Parent, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_Main"
    bl_label = 'Проверка Geojson'
    bl_options = {"DEFAULT_CLOSED"}
 
    def draw(self, context):
        if not os_utils.check_models_path():
            ui_utills.drow_label_multiline(context, "Укажите путь к архивам, чтобы начать работу с чеклистом!", self.layout, width=250)
            return
        
        scene = context.scene
        scene_properties = scene.agr_scene_properties
        layout = self.layout

        layout.label(text="Параметры для проверки Geojson")
        layout.prop(scene_properties, "geojson_ZU_area", text="ZU_area")
        layout.prop(scene_properties, "geojson_h_relief", text="h_relief")
        layout.prop(scene_properties, "geojson_s_obsh", text="s_obsh")
        layout.prop(scene_properties, "geojson_s_naz", text="s_naz")
        layout.prop(scene_properties, "geojson_s_podz", text="s_podz")
        layout.prop(scene_properties, "geojson_spp_gns", text="spp_gns")

        layout.operator(operator="agr.check_geojson", text="Проверить!")

        categories = context.scene.agr_scene_properties.geojson_categories

        layout.separator(type='LINE')

        if not categories:
            return

        rows_count = len(categories[0].collection) + 1
        columns_count = len(categories) + 1

        box = layout.box()
        row = box.row()
        cols = [row.column() for i in range(columns_count)]
        for i in range(columns_count):
            for j in range(rows_count):
                if i == 0 and j == 0:
                    cols[i].label(text="")
                elif i == 0:
                    cols[0].label(text=categories[0].collection[j-1].name)
                elif j == 0:
                    name = categories[i-1].name if categories[i-1].name else "ОКС"
                    cols[i].label(text=name)
                else:
                    # cols[i].label(text=categories[i-1].collection[j-1].description)

                    cell = cols[i].row()
                    item = categories[i-1].collection[j-1]
                    op_icon = 'CHECKMARK'
                    if item.check_state == "undefined":
                        op_icon = 'BLANK1'
                    elif item.check_state == "verified":
                        op_icon = 'CHECKMARK'
                    elif item.check_state == "failed":
                        # op_icon = 'PANEL_CLOSE'
                        op_icon = 'X'
                    cell.alignment='LEFT'
                    cell.alert = True if item.check_state == utills.CHECK_STATE_ITEMS[2] else False
                    cell.enabled = not item.auto or context.scene.agr_scene_properties.unlock_auto_checks
                    # check_op = cell.operator(operator="agr.checkbox_test_operator", icon=op_icon, text=item.description, emboss=False)
                    check_op = cell.operator(operator="agr.checkbox_test_operator", text=item.description, emboss=False)
                    # check_op.tooltip = item.description
                    check_op.tooltip = ""
                    check_op.category = item.category
                    check_op.index = j - 1
                    # check_op.is_highpoly = item.highpoly
                    check_op.geojson_list = True

class VIEW3D_PT_TexelDencity(VIEW3D_PT_Parent, bpy.types.Panel):
    # bl_parent_id = "VIEW3D_PT_Main"
    # bl_label = 'Texel Dencity'
    # bl_options = {"DEFAULT_CLOSED"}

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SINTEZ AGR"

    bl_idname = 'VIEW3D_PT_TexelDencity'
    bl_label = 'Texel Density'
    bl_options = {"DEFAULT_CLOSED"}
 
    def draw(self, context):
        # self.layout.label(text="Texel density")

        scene = context.scene
        scene_properties = scene.agr_scene_properties
        layout = self.layout

        row = self.layout.row(align=True)
        row.label(text="Значения для: ")
        lp = row.operator("agr.td_values_set", text="НПМ")
        lp.is_highpoly = False
        lp = row.operator("agr.td_values_set", text="ВПМ")
        lp.is_highpoly = True

        box = layout.box()

        row = box.row(align=True)
        row.label(text="Нижняя граница (px/m):")
        row.prop(scene_properties, "td_min", text="")
        row = box.row(align=True)
        row.label(text="Верхняя граница (px/m):")
        row.prop(scene_properties, "td_max", text="")
        row = box.row(align=True)
        row.label(text="Размер текстуры (px):")
        row.prop(scene_properties, "texture_size_enum", text="")
        texture_size_enum = context.scene.agr_scene_properties.texture_size_enum
        if texture_size_enum == "Custom":
            # row = box.row()
            # row.label(text="")
            row.prop(scene_properties, "texture_size", text="")

        self.layout.operator(
            operator='agr.select_texel_less',
            text='Выбрать полигоны МЕНЬШЕ допуска'
        )

        self.layout.operator(
            operator='agr.select_texel_greater',
            text='Выбрать полигоны БОЛЬШЕ допуска'
        )

        # self.layout.operator(
        #     operator='agr.select_out_udim',
        #     text='select_udim_out'
        # )


classes = (
    properties.CUSTOM_objectCollection_Image,
    properties.CUSTOM_objectCollection,
    properties.CUSTOM_objectCollection_category,
    properties.ChecklistProperties,
    properties.CUSTOM_objectCollection_TD_error,
    properties.AGRCheckerProperties,
    model_preparer.ImportModelsOperator,
    selection.SelectTexelLessOperator,
    selection.SelectTexelGreaterOperator,
    selection.SelectUdimOutOperator,
    selection.TDValuesSetOperator,
    VIEW3D_PT_Main,
    VIEW3D_PT_Checklist_Settings,
    VIEW3D_PT_Checklist_Lowpoly,
    VIEW3D_PT_Checklist_Highpoly,
    VIEW3D_PT_Check_Geojson,
    VIEW3D_PT_TexelDencity,
    operators.ShowChecklist,
    operators.UpdateRequrements,
    operators.ImportModelsButton,
    operators.ClearBlenderFileButton,
    operators.RunCalculate_all,
    operators.RunCalculate_all_collections,
    operators.ClearChecklist,
    operators.CheckboxTestOperator,
    operators.ErrorsButtonOperator,
    operators.CheckHelpLinkOperator,
    operators.EditCheckButton,
    operators.SaveReportButtonOperator,
    operators.ShowProjectFolderButtonOperator,
    operators.AddImageCheckButton,
    operators.ModifyImageCheckButton,
    operators.GlassAllGray,
    operators.CheckGeojson,
    operators.CheckLowpolyCode,
    operators.TestDebugOperator,
    operators.HpSelectTexelLessOperator,
    operators.HpSelectTexelGreaterOperator,
    operators.SelectTexelErrorsOperator,
    operators.ZoomModel,
    operators.OneColorPlugsFixOperator,
    operators.AlphaFixOperator,
    operators.DoublesAndLooseFixOperator,
)


@bpy.app.handlers.persistent
def load_post_handler(dummy):
    pass
    # print("Event: load_post" + bpy.data.filepath)
    # logger.add("Event: load_post" + bpy.data.filepath)
    # ui_utills.update_images()

    # scene_props = bpy.context.scene.agr_scene_properties
    # scene_props.checklist_hp_props.categories.clear()
    # scene_props.checklist_lp_props.categories.clear()

    # operators.UpdateRequrements.update_requrements(True)
    # operators.UpdateRequrements.update_requrements(False)


def register():
    export_models.register()
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.agr_scene_properties = PointerProperty(type=properties.AGRCheckerProperties)
    # bpy.types.object.agr_td_less = []
    # bpy.types.object.agr_td_greater = []
    bpy.app.handlers.load_post.append(load_post_handler)
    print("Sintez AGR Checker register")

def unregister():
    export_models.unregister()
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass

    del bpy.types.Scene.agr_scene_properties
    # del bpy.types.object.agr_td_less
    # del bpy.types.object.agr_td_greater
    bpy.app.handlers.load_post.remove(load_post_handler)
    print("Sintez AGR Checker unregister")

if __name__ == "__main__":
    register()

