# bl_info = {
#     "name": "AGR Export Tools",
#     "description": "Инструменты для экспорта моделей из AGR_checker",
#     "author": "computer_invaders",
#     "version": (1, 0, 0),
#     "blender": (4, 2, 0),
#     "location": "3D Viewport > Sidebar > AGR_export",
#     "category": "Import-Export"
# }

import bpy
import bmesh
from mathutils import Vector
import re
import os
import zipfile
import datetime
import shutil

from . import os_utils
from . import utills

class AGR_CollectionItem(bpy.types.PropertyGroup):
    """Элемент коллекции с настройками экспорта"""
    name: bpy.props.StringProperty(name="Название коллекции")
    is_low_poly: bpy.props.BoolProperty(name="Низкополигональная", default=False)
    is_light: bpy.props.BoolProperty(name="Световая", default=False)
    enabled: bpy.props.BoolProperty(name="Включить в экспорт", default=True)
    object_count: bpy.props.IntProperty(name="Количество объектов", default=0)
    material_count: bpy.props.IntProperty(name="Количество материалов", default=0)
    texture_count: bpy.props.IntProperty(name="Количество текстур", default=0)
    triangle_count: bpy.props.IntProperty(name="Количество треугольников", default=0)

class AGR_ExportedFolder(bpy.types.PropertyGroup):
    """Папка куда экспортировалась коллекция"""
    folder_name: bpy.props.StringProperty(name="Имя папки")
    collection_name: bpy.props.StringProperty(name="Имя коллекции")

class AGR_CollectionSettings(bpy.types.PropertyGroup):
    """Настройки коллекций для экспорта"""
    collection_items: bpy.props.CollectionProperty(type=AGR_CollectionItem)
    collection_index: bpy.props.IntProperty(name="Индекс коллекции", default=0)
    last_export_path: bpy.props.StringProperty(name="Путь последнего экспорта", default="")
    exported_folders: bpy.props.CollectionProperty(type=AGR_ExportedFolder)

    save_old_archives: bpy.props.BoolProperty(default=False,
                                              description="При экспорте моделей, переносит старые архивы в папку 'AGRChecker_export_saves' и в подпапки по дате экспорта. При необходимости старые архивы можно удалить вручную.")
    saves_size_info: bpy.props.StringProperty()

