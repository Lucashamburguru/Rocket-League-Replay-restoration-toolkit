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
