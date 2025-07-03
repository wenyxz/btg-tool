bl_info = {
    "name": "Blender To Godot Tool",
    "author": "wenyxz",
    "version": (1, 0),
    "blender": (4, 4, 3),
    "location": "Properties > Object / Sidebar > Godot",
    "description": "Helps prepare Blender objects for export to Godot",
    "category": "Object",
}

import bpy
import os

# Custom icon preview collection
from bpy.utils import previews
custom_icons = None

# Extended Godot types
godot_items = [
    ('NONE', "None", "", 'X', 0),
    ('NOIMP', "No Import", "", 'CANCEL', 1),
    ('COL', "Collision", "", 'MOD_PHYSICS', 2),
    ('COLONLY', "Collision Only", "", 'MOD_SIMPLIFY', 3),
    ('CONVCOL', "Convex Collision", "", 'MESH_DATA', 4),
    ('CONVCOLONLY', "Convex Only", "", 'MESH_CIRCLE', 5),
    ('OCC', "Occluder", "", 'RESTRICT_VIEW_OFF', 6),
    ('OCCONLY', "Occluder Only", "", 'HIDE_ON', 7),
    ('NAVMESH', "Navigation Mesh", "", 'OUTLINER_OB_MESH', 8),
    ('VEHICLE', "Vehicle", "", 'AUTO', 9),
    ('WHEEL', "Wheel", "", 'MOD_WAVE', 10),
    ('RIGID', "Rigid Body", "", 'PHYSICS', 11),
]

def register_properties():
    bpy.types.Object.godot_type = bpy.props.EnumProperty(
        name="Godot Type",
        items=godot_items,
        default='NONE',
        update=update_object_name
    )

def unregister_properties():
    del bpy.types.Object.godot_type

def update_object_name(self, context):
    suffix_map = {
        "NOIMP": "-noimp",
        "COL": "-col",
        "COLONLY": "-colonly",
        "CONVCOL": "-convcol",
        "CONVCOLONLY": "-convcolonly",
        "OCC": "-occ",
        "OCCONLY": "-occonly",
        "NAVMESH": "-navmesh",
        "VEHICLE": "-vehicle",
        "WHEEL": "-wheel",
        "RIGID": "-rigid",
        "NONE": ""
    }

    suffix = suffix_map.get(self.godot_type, "")
    base_name = self.name.split("-")[0]
    self.name = base_name + suffix if suffix else base_name

# Object properties panel
class OBJECT_PT_godot_export(bpy.types.Panel):
    bl_label = "Godot Export Settings"
    bl_idname = "OBJECT_PT_godot_export"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            layout.prop(obj, "godot_type", text="Godot Type")

# Sidebar panel
class VIEW3D_PT_godot_tools(bpy.types.Panel):
    bl_label = "BTG"
    bl_idname = "VIEW3D_PT_godot_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Godot"

    def draw(self, context):
        layout = self.layout

        sections = {
            "General": [
                ("NONE", "None", "CUBE"),
                ("NOIMP", "No Import", "CUBE"),
            ],
            "Collisions": [
                ("COL", "Collision", "MESH_CUBE"),
                ("COLONLY", "Only Collision", "MESH_CUBE"),
                ("CONVCOL", "Convex Collision", "MESH_ICOSPHERE"),
                ("CONVCOLONLY", "Convex Only", "MESH_ICOSPHERE"),
            ],
            "Occlusion": [
                ("OCC", "Occlusion", "MOD_BOOLEAN"),
                ("OCCONLY", "Only Occluder", "MOD_BOOLEAN"),
            ],
            "Other": [
                ("NAVMESH", "Navigation Mesh", "OUTLINER_OB_LIGHT"),
                ("VEHICLE", "Vehicle", "OUTLINER_OB_ARMATURE"),
                ("WHEEL", "Wheel", "OUTLINER_OB_EMPTY"),
                ("RIGID", "Rigid Body", "PHYSICS"),
            ],
        }

        for section_name, items in sections.items():
            layout.label(text=section_name + ":")

            # Use vertical stack for General and Other
            if section_name in {"General", "Other"}:
                for identifier, label, fallback_icon in items:
                    icon_id = f"godot_icon_{identifier.lower()}"
                    if custom_icons and icon_id in custom_icons:
                        icon_val = custom_icons[icon_id].icon_id
                        layout.operator("godot.set_type", text=label, icon_value=icon_val).godot_type = identifier
                    else:
                        layout.operator("godot.set_type", text=label, icon=fallback_icon).godot_type = identifier
            else:
                # Use two-per-row layout for Collisions and Occlusion
                col = layout.column()
                for i in range(0, len(items), 2):
                    row = col.row(align=True)
                    for identifier, label, fallback_icon in items[i:i+2]:
                        icon_id = f"godot_icon_{identifier.lower()}"
                        if custom_icons and icon_id in custom_icons:
                            icon_val = custom_icons[icon_id].icon_id
                            row.operator("godot.set_type", text=label, icon_value=icon_val).godot_type = identifier
                        else:
                            row.operator("godot.set_type", text=label, icon=fallback_icon).godot_type = identifier
                            
class VIEW3D_PT_help(bpy.types.Panel):
    bl_label = "Help"
    bl_idname = "VIEW3D_PT_help"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Godot"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        layout.operator("wm.url_open", text="Godot Doc", icon="URL").url = "https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/node_type_customization.html"

# Operator to set type and rename
class GODOT_OT_set_type(bpy.types.Operator):
    bl_idname = "godot.set_type"
    bl_label = "Set Godot Type"

    godot_type: bpy.props.StringProperty()

    def execute(self, context):
        for obj in context.selected_objects:
            obj.godot_type = self.godot_type
        return {'FINISHED'}

classes = (
    OBJECT_PT_godot_export,
    VIEW3D_PT_godot_tools,
    VIEW3D_PT_help,
    GODOT_OT_set_type,
)

def register_icons():
    global custom_icons
    custom_icons = previews.new()

    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    if os.path.isdir(icons_dir):
        for identifier, _, _, _, _ in godot_items:
            icon_id = f"godot_icon_{identifier.lower()}"
            filename = f"{identifier.lower()}.png"
            path = os.path.join(icons_dir, filename)
            if os.path.isfile(path):
                custom_icons.load(icon_id, path, 'IMAGE')

def unregister_icons():
    global custom_icons
    if custom_icons:
        previews.remove(custom_icons)
        custom_icons = None

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()
    register_icons()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()
    unregister_icons()

if __name__ == "__main__":
    register()