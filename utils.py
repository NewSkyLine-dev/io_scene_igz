"""
Utility classes and functions for the Skylanders importer
"""

import struct
from . import constants


class NoeBitStream:
    """
    Reimplementation of Noesis's stream functionality for reading binary data
    """

    def __init__(self, data, endian=constants.NOE_LITTLEENDIAN):
        self.data = data
        self.endian = endian
        self.offset = 0

    def seek(self, offset, whence=constants.NOESEEK_ABS):
        if whence == constants.NOESEEK_ABS:
            self.offset = offset
        elif whence == constants.NOESEEK_REL:
            self.offset += offset
        return self.offset

    def tell(self):
        return self.offset

    def readBytes(self, size):
        bytes_data = self.data[self.offset:self.offset + size]
        self.offset += size
        return bytes_data

    def readUInt(self):
        val = struct.unpack(self.endian + 'I',
                            self.data[self.offset:self.offset + 4])[0]
        self.offset += 4
        return val

    def readUInt64(self):
        val = struct.unpack(self.endian + 'Q',
                            self.data[self.offset:self.offset + 8])[0]
        self.offset += 8
        return val

    def readInt(self):
        val = struct.unpack(self.endian + 'i',
                            self.data[self.offset:self.offset + 4])[0]
        self.offset += 4
        return val

    def readUShort(self):
        val = struct.unpack(self.endian + 'H',
                            self.data[self.offset:self.offset + 2])[0]
        self.offset += 2
        return val

    def readUByte(self):
        val = self.data[self.offset]
        self.offset += 1
        return val

    def readString(self):
        start = self.offset
        while self.data[self.offset] != 0:
            self.offset += 1
        return self.data[start:self.offset].decode('utf-8')

    def readHalfFloat(self):
        """Convert half precision (16-bit) float to regular float"""
        half = struct.unpack(
            self.endian + 'H', self.data[self.offset:self.offset + 2])[0]
        self.offset += 2

        # Extract sign, exponent, and mantissa
        sign = (half >> 15) & 0x1
        exponent = (half >> 10) & 0x1F
        mantissa = half & 0x3FF

        # Handle special cases
        if exponent == 0:
            if mantissa == 0:
                return -0.0 if sign else 0.0
            else:
                # Denormalized number
                return ((-1) ** sign) * (mantissa / 1024.0) * (2 ** -14)
        elif exponent == 31:
            if mantissa == 0:
                return float('-inf') if sign else float('inf')
            else:
                return float('nan')

        # Normalized number
        return ((-1) ** sign) * (1 + mantissa / 1024.0) * (2 ** (exponent - 15))


def decompressEdgeIndices(indexBuffer, indexCount):
    """
    Simplified placeholder for the edge index decompression
    In a full implementation, this would properly handle the triangle strips format
    """
    # This is a very basic implementation, just returning transformed indices
    # A proper implementation would need to follow the original algorithm
    result = bytearray(indexCount * 2)

    for i in range(indexCount):
        # Placeholder - in real implementation we would properly decompress
        idx = i % 256
        result[i*2] = idx
        result[i*2+1] = 0

    return bytes(result)


class Bone:
    """Helper class for bone data"""

    def __init__(self, index, name, parentIndex, translation):
        self.index = index
        self.name = name if name else f"bone_{index}"
        self.parentIndex = parentIndex
        self.position = translation
        self.matrix = None
        self.children = []

    def setMatrix(self, matrix_data, endian):
        """Parse matrix data from the file to create a bone matrix"""
        from mathutils import Matrix

        # Create a 4x4 matrix from the raw data
        mtx = []
        for i in range(0, 64, 4):
            value = struct.unpack(endian + 'f', matrix_data[i:i+4])[0]
            mtx.append(value)

        # Convert to Blender format
        # This would need to be tested and adjusted for proper orientation
        self.matrix = Matrix((
            (mtx[0], mtx[4], mtx[8], mtx[12]),
            (mtx[1], mtx[5], mtx[9], mtx[13]),
            (mtx[2], mtx[6], mtx[10], mtx[14]),
            (mtx[3], mtx[7], mtx[11], mtx[15])
        ))

        # Inverse the matrix as needed
        self.matrix.invert()

    def getPosition(self):
        """Get the bone position, either from translation or matrix"""
        if self.matrix:
            # Extract position from matrix
            return (self.matrix[0][3], self.matrix[1][3], self.matrix[2][3])
        else:
            # Use the translation directly
            return self.position
