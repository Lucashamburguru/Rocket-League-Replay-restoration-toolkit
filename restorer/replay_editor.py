import struct
import os

class ReplayEditor:
    def __init__(self):
        self.data = None
        self.header_size = 0
        self._unreal_table = self._make_unreal_table()

    def _make_unreal_table(self):
        poly = 0x04C11DB7
        table = [0] * 256
        for i in range(256):
            crc = i << 24
            for _ in range(8):
                if crc & 0x80000000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
            val = crc & 0xFFFFFFFF
            swapped = struct.unpack('<I', struct.pack('>I', val))[0]
            table[i] = swapped
        return table

    def calculate_ue3_crc(self, data):
        crc = 0xFE0D3410
        for byte in data:
            crc = (crc >> 8) ^ self._unreal_table[(byte ^ (crc & 0xFF)) & 0xFF]
        final_crc = (~crc) & 0xFFFFFFFF
        return struct.unpack('<I', struct.pack('>I', final_crc))[0]

    def load(self, path):
        with open(path, 'rb') as f:
            self.data = bytearray(f.read())
        self.header_size = struct.unpack('<I', self.data[0:4])[0]
        return True

    def find_property(self, name):
        # Rocket League strings in header are [length][string\0]
        token = struct.pack('<I', len(name) + 1) + name.encode('ascii') + b'\x00'
        pos = self.data.find(token)
        if pos == -1:
            return -1
        return pos

    def update_int_property(self, name, new_value, occurrence=1):
        pos = self.find_property(name)
        if pos == -1: return False
        
        # Structure: [Name][StrProperty][Size][0][Value]
        # IntProperty value starts 8 bytes after "IntProperty\0"
        type_pos = self.data.find(b"IntProperty\x00", pos)
        if type_pos == -1: return False
        
        value_pos = type_pos + 12 + 8 # "IntProperty\0" (12) + metadata (8)
        struct.pack_into('<I', self.data, value_pos, new_value)
        return True
