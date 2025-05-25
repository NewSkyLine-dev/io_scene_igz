import bpy
import bpy_extras


class IMPORT_OT_archive_file(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import an Alchemy Archive file (.pak, .iga, .igz, .arc, .bld)"""
    bl_idname = "import_scene.alchemy_archive"
    bl_label = "Import Alchemy Archive"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".pak;.iga;.igz;.arc;.bld"
    filter_glob: bpy.props.StringProperty(
        default="*.pak;*.iga;*.igz;*.arc;*.bld",
        options={'HIDDEN'},
    )
    iga_file_version: bpy.props.EnumProperty(
        name="IGA File Version",
        description="Select the IGA file version",
        items=[
            ("SKYLANDERS_IMAGINATORS_PS4", "Skylanders Imaginators PS4", ""),
        ],
        default="SKYLANDERS_IMAGINATORS_PS4",
    )

    def execute(self, context):
        filepath = self.filepath
        scene = context.scene

        scene.imported_file_path = filepath
        scene.selected_file_path = filepath

        scene.file_tree_nodes.clear()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "filepath")

        box = layout.box()
        box.label(text="Import Settings:", icon="PREFERENCES")

        box.prop(self, "iga_file_version", text="IGA File Version")
        box.prop(self, "build_meshes", text="Build Meshes")
        box.prop(self, "build_bones", text="Build Bones")
        box.prop(self, "build_faces", text="Build Faces")
        box.prop(self, "allow_wii", text="Allow Wii Models")


def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_archive_file.bl_idname,
                         text="Alchemy Archive (.pak, .iga, .igz, .arc, .bld)")
