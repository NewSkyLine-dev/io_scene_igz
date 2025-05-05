"""
Base IGZ file class for handling Skylanders file formats
"""

import struct
from . import constants
from . import utils
from . import formats


class igzFile:
    def __init__(self, data):
        self.inFile = utils.NoeBitStream(data, constants.NOE_BIGENDIAN)
        self.endianness = "BE"
        magic = self.inFile.readUInt()
        if magic == 0x015A4749:
            self.inFile = utils.NoeBitStream(data, constants.NOE_LITTLEENDIAN)
            self.endianness = "LE"

        self.pointers = []
        self.stringList = []
        self.metatypes = []
        self.thumbnails = []
        self.platform = 0
        self.version = 0

        self.models = []
        self.boneIdList = []

        self.is64Bit = None
        self.arkRegisteredTypes = None

    def __del__(self):
        self.arkRegisteredTypes = None
        self.is64Bit = None

    def loadFile(self):
        bs = self.inFile
        bs.seek(0x0, constants.NOESEEK_ABS)

        bs.readUInt()
        self.version = bs.readUInt()
        bs.readUInt()

        if self.version >= 0x07:
            pointerStart = 0x18
            self.platform = bs.readUInt()
            numFixups = bs.readUInt()
        else:
            pointerStart = 0x10
            bs.seek(0x10, constants.NOESEEK_ABS)
            numFixups = -1

        for i in range(0x20):
            bs.seek((i * 0x10) + pointerStart, constants.NOESEEK_ABS)
            pointer = bs.readUInt()
            if pointer == 0x0:
                break
            self.pointers.append(pointer)

        bs.seek(self.pointers[0], constants.NOESEEK_ABS)
        self.processFixupSections(bs, numFixups)
        if constants.dFirstObjectOffset >= 0:
            self.process_igObject(bs, constants.dFirstObjectOffset)
        else:
            if self.version >= 0x09:
                self.process_igObjectList(bs, self.pointers[1])
            else:
                self.process_igObjectList(bs, self.pointers[1] + 4)

    def addModel(self, id):
        shouldAddModel = True
        if len(self.models) > 0:
            for model in self.models:
                if model.id == id:
                    shouldAddModel = False
                    break
        if shouldAddModel == True:
            self.models.append(formats.ModelObject(id))
            print(f"Adding model with id {hex(id)}, model didn't exist")
        else:
            print(f"Adding model with id {hex(id)}, model did exist")
        return shouldAddModel

    def buildMeshes(self):
        """Build Blender meshes from the parsed data"""
        startIndex = 0
        numModels = len(self.models)

        # If there are too many models, ask the user how many to import
        if len(self.models) > constants.dModelThreshold:
            # In Blender, we'll replace this with a proper UI dialog
            startIndex = 0  # Default to starting from the first model
            numModels = min(constants.dModelThreshold, len(
                self.models))  # Limit to threshold by default

        # Process the selected models
        for index in range(numModels):
            print(f"Building model {index+startIndex} of {len(self.models)}")
            if len(self.models[index+startIndex].meshes) > 0:
                self.models[index+startIndex].build(self, index+startIndex)

    def bitAwareSeek(self, bs, baseOffset, offset64, offset32):
        if self.is64Bit(self):
            bs.seek(baseOffset + offset64, constants.NOESEEK_ABS)
        else:
            bs.seek(baseOffset + offset32, constants.NOESEEK_ABS)

    def fixPointer(self, pointer):
        if pointer & 0x80000000 == 0:
            if self.version <= 0x06:
                return self.pointers[(pointer >> 0x18) + 1] + (pointer & 0x00FFFFFF)
            else:
                return self.pointers[(pointer >> 0x1B) + 1] + (pointer & 0x07FFFFFF)
        else:
            return -1

    def readPointer(self, bs):
        if self.is64Bit(self):
            pointer = bs.readUInt64()
        else:
            pointer = bs.readUInt()
        return self.fixPointer(pointer)

    def readMemoryRef(self, bs):
        size = bs.readUInt() & 0x00FFFFFF
        if self.is64Bit(self):
            bs.seek(0x04, constants.NOESEEK_REL)
        pointer = self.readPointer(bs)
        if pointer == self.pointers[1]:
            return (0, 0, [])
        bs.seek(pointer, constants.NOESEEK_ABS)
        memory = bs.readBytes(size)
        return (size, pointer, memory)

    def readMemoryRefHandle(self, bs):
        if self.is64Bit(self):
            index = bs.readUInt64()
        else:
            index = bs.readUInt()
        return self.thumbnails[index]

    def readVector(self, bs):
        if self.is64Bit(self) and self.version >= 0x09:
            count = bs.readUInt64()
            size = bs.readUInt64()
        else:
            count = bs.readUInt()
            size = bs.readUInt()
        pointer = self.readPointer(bs)
        return (count, size & 0x00FFFFFF, pointer)

    def readObjectVector(self, bs):
        vector = self.readVector(bs)
        offset = bs.tell()
        objects = []
        sizeofPointer = 8 if self.is64Bit(self) else 4
        for i in range(vector[0]):
            bs.seek(vector[2] + sizeofPointer * i, constants.NOESEEK_ABS)
            objects.append(self.readPointer(bs))
        return objects

    def readIntVector(self, bs):
        vector = self.readVector(bs)
        ints = []
        for i in range(vector[0]):
            bs.seek(vector[2] + 4 * i, constants.NOESEEK_ABS)
            ints.append(bs.readInt())
        return ints

    def readVector3(self, bs):
        return (bs.readFloat(), bs.readFloat(), bs.readFloat())

    def readString(self, bs):
        if self.is64Bit(self):
            raw = bs.readUInt64()
        else:
            raw = bs.readUInt()

        if raw >= len(self.stringList):
            bs.seek(self.fixPointer(raw), constants.NOESEEK_ABS)
            return bs.readString()
        else:
            return self.stringList[raw]

    # ☑️
    def processFixupSections(self, bs, numFixups):
        start = bs.tell()
        if self.version <= 0x06:
            bs.seek(self.pointers[0] + 0x08, constants.NOESEEK_ABS)
            self.platform = bs.readUShort()
            bs.seek(self.pointers[0] + 0x10, constants.NOESEEK_ABS)
            numFixups = bs.readUInt()
            start += 0x1C
        for i in range(numFixups):
            bs.seek(start, constants.NOESEEK_ABS)
            magic = bs.readUInt()
            if self.version <= 0x06:
                bs.seek(0x08, constants.NOESEEK_REL)
            count = bs.readUInt()
            length = bs.readUInt()
            dataStart = bs.readUInt()
            bs.seek(start + dataStart, constants.NOESEEK_ABS)

            if magic == 0x52545354 or magic == 1:
                for j in range(count):
                    self.stringList.append(bs.readString())
                    if self.version > 0x07 and bs.tell() % 2 != 0:
                        bs.seek(1, constants.NOESEEK_REL)
            if magic == 0x54454D54 or magic == 0:
                for j in range(count):
                    self.metatypes.append(bs.readString())
                    if self.version > 0x07 and bs.tell() % 2 != 0:
                        bs.seek(1, constants.NOESEEK_REL)
            if magic == 0x4E484D54 or magic == 10:
                for j in range(count):
                    tmhnSize = bs.readUInt() & 0x00FFFFFF
                    if self.is64Bit(self):
                        bs.seek(0x04, constants.NOESEEK_REL)
                    tmhnOffset = self.readPointer(bs)
                    offset = bs.tell()
                    bs.seek(tmhnOffset, constants.NOESEEK_ABS)
                    memory = bs.readBytes(tmhnSize)
                    bs.seek(offset, constants.NOESEEK_ABS)
                    self.thumbnails.append((tmhnSize, tmhnOffset, memory))

            start += length

    def process_igObject(self, bs, pointer):
        if pointer <= self.pointers[1]:
            return None
        bs.seek(pointer, constants.NOESEEK_ABS)
        if self.is64Bit(self):
            typeIndex = bs.readUInt64()
        else:
            typeIndex = bs.readUInt()

        try:
            metatype = self.metatypes[typeIndex]
        except:
            return None

        if metatype in self.arkRegisteredTypes:
            return self.arkRegisteredTypes[metatype](self, bs, pointer)
        else:
            return None

    # ☑️
    def process_igDataList(self, bs, offset):
        self.bitAwareSeek(bs, offset, 0x0C, 0x08)
        _count = bs.readUInt()
        _capacity = bs.readUInt()
        self.bitAwareSeek(bs, offset, 0x18, 0x10)
        _data = self.readMemoryRef(bs)
        return (_count, _capacity, _data)

    def process_igNamedObject(self, bs, offset):
        self.bitAwareSeek(bs, offset, 0x10, 0x08)
        return self.readString(bs)

    # ☑️
    def process_igObjectList(self, bs, offset):
        dataList = self.process_igDataList(bs, offset)
        pointerSize = 4
        if self.is64Bit(self):
            pointerSize = 8
        returns = []
        for i in range(dataList[0]):
            bs.seek(dataList[2][1] + i * pointerSize, constants.NOESEEK_ABS)
            returns.append(self.process_igObject(bs, self.readPointer(bs)))
        return returns

    def process_igIntList(self, bs, offset):
        dataList = self.process_igDataList(bs, offset)
        sizeofSize = 4
        returns = []
        for i in range(dataList[0]):
            bs.seek(dataList[2][1] + i * sizeofSize, constants.NOESEEK_ABS)
            returns.append(bs.readInt())
        return returns
