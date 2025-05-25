import bpy
from bpy.props import (
    StringProperty,
    BoolProperty
)
from bpy_extras.io_utils import ImportHelper
from . import constants
from . import utils
from . import game_formats
from typing import Any
import os
import importlib
from .operators.file_operator import menu_func_import

ADDON_PATH = os.path.direname(__file__)
ARCHIVE_EXTENSIONS = ('.iga', '.igz', '.arc', '.bld', '.pak', '.lang')
DEFAULT_WINDOW_WIDTH = 600
MAX_TREE_DEPTH = 20

if "bpy" in locals():
    ...


class ImportSkylandersIGZ(bpy.types.Operator, ImportHelper):
    """Import Skylanders IGZ/BLD models"""
    bl_idname = "import_mesh.skylanders_igz"
    bl_label = "Import Skylanders IGZ/BLD"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext: str = ".igz;.bld"
    filter_glob: StringProperty = StringProperty(
        default="*.igz;*.bld", options={'HIDDEN'})

    build_meshes: BoolProperty = BoolProperty(
        name="Build Meshes",
        description="Whether to build the meshes or just parse the file",
        default=True,
    )

    build_bones: BoolProperty = BoolProperty(
        name="Build Bones",
        description="Whether to build the bones",
        default=True,
    )

    build_faces: BoolProperty = BoolProperty(
        name="Build Faces",
        description="Whether to build the faces",
        default=True,
    )

    allow_wii: BoolProperty = BoolProperty(
        name="Allow Wii Models",
        description="Whether to allow Wii models (may be buggy)",
        default=True,
    )

    def execute(self, context: Any) -> set:
        # Set global variables from UI options
        constants.dBuildMeshes = self.build_meshes
        constants.dBuildBones = self.build_bones
        constants.dBuildFaces = self.build_faces
        constants.dAllowWii = self.allow_wii

        # Load and process the file
        try:
            with open(self.filepath, 'rb') as file:
                data = file.read()

                # Check file validity
                bs = utils.NoeBitStream(data)
                magic = bs.readUInt()
                if magic != 0x015A4749 and magic != 0x49475A01:
                    self.report({'ERROR'}, "Invalid IGZ file format")
                    return {'CANCELLED'}

                # Reset stream and determine version
                bs = utils.NoeBitStream(data, constants.Endianness.BIG)
                magic = bs.readUInt()
                if magic == 0x015A4749:
                    bs = utils.NoeBitStream(
                        data, constants.Endianness.LITTLE)
                    bs.readUInt()

                version = bs.readUInt()

                # Initialize appropriate parser based on version
                if version == 0x05:
                    parser = game_formats.ssaIgzFile(data)
                elif version == 0x06:
                    parser = game_formats.sgIgzFile(data)
                elif version == 0x07:
                    parser = game_formats.ssfIgzFile(data)
                elif version == 0x08:
                    parser = game_formats.sttIgzFile(data)
                elif version == 0x09:
                    parser = game_formats.sscIgzFile(data)
                elif version == 0x0A:
                    parser = game_formats.nstIgzFile(data)
                else:
                    self.report(
                        {'ERROR'}, f"Version {hex(version)} is unsupported.")
                    return {'CANCELLED'}

                # Load the file and build meshes
                parser.loadFile()

                if parser.version < 0x0A and parser.platform == 2 and not constants.dAllowWii:
                    self.report(
                        {'ERROR'}, "Wii Models are not allowed as they are buggy. Enable 'Allow Wii Models' in import options to try anyway.")
                    return {'CANCELLED'}

                if constants.dBuildMeshes:
                    parser.buildMeshes()

                self.report(
                    {'INFO'}, f"Successfully imported {len(parser.models)} models")

                return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


classes = ()
# ------------------------------------------------------------------------------
# Register/Unregister functionality
# ------------------------------------------------------------------------------


def menu_func_import(self, context):
    self.layout.operator(ImportSkylandersIGZ.bl_idname,
                         text="Skylanders IGZ/BLD (.igz/.bld)")


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register class {cls.__name__}: {e}")

    register_properties()

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    unregister_properties()

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Failed to unregister class {cls.__name__}: {e}")
