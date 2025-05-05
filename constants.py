dBuildMeshes = True      # Whether to build the meshes or just parse the file
dBuildBones = True       # Whether to build the bones
dBuildFaces = True       # Whether to build the index buffer
dAllowWii = True         # Whether to allow Wii models
# Offset of the first object to process, -1 means just loop through every object
dFirstObjectOffset = -1
# The highest number of models to extract before the user is prompted
dModelThreshold = 50

# Constants for platform identification and byte order
NOE_BIGENDIAN = ">"
NOE_LITTLEENDIAN = "<"
NOESEEK_ABS = 0  # os.SEEK_SET
NOESEEK_REL = 1  # os.SEEK_CUR

# Edge Geometry Skin types
EDGE_GEOM_SKIN_NONE = 0
EDGE_GEOM_SKIN_NO_SCALING = 1
EDGE_GEOM_SKIN_UNIFORM_SCALING = 2
EDGE_GEOM_SKIN_NON_UNIFORM_SCALING = 3
EDGE_GEOM_SKIN_SINGLE_BONE_NO_SCALING = 4
EDGE_GEOM_SKIN_SINGLE_BONE_UNIFORM_SCALING = 5
EDGE_GEOM_SKIN_SINGLE_BONE_NON_UNIFORM_SCALING = 6

# Constants for primitive types
RPGEO_POINTS = 0
RPGEO_TRIANGLE = 3
RPGEO_TRIANGLE_STRIP = 4
RPGEO_TRIANGLE_FAN = 5
RPGEO_TRIANGLE_QUADS = 6

# Vertex maximum magnitude values
vertexMaxMags = [
    1,          # FLOAT1
    1,          # FLOAT2
    1,          # FLOAT3
    1,          # FLOAT4
    1,          # UBYTE4N_COLOR
    1,          # UBYTE4N_COLOR_ARGB
    1,          # UBYTE4N_COLOR_RGBA
    1,          # UNDEFINED_0
    1,          # UBYTE2N_COLOR_5650
    1,          # UBYTE2N_COLOR_5551
    1,          # UBYTE2N_COLOR_4444
    0x7FFFFFFF,  # INT1
    0x7FFFFFFF,  # INT2
    0x7FFFFFFF,  # INT4
    0xFFFFFFFF,  # UINT1
    0xFFFFFFFF,  # UINT2
    0xFFFFFFFF,  # UINT4
    1,          # INT1N
    1,          # INT2N
    1,          # INT4N
    1,          # UINT1N
    1,          # UINT2N
    1,          # UINT4N
    0xFF,       # UBYTE4
    0xFF,       # UBYTE4_X4
    0x7F,       # BYTE4
    1,          # UBYTE4N
    1,          # UNDEFINED_1
    1,          # BYTE4N
    0x3FFF,     # SHORT2
    0x3FFF,     # SHORT4
    0xFFFF,     # USHORT2
    0xFFFF,     # USHORT4
    1,          # SHORT2N
    1,          # SHORT3N
    1,          # SHORT4N
    1,          # USHORT2N
    1,          # USHORT3N
    1,          # USHORT4N
    1,          # UDEC3
    1,          # DEC3N
    1,          # DEC3N_S11_11_10
    1,          # HALF2
    1,          # HALF4
    1,          # UNUSED
    1,          # BYTE3N
    0x7FFF,     # SHORT3
    0xFFFF,     # USHORT3
    0xFF,       # UBYTE4_ENDIAN
    0xFF,       # UBYTE4_COLOR
    0x7F,       # BYTE3
    1,          # UBYTE2N_COLOR_5650_RGB
    1,          # UDEC3_OES
    1,          # DEC3N_OES
    1,          # SHORT4N_EDGE
]