def exit_local_view():
    """Выходит из Local View если он активен"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if space.local_view:
                        with bpy.context.temp_override(area=area, space=space):
                            bpy.ops.view3d.localview(frame_selected=False)
                        print("🔓 Выход из Local View выполнен")
                        return True
    return False

LOW_POLY_SETTINGS = {
    'use_selection': False,
    'use_visible': False,
    'use_active_collection': False,
    'global_scale': 1.0,
    'apply_unit_scale': True,
    'apply_scale_options': 'FBX_SCALE_ALL',
    'use_space_transform': True,
    'bake_space_transform': False,
    'object_types': {'EMPTY', 'MESH', 'LIGHT'},
    'use_mesh_modifiers': True,
    'use_mesh_modifiers_render': True,
    'mesh_smooth_type': 'FACE',
    'colors_type': 'SRGB',
    'prioritize_active_color': False,
    'use_subsurf': False,
    'use_mesh_edges': False,
    'use_tspace': False,
    'use_triangles': True,
    'use_custom_props': False,
    'add_leaf_bones': False,
    'primary_bone_axis': 'Y',
    'secondary_bone_axis': 'X',
    'use_armature_deform_only': False,
    'armature_nodetype': 'NULL',
    'bake_anim': False,
    'bake_anim_use_all_bones': True,
    'bake_anim_use_nla_strips': True,
    'bake_anim_use_all_actions': True,
    'bake_anim_force_startend_keying': True,
    'bake_anim_step': 1.0,
    'bake_anim_simplify_factor': 1.0,
    'path_mode': 'COPY',
    'embed_textures': True,
    'batch_mode': 'OFF',
    'use_batch_own_dir': True,
    'axis_forward': '-Z',
    'axis_up': 'Y'
}

def is_low_poly_collection(collection_name):
    """Проверяет, является ли коллекция низкополигональной по четырехзначному коду в начале имени"""
    pattern = r'^\d{4}(?!\d)'
    return bool(re.match(pattern, collection_name))

def get_low_poly_collections():
    """Возвращает список низкополигональных коллекций"""
    low_poly_collections = []
    for collection in bpy.data.collections:
        if is_low_poly_collection(collection.name):
            low_poly_collections.append(collection)
    return low_poly_collections

def get_high_poly_export_folder(collection_name):
    """Возвращает имя папки для экспорта high-poly коллекции (без .fbx и _Light)"""
    name = collection_name
    if name.endswith('_Light'):
        name = name[:-6]
    if name.lower().endswith('.fbx'):
        name = name[:-4]
    return name

def get_low_poly_export_folder(collection_name):
    """Возвращает 4-значный код из начала имени коллекции для low-poly папки"""
    import re
    match = re.match(r'^(\d{4})', collection_name)
    if match:
        return match.group(1)
    return 'lowpoly'

def is_light_collection(collection_name):
    """Проверяет, является ли коллекция световой (содержит Light в названии)"""
    return '_Light' in collection_name or 'Light' in collection_name

def count_collection_stats(collection):
    """Подсчитывает статистику коллекции: материалы, текстуры, треугольники"""
    materials = set()
    textures = set()
    triangles = 0
    
    for obj in collection.objects:
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            if mesh.loop_triangles:
                triangles += len(mesh.loop_triangles)
            elif mesh.polygons:
                triangles += len(mesh.polygons)
            
            for material_slot in obj.material_slots:
                if material_slot.material:
                    materials.add(material_slot.material)
                    
                    material = material_slot.material
                    if material.use_nodes and material.node_tree:
                        for node in material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image:
                                textures.add(node.image)
    
    return len(materials), len(textures), triangles

def update_collection_list(context):
    """Обновляет список коллекций в настройках"""
    settings = context.scene.agr_collection_settings
    settings.collection_items.clear()
    
    for collection in bpy.data.collections:
        if len(collection.objects) > 0:
            item = settings.collection_items.add()
            item.name = collection.name
            item.is_low_poly = is_low_poly_collection(collection.name)
            item.is_light = is_light_collection(collection.name)
            item.enabled = not utills.get_layer_collection_by_name(collection.name).exclude
            item.object_count = len(collection.objects)
            
            material_count, texture_count, triangle_count = count_collection_stats(collection)
            item.material_count = material_count
            item.texture_count = texture_count
            item.triangle_count = triangle_count
    
    print(f"Список коллекций обновлен: {len(settings.collection_items)} элементов")

class AGR_OT_PackToZip(bpy.types.Operator):
    """Упаковать экспортированные коллекции в ZIP архивы"""
    bl_idname = "agr.pack_to_zip"
    bl_label = "AGR: Упаковать в ZIP"
    bl_options = {'REGISTER', 'UNDO'}
    
    # @classmethod
    # def poll(cls, context):
    #     """Проверяем, был ли выполнен экспорт и есть ли экспортированные папки"""
    #     settings = context.scene.agr_collection_settings
    #     return settings.last_export_path != "" and len(settings.exported_folders) > 0
    
    def execute(self, context):
        import os
        import zipfile
        
        settings = context.scene.agr_collection_settings
        source_directory = settings.last_export_path
        
        if not source_directory:
            self.report({'ERROR'}, "Экспорт не выполнен. Сначала выполните экспорт коллекций")
            return {'CANCELLED'}
        
        if not os.path.exists(source_directory):
            self.report({'ERROR'}, f"Папка экспорта не найдена: {source_directory}")
            return {'CANCELLED'}
        
        # source_directory = os_utils._get_project_path()
        if settings.save_old_archives:
            export_dir = os_utils.get_export_dir()
            # subdirectories = [name for name in os.listdir(export_dir) if os.path.isdir(os.path.join(export_dir, name))]
            # if subdirectories:
            #     pass
            dt = datetime.datetime.now()
            day = str(dt.day).rjust(2, "0")
            month = str(dt.month).rjust(2, "0")
            hour = str(dt.hour).rjust(2, "0")
            minute = str(dt.minute).rjust(2, "0")
            sec = str(dt.second).rjust(2, "0")
            subdir_name = f"{dt.year}{month}{day}_{hour}_{minute}_{sec}"
            subdir_path = os.path.join(export_dir, subdir_name)
            os.mkdir(subdir_path)
            print(f"📁 Создана папка для старых архивов: {subdir_path}")

            for exported_folder in settings.exported_folders:
                item_name = exported_folder.folder_name
                item_path = os.path.join(source_directory, item_name)
                
                zip_filename = f"{item_name}.zip"
                zip_old_path = os.path.join(os_utils._get_project_path(), zip_filename)
                zip_new_path = os.path.join(subdir_path, zip_filename)

                shutil.move(zip_old_path, zip_new_path)
                print(f"📁 Архив {zip_filename} перемещен: {zip_new_path}")

            files_size_all = 0
            for root, dirs, files in os.walk(export_dir):
                for file in files:
                    file_size = os.path.getsize(os.path.join(root, file))
                    files_size_all += file_size
            settings.saves_size_info = f"{round(files_size_all / 1048576)} Mb"
        else:
            pass

        # new_directory = os.path.join(source_directory, "new")
        new_directory = source_directory
        if not os.path.exists(new_directory):
            try:
                os.makedirs(new_directory)
                print(f"📁 Создана папка для архивов: {new_directory}")
            except Exception as e:
                self.report({'ERROR'}, f"Не удалось создать папку 'new': {e}")
                return {'CANCELLED'}
        
        print(f"\n📦 Начинаем упаковку коллекций в ZIP архивы")
        print(f"📍 Исходная папка: {source_directory}")
        print(f"📍 Папка для архивов: {new_directory}")
        
        created_archives = 0
        skipped_items = 0
        
        try:
            if not settings.exported_folders:
                self.report({'WARNING'}, "Нет информации об экспортированных папках. Выполните экспорт заново.")
                return {'CANCELLED'}
            
            for exported_folder in settings.exported_folders:
                item_name = exported_folder.folder_name
                item_path = os.path.join(source_directory, item_name)
                
                if not os.path.exists(item_path) or not os.path.isdir(item_path):
                    print(f"⚠️  Папка экспорта не найдена: {item_name}")
                    skipped_items += 1
                    continue
                
                files_in_folder = []
                for root, dirs, files in os.walk(item_path):
                    files_in_folder.extend(files)
                
                if not files_in_folder:
                    print(f"⚠️  Пропускаем пустую папку: {item_name}")
                    skipped_items += 1
                    continue
                
                zip_filename = f"{item_name}.zip"
                zip_path = os.path.join(new_directory, zip_filename)
                
                print(f"\n📦 Создаем архив: {zip_filename}")
                print(f"   📂 Папка-источник: {item_name}")
                print(f"   🎯 Коллекции: {exported_folder.collection_name}")
                print(f"   📄 Файлов в папке: {len(files_in_folder)}")
                
                try:
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, item_path)
                                zipf.write(file_path, arc_path)
                                print(f"     ✅ Добавлен: {arc_path}")
                    
                    created_archives += 1
                    print(f"   💾 Архив создан: {zip_path}")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка создания архива {zip_filename}: {e}")
                    self.report({'WARNING'}, f"Ошибка создания архива {zip_filename}: {e}")
                    continue
        
        except Exception as e:
            self.report({'ERROR'}, f"Общая ошибка при упаковке: {e}")
            return {'CANCELLED'}
        
        # Результат
        message = f"Создано архивов: {created_archives}"
        if skipped_items > 0:
            message += f", пропущено папок: {skipped_items}"
        
        if created_archives > 0:
            self.report({'INFO'}, f"{message}")
            print(f"\n✅ {message}")
            print(f"📁 Архивы сохранены в: {new_directory}")
            
            total_collections = sum(len(folder.collection_name.split(", ")) for folder in settings.exported_folders)
            print(f"📊 Итоговая статистика упаковки:")
            print(f"   📦 ZIP архивов создано: {created_archives}")
            print(f"   🎯 Коллекций упаковано: {total_collections}")
            print(f"   📁 Папок обработано: {len(settings.exported_folders)}")
        else:
            self.report({'WARNING'}, "Не удалось создать ни одного архива")
        
        return {'FINISHED'}

def temporarily_clean_names_in_collection(collection):
    """Временно очищает названия объектов и материалов от суффикса .001 в низкополигональной коллекции"""
    name_mapping = {
        'objects': {},
        'materials': {},
        'displaced_objects': {},
        'displaced_materials': {}
    }
    
    print(f"🔧 Временная очистка названий в коллекции: {collection.name}")
    
    for obj in collection.objects:
        if obj.name.endswith('.001'):
            original_name = obj.name[:-4]
            
            if original_name not in bpy.data.objects:
                old_name = obj.name
                obj.name = original_name
                name_mapping['objects'][old_name] = original_name
                print(f"   📝 Объект: {old_name} -> {original_name}")
            else:
                existing_obj = bpy.data.objects[original_name]
                existing_in_lowpoly = any(is_low_poly_collection(col.name) for col in existing_obj.users_collection)
                
                if not existing_in_lowpoly:
                    import uuid
                    temp_name = f"_TEMP_{uuid.uuid4().hex[:8]}_{original_name}"
                    existing_obj.name = temp_name
                    name_mapping['displaced_objects'][original_name] = temp_name
                    print(f"   🔄 Высокополигональный объект временно переименован: {original_name} -> {temp_name}")
                    
                    old_name = obj.name
                    obj.name = original_name
                    name_mapping['objects'][old_name] = original_name
                    print(f"   📝 Низкополигональный объект: {old_name} -> {original_name}")
        
        if obj.data and hasattr(obj.data, 'materials'):
            for material_slot in obj.material_slots:
                if material_slot.material and material_slot.material.name.endswith('.001'):
                    material = material_slot.material
                    original_name = material.name[:-4]
                    
                    if original_name not in bpy.data.materials:
                        old_name = material.name
                        material.name = original_name
                        name_mapping['materials'][old_name] = original_name
                        print(f"   🎨 Материал: {old_name} -> {original_name}")
                    else:
                        existing_material = bpy.data.materials[original_name]
                        used_in_lowpoly = False
                        
                        for obj_check in bpy.data.objects:
                            if obj_check.data and hasattr(obj_check.data, 'materials'):
                                for slot in obj_check.material_slots:
                                    if slot.material == existing_material:
                                        if any(is_low_poly_collection(col.name) for col in obj_check.users_collection):
                                            used_in_lowpoly = True
                                            break
                                if used_in_lowpoly:
                                    break
                        
                        if not used_in_lowpoly:
                            import uuid
                            temp_name = f"_TEMP_{uuid.uuid4().hex[:8]}_{original_name}"
                            existing_material.name = temp_name
                            name_mapping['displaced_materials'][original_name] = temp_name
                            print(f"   🔄 Высокополигональный материал временно переименован: {original_name} -> {temp_name}")
                            
                            old_name = material.name
                            material.name = original_name
                            name_mapping['materials'][old_name] = original_name
                            print(f"   🎨 Низкополигональный материал: {old_name} -> {original_name}")
    
    cleaned_objects = len(name_mapping['objects'])
    cleaned_materials = len(name_mapping['materials'])
    displaced_objects = len(name_mapping['displaced_objects'])
    displaced_materials = len(name_mapping['displaced_materials'])
    print(f"   ✅ Временно очищено: объектов {cleaned_objects}, материалов {cleaned_materials}")
    print(f"   🔄 Временно перемещено: объектов {displaced_objects}, материалов {displaced_materials}")
    
    return name_mapping

def restore_names_in_collection(collection, name_mapping):
    """Восстанавливает оригинальные названия объектов и материалов в коллекции"""
    print(f"🔄 Восстановление названий в коллекции: {collection.name}")
    
    restored_objects = 0
    restored_materials = 0
    restored_displaced_objects = 0
    restored_displaced_materials = 0
    
    for obj in collection.objects:
        for old_name, new_name in name_mapping['objects'].items():
            if obj.name == new_name:
                obj.name = old_name
                restored_objects += 1
                print(f"   📝 Низкополигональный объект: {new_name} -> {old_name}")
                break
    
    for old_name, new_name in name_mapping['materials'].items():
        if new_name in bpy.data.materials:
            material = bpy.data.materials[new_name]
            material.name = old_name
            restored_materials += 1
            print(f"   🎨 Низкополигональный материал: {new_name} -> {old_name}")
    
    for original_name, temp_name in name_mapping['displaced_objects'].items():
        if temp_name in bpy.data.objects:
            obj = bpy.data.objects[temp_name]
            obj.name = original_name
            restored_displaced_objects += 1
            print(f"   🔄 Высокополигональный объект: {temp_name} -> {original_name}")
    
    for original_name, temp_name in name_mapping['displaced_materials'].items():
        if temp_name in bpy.data.materials:
            material = bpy.data.materials[temp_name]
            material.name = original_name
            restored_displaced_materials += 1
            print(f"   🔄 Высокополигональный материал: {temp_name} -> {original_name}")
    
    print(f"   ✅ Восстановлено низкополигональных: объектов {restored_objects}, материалов {restored_materials}")
    print(f"   🔄 Восстановлено высокополигональных: объектов {restored_displaced_objects}, материалов {restored_displaced_materials}")
    
    return restored_objects + restored_displaced_objects, restored_materials + restored_displaced_materials

class AGR_OT_ExportRun(bpy.types.Operator):
    """Подготовка объектов к экспорту"""
    bl_idname = "agr.export_run"
    bl_label = "AGR: Экспорт"
    bl_description = "Экспортирует активные коллекции в fbx-файлы и собирает необходимые zip-архивы. Заменяет текущие файлы и архивы в корневой папке. При включенной опции 'Сохранять старые архивы' переносит старые архивы в соответствующие папки по дате. Для ВПМ обнуляет координаты и очищает материалы. Для повторной проверки и импорта необходимо запустить проверку."
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        exit_local_view()
        
        original_mode = context.mode
        
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        self.expand_all_collections()
        
        low_poly_collections = get_low_poly_collections()
        
        if low_poly_collections:
            print(f"🔧 Найдено {len(low_poly_collections)} низкополигональных коллекций")
            print(f"📝 Очистка названий будет выполнена перед экспортом каждой коллекции")
        
        self.reset_object_origins(low_poly_collections)
        
        self.apply_rotations()
        
        self.clean_materials(low_poly_collections)
        
        self.purge_unused_data()
        
        self.setup_export_settings()
        
        update_collection_list(context)
        
        # self.report({'INFO'}, "Подготовка к экспорту завершена!")


        bpy.ops.agr.export_collections()

        bpy.ops.agr.pack_to_zip()


        return {'FINISHED'}
    
    def expand_all_collections(self):
        """Раскрывает все коллекции в Outliner"""
        def expand_collection(collection, layer_collection=None):
            collection.hide_select = False
            collection.hide_viewport = False
            if layer_collection:
                layer_collection.hide_viewport = False
                # layer_collection.exclude = False
                for area in bpy.context.screen.areas:
                    if area.type == 'OUTLINER':
                        with bpy.context.temp_override(area=area):
                            for obj in collection.objects:
                                obj.hide_select = False
                                obj.hide_viewport = False
                                obj.hide_set(False)
            
            for child in collection.children:
                child_layer = None
                if layer_collection:
                    for child_layer_coll in layer_collection.children:
                        if child_layer_coll.collection == child:
                            child_layer = child_layer_coll
                            break
                expand_collection(child, child_layer)
        
        expand_collection(bpy.context.scene.collection, bpy.context.view_layer.layer_collection)
        
        print("Все коллекции раскрыты")
    
    def reset_object_origins(self, low_poly_collections):
        """Сбрасывает позиции объектов в 0,0,0 (кроме источников света и низкополигональных моделей)"""
        bpy.ops.object.select_all(action='DESELECT')
        
        low_poly_objects = set()
        for collection in low_poly_collections:
            for obj in collection.objects:
                low_poly_objects.add(obj)
        
        selected_count = 0
        for col in bpy.data.collections:
            layer_col = utills.get_layer_collection_by_name(col.name)
            if layer_col and not layer_col.exclude:
                for obj in col.objects:
                    if obj.type in ['MESH', 'EMPTY'] and obj not in low_poly_objects:
                        obj.select_set(True)
                        selected_count += 1
        # for obj in bpy.context.scene.objects:
        #     if obj.type in ['MESH', 'EMPTY'] and obj not in low_poly_objects:
        #         obj.select_set(True)
        #         selected_count += 1
        
        if bpy.context.selected_objects:
            bpy.ops.object.location_clear(clear_delta=False)
            print(f"Сброшены позиции для {selected_count} объектов (пропущены низкополигональные)")
        
        if low_poly_objects:
            print(f"🔒 Пропущено {len(low_poly_objects)} объектов из низкополигональных коллекций")
    
    def apply_rotations(self):
        """Применяет ротацию всех объектов (кроме источников света)"""
        bpy.ops.object.select_all(action='DESELECT')
        
        for col in bpy.data.collections:
            layer_col = utills.get_layer_collection_by_name(col.name)
            if layer_col and not layer_col.exclude:
                for obj in col.objects:
                    if obj.type != 'LIGHT':
                        obj.select_set(True)
        # for obj in bpy.context.scene.objects:
        #     if obj.type != 'LIGHT':
        #         obj.select_set(True)
        
        if bpy.context.selected_objects:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            print(f"Применена ротация для {len(bpy.context.selected_objects)} объектов")
    
    def clean_materials(self, low_poly_collections):
        """Очищает материалы, оставляя только Principled BSDF и Material Output (кроме низкополигональных)"""
        materials_cleaned = 0
        materials_skipped = 0
        
        low_poly_materials = set()
        for collection in low_poly_collections:
            for obj in collection.objects:
                if obj.data and hasattr(obj.data, 'materials'):
                    for material_slot in obj.material_slots:
                        if material_slot.material:
                            low_poly_materials.add(material_slot.material)
        
        for obj in bpy.data.objects:
            if obj.name.startswith("UCX_"):
                obj.data.materials.clear()

        for material in bpy.data.materials:
            if material in low_poly_materials:
                materials_skipped += 1
                continue
                
            if material.use_nodes and material.node_tree:
                nodes = material.node_tree.nodes
                links = material.node_tree.links
                
                principled_node = None
                output_node = None
                
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principled_node = node
                    elif node.type == 'OUTPUT_MATERIAL':
                        output_node = node
                
                if principled_node and output_node:
                    nodes_to_remove = []
                    for node in nodes:
                        if node != principled_node and node != output_node:
                            nodes_to_remove.append(node)
                    
                    for node in nodes_to_remove:
                        nodes.remove(node)
                    
                    links.clear()
                    if principled_node.outputs.get('BSDF') and output_node.inputs.get('Surface'):
                        links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
                    
                    materials_cleaned += 1
        
        print(f"Очищено материалов: {materials_cleaned}")
        if materials_skipped > 0:
            print(f"🔒 Пропущено материалов из низкополигональных коллекций: {materials_skipped}")
    
    def purge_unused_data(self):
        """Удаляет неиспользуемые данные"""
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        print("Неиспользуемые данные удалены")
    
    def setup_export_settings(self):
        """Подготовка настроек экспорта коллекций"""
        print("\n" + "="*60)
        print("НАСТРОЙКА ЭКСПОРТА КОЛЛЕКЦИЙ")
        print("="*60)
        
        collections_count = len(bpy.data.collections)
        low_poly_collections = get_low_poly_collections()
        high_poly_collections = [col for col in bpy.data.collections if not is_low_poly_collection(col.name)]
        
        print(f"Найдено коллекций: {collections_count}")
        print(f"  🔻 Низкополигональных: {len(low_poly_collections)}")
        print(f"  🔺 Высокополигональных: {len(high_poly_collections)}")
        
        if collections_count == 0:
            print("❌ Коллекции не найдены!")
            return 0
        
        print("\n📋 СПИСОК КОЛЛЕКЦИЙ:")
        for i, collection in enumerate(bpy.data.collections, 1):
            obj_count = len(collection.objects)
            collection_type = "🔻 LOW-POLY" if is_low_poly_collection(collection.name) else "🔺 HIGH-POLY"
            print(f"  {i}. {collection.name} ({obj_count} объектов) [{collection_type}]")
        
        print(f"\n🔍 ИНФОРМАЦИЯ:")
        print(f"- Версия Blender: {bpy.app.version_string}")
        print(f"- Готов к экспорту: ✅ Да")
        print(f"- Низкополигональные коллекции определяются по 4-значному коду в начале имени")
        
        print("\n🚀 ЭКСПОРТ КОЛЛЕКЦИЙ:")
        print("Используйте кнопку 'Экспорт по коллекциям' в панели AGR")
        print("• Высокополигональные коллекции: стандартные настройки")
        print("• Низкополигональные коллекции: специальные настройки + очистка названий")
        
        print("\n📖 НАСТРОЙКИ FBX (ВЫСОКОПОЛИГОНАЛЬНЫЕ):")
        settings = [
            "Scale: 1.0",
            "Apply Unit Scale: ✅",
            "Apply Scale Options: FBX Scale All",
            "Forward Axis: -Z",
            "Up Axis: Y",
            "Object Types: Mesh, Light, Empty",
            "Apply Modifiers: ✅",
            "Smoothing: Face",
            "Triangulate Faces: ✅",
            "Embed Textures: ❌"
        ]
        for setting in settings:
            print(f"  • {setting}")
        
        print("\n📖 НАСТРОЙКИ FBX (НИЗКОПОЛИГОНАЛЬНЫЕ):")
        low_poly_settings = [
            "Scale: 1.0",
            "Apply Unit Scale: ✅",
            "Apply Scale Options: FBX Scale All",
            "Forward Axis: -Z",
            "Up Axis: Y",
            "Object Types: Mesh, Light, Empty",
            "Apply Modifiers: ✅",
            "Smoothing: Face",
            "Triangulate Faces: ✅",
            "Embed Textures: ✅",
            "Path Mode: COPY"
        ]
        for setting in low_poly_settings:
            print(f"  • {setting}")
        
        print("\n" + "="*60)
        print("✅ Настройки экспорта готовы!")
        print("💡 Используйте кнопку 'Экспорт по коллекциям' для автоматического экспорта")
        print("🔧 Низкополигональные модели:")
        print("   • Названия будут временно очищены от .001 перед экспортом")
        print("   • После экспорта названия восстановятся автоматически")
        print("="*60)
        
        return collections_count
    
    def find_layer_collection(self, layer_collection, collection_name):
        """Рекурсивно ищет layer_collection по имени коллекции"""
        if layer_collection.collection.name == collection_name:
            return layer_collection
        for child in layer_collection.children:
            result = self.find_layer_collection(child, collection_name)
            if result:
                return result
        return None

class AGR_OT_ExportCollections(bpy.types.Operator):
    """Экспорт всех коллекций по отдельности"""
    bl_idname = "agr.export_collections"
    bl_label = "AGR: Экспорт по коллекциям"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        exit_local_view()
        
        if os_utils.check_models_path():
            export_directory = os_utils._get_project_path()
        # if self.filepath:
        #     export_directory = os.path.dirname(self.filepath)
        # elif self.directory:
        #     export_directory = self.directory
        else:
            self.report({'ERROR'}, "Укажите папку для экспорта")
            return {'CANCELLED'}
        
        import os
        
        if not os.path.exists(export_directory):
            try:
                os.makedirs(export_directory)
                print(f"📁 Создана папка: {export_directory}")
            except Exception as e:
                self.report({'ERROR'}, f"Не удалось создать папку: {e}")
                return {'CANCELLED'}
        
        print(f"\n🚀 Начинаем экспорт коллекций в папку: {export_directory}")
        
        settings = context.scene.agr_collection_settings
        
        settings.last_export_path = export_directory
        
        settings.exported_folders.clear()
        
        enabled_collections = {}
        
        for item in settings.collection_items:
            if item.enabled:
                enabled_collections[item.name] = True
        
        if len(settings.collection_items) == 0:
            print("⚠️  Список коллекций пуст, экспортируем все коллекции")
            for collection in bpy.data.collections:
                if len(collection.objects) > 0:
                    enabled_collections[collection.name] = True
        
        original_visibility = {}
        for collection in bpy.data.collections:
            original_visibility[collection.name] = collection.hide_viewport
        
        exported_count = 0
        skipped_count = 0
        
        try:
            for collection in bpy.data.collections:
                if len(collection.objects) == 0:
                    print(f"Пропускаем пустую коллекцию: {collection.name}")
                    continue
                
                if collection.name not in enabled_collections:
                    print(f"🚫 Пропускаем отключенную коллекцию: {collection.name}")
                    skipped_count += 1
                    continue
                
                is_low_poly = is_low_poly_collection(collection.name)
                
                for col in bpy.data.collections:
                    col.hide_viewport = True

                collection.hide_viewport = False
                
                import os
                collection_name = collection.name
                if collection_name.lower().endswith('.fbx'):
                    collection_name = collection_name[:-4]
                
                safe_name = "".join(c for c in collection_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                if not safe_name:
                    safe_name = f"collection_{exported_count + 1}"

                if is_low_poly:
                    export_subfolder = get_low_poly_export_folder(collection_name)
                    found_folder = None
                    for folder_name in os.listdir(export_directory):
                        folder_path = os.path.join(export_directory, folder_name)
                        if os.path.isdir(folder_path) and folder_name.startswith(export_subfolder):
                            found_folder = folder_path
                            break
                    if not found_folder:
                        print(f"❌ Папка для экспорта не найдена (начинается с {export_subfolder}): {export_directory}. Коллекция {collection.name} пропущена.")
                        self.report({'WARNING'}, f"Папка для экспорта не найдена (начинается с {export_subfolder}). Коллекция {collection.name} пропущена.")
                        skipped_count += 1
                        continue
                    export_path = found_folder
                else:
                    export_subfolder = get_high_poly_export_folder(collection_name)
                    export_path = os.path.join(export_directory, export_subfolder)
                    if not os.path.exists(export_path):
                        print(f"❌ Папка для экспорта не найдена: {export_path}. Коллекция {collection.name} пропущена.")
                        self.report({'WARNING'}, f"Папка для экспорта не найдена: {export_subfolder}. Коллекция {collection.name} пропущена.")
                        skipped_count += 1
                        continue
                
                filepath = os.path.join(export_path, f"{safe_name}.fbx")
                
                print(f"\n📁 Экспорт коллекции: {collection.name}")
                if is_low_poly:
                    print(f"   🔻 Тип: НИЗКОПОЛИГОНАЛЬНАЯ")
                else:
                    print(f"   🔺 Тип: ВЫСОКОПОЛИГОНАЛЬНАЯ")
                if collection.name != collection_name:
                    print(f"   🔄 Имя очищено от .fbx: {collection_name}")
                print(f"   📄 Итоговый файл: {safe_name}.fbx")
                print(f"   📍 Полный путь: {filepath}")
                print(f"   📂 Папка экспорта: {export_path}")
                print(f"   🔢 Объектов в коллекции: {len(collection.objects)}")
                
                try:
                    if is_low_poly:
                        collection_export_settings = LOW_POLY_SETTINGS.copy()
                        print(f"🔧 Используются настройки низкополигонального экспорта")
                    else:
                        collection_export_settings = FBX_EXPORT_SETTINGS.copy()
                        print(f"🔧 Используются настройки высокополигонального экспорта")
                    
                    collection_export_settings['use_visible'] = True
                    
                    print(f"🔧 Настройки экспорта:")
                    print(f"   • Scale: {collection_export_settings['global_scale']}")
                    print(f"   • Apply Unit Scale: {collection_export_settings['apply_unit_scale']}")
                    print(f"   • Apply Scale Options: {collection_export_settings['apply_scale_options']}")
                    print(f"   • Object Types: {collection_export_settings['object_types']}")
                    print(f"   • Apply Modifiers: {collection_export_settings['use_mesh_modifiers']}")
                    print(f"   • Triangulate: {collection_export_settings['use_triangles']}")
                    print(f"   • Axis Forward: {collection_export_settings['axis_forward']}")
                    print(f"   • Axis Up: {collection_export_settings['axis_up']}")
                    print(f"   • Use Visible: {collection_export_settings['use_visible']}")
                    if is_low_poly:
                        print(f"   • Embed Textures: {collection_export_settings['embed_textures']}")
                        print(f"   • Path Mode: {collection_export_settings['path_mode']}")
                    
                    name_mapping = None
                    if is_low_poly:
                        name_mapping = temporarily_clean_names_in_collection(collection)
                    
                    print(f"🚀 Запуск экспорта FBX...")
                    bpy.ops.export_scene.fbx(
                        filepath=filepath,
                        **collection_export_settings
                    )
                    
                    if is_low_poly and name_mapping:
                        restore_names_in_collection(collection, name_mapping)
                    
                    exported_count += 1
                    print(f"✅ Экспортирована коллекция: {collection.name} -> {safe_name}.fbx")
                    print(f"   💾 Сохранено в: {filepath}")
                    
                    folder_name = os.path.basename(export_path)
                    
                    folder_exists = False
                    for existing_folder in settings.exported_folders:
                        if existing_folder.folder_name == folder_name:
                            folder_exists = True
                            if collection.name not in existing_folder.collection_name:
                                existing_folder.collection_name += f", {collection.name}"
                            break
                    
                    if not folder_exists:
                        exported_folder = settings.exported_folders.add()
                        exported_folder.folder_name = folder_name
                        exported_folder.collection_name = collection.name
                        print(f"   📁 Новая папка сохранена для упаковки: {folder_name}")
                    else:
                        print(f"   📁 Коллекция добавлена в существующую папку: {folder_name}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при экспорте {collection.name}: {e}")
                    self.report({'WARNING'}, f"Ошибка при экспорте {collection.name}: {e}")
                    skipped_count += 1
                    
                    if is_low_poly and 'name_mapping' in locals() and name_mapping:
                        try:
                            restore_names_in_collection(collection, name_mapping)
                        except Exception as restore_error:
                            print(f"❌ Ошибка при восстановлении названий: {restore_error}")
        
        finally:
            for collection in bpy.data.collections:
                if collection.name in original_visibility:
                    collection.hide_viewport = original_visibility[collection.name]
        
        message = f"Экспортировано {exported_count} коллекций в {len(settings.exported_folders)} папок"
        if skipped_count > 0:
            message += f", пропущено {skipped_count}"
        message += f" в {export_directory}"
        
        if exported_count > 0:
            # self.report({'INFO'}, message)
            print(f"\n📊 Итоговая статистика экспорта:")
            print(f"   ✅ Коллекций экспортировано: {exported_count}")
            print(f"   📁 Папок создано/использовано: {len(settings.exported_folders)}")
            print(f"   🎯 Готово к упаковке в ZIP: {len(settings.exported_folders)} папок")
        else:
            self.report({'WARNING'}, "Не удалось экспортировать ни одной коллекции")
        
        return {'FINISHED'}
    
    # def invoke(self, context, event):
    #     import os
    #     if not self.filepath:
    #         blend_filepath = bpy.data.filepath
    #         if blend_filepath:
    #             base_dir = os.path.dirname(blend_filepath)
    #             self.filepath = os.path.join(base_dir, "collections_export.fbx")
    #         else:
    #             desktop = os.path.expanduser("~/Desktop")
    #             self.filepath = os.path.join(desktop, "collections_export.fbx")
        
    #     context.window_manager.fileselect_add(self)
    #     return {'RUNNING_MODAL'}


def register():
    """Регистрация классов и настроек"""
    bpy.utils.register_class(AGR_CollectionItem)
    bpy.utils.register_class(AGR_ExportedFolder)
    bpy.utils.register_class(AGR_CollectionSettings)
    bpy.utils.register_class(AGR_OT_ExportRun)
    bpy.utils.register_class(AGR_OT_ExportCollections)
    # bpy.utils.register_class(AGR_PT_ExportPanel)
    # bpy.utils.register_class(AGR_OT_UpdateCollectionList)
    # bpy.utils.register_class(AGR_OT_EnableAllCollections)
    # bpy.utils.register_class(AGR_OT_DisableAllCollections)
    bpy.utils.register_class(AGR_OT_PackToZip)
    
    bpy.types.Scene.agr_collection_settings = bpy.props.PointerProperty(type=AGR_CollectionSettings)
    
    # bpy.types.VIEW3D_MT_object.append(menu_func_prepare)

def unregister():
    """Отмена регистрации"""
    # bpy.types.VIEW3D_MT_object.remove(menu_func_prepare)
    
    if hasattr(bpy.types.Scene, 'agr_collection_settings'):
        del bpy.types.Scene.agr_collection_settings
    
    # bpy.utils.unregister_class(AGR_PT_ExportPanel)
    bpy.utils.unregister_class(AGR_OT_ExportCollections)
    bpy.utils.unregister_class(AGR_OT_ExportRun)
    # bpy.utils.unregister_class(AGR_OT_UpdateCollectionList)
    # bpy.utils.unregister_class(AGR_OT_EnableAllCollections)
    # bpy.utils.unregister_class(AGR_OT_DisableAllCollections)
    bpy.utils.unregister_class(AGR_OT_PackToZip)
    bpy.utils.unregister_class(AGR_CollectionSettings)
    bpy.utils.unregister_class(AGR_ExportedFolder)
    bpy.utils.unregister_class(AGR_CollectionItem)

FBX_EXPORT_SETTINGS = {
    'use_selection': False,
    'use_visible': False,
    'use_active_collection': False,
    'global_scale': 1.0,
    'apply_unit_scale': True,
    'apply_scale_options': 'FBX_SCALE_ALL',
    'use_space_transform': True,
    'bake_space_transform': False,
    'object_types': {'LIGHT', 'MESH', 'EMPTY'},
    'use_mesh_modifiers': True,
    'use_mesh_modifiers_render': True,
    'mesh_smooth_type': 'FACE',
    'colors_type': 'SRGB',
    'prioritize_active_color': False,
    'use_subsurf': False,
    'use_mesh_edges': False,
    'use_tspace': False,
    'use_triangles': True,
    'use_custom_props': False,
    'add_leaf_bones': False,
    'primary_bone_axis': 'Y',
    'secondary_bone_axis': 'X',
    'use_armature_deform_only': False,
    'armature_nodetype': 'NULL',
    'bake_anim': False,
    'bake_anim_use_all_bones': True,
    'bake_anim_use_nla_strips': True,
    'bake_anim_use_all_actions': True,
    'bake_anim_force_startend_keying': True,
    'bake_anim_step': 1.0,
    'bake_anim_simplify_factor': 1.0,
    'path_mode': 'AUTO',
    'embed_textures': False,
    'batch_mode': 'OFF',
    'use_batch_own_dir': True,
    'axis_forward': '-Z',
    'axis_up': 'Y'
}

# if __name__ == "__main__":
#     register()
