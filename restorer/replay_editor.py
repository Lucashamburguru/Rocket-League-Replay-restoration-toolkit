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

    def find_property(self, name, occurrence=1):
        # Rocket League strings in header are [length][string\0]
        token = struct.pack('<I', len(name) + 1) + name.encode('ascii') + b'\x00'
        pos = -1
        for _ in range(occurrence):
            pos = self.data.find(token, pos + 1)
            if pos == -1:
                return -1
        return pos

    def update_int_property(self, name, new_value, occurrence=1):
        pos = self.find_property(name, occurrence)
        if pos == -1: return False
        
        # Structure: [Name][StrProperty][Size][0][Value]
        # IntProperty value starts 8 bytes after "IntProperty\0"
        type_pos = self.data.find(b"IntProperty\x00", pos)
        if type_pos == -1: return False
        
        value_pos = type_pos + 12 + 8 # "IntProperty\0" (12) + metadata (8)
        struct.pack_into('<I', self.data, value_pos, new_value)
        return True

    def update_str_property(self, name, new_str, occurrence=1):
        pos = self.find_property(name, occurrence)
        if pos == -1: return False
        
        type_pos = self.data.find(b"StrProperty\x00", pos)
        if type_pos == -1: return False
        
        # Meta positions
        prop_size_pos = type_pos + 12
        str_len_pos = prop_size_pos + 8
        old_str_pos = str_len_pos + 4
        
        old_str_len = struct.unpack('<I', self.data[str_len_pos:str_len_pos+4])[0]
        new_str_bytes = new_str.encode('utf-8') + b'\x00'
        new_str_len = len(new_str_bytes)
        
        # Update PropertySize (String + 4 bytes for length field)
        struct.pack_into('<I', self.data, prop_size_pos, new_str_len + 4)
        # Update StringLength
        struct.pack_into('<I', self.data, str_len_pos, new_str_len)
        
        # Perform the Shift
        diff = new_str_len - old_str_len
        if diff != 0:
            tail = self.data[old_str_pos + old_str_len:]
            self.data = self.data[:old_str_pos] + new_str_bytes + tail
            # Update Global Header Size
            self.header_size += diff
            struct.pack_into('<I', self.data, 0, self.header_size)
        else:
            self.data[old_str_pos : old_str_pos + new_str_len] = new_str_bytes
            
        return True

    def save(self, path):
        # 1. Recalculate Header CRC (offset 4)
        # Header data starts at offset 8
        h_data = self.data[8:8+self.header_size]
        h_crc = self.calculate_ue3_crc(h_data)
        struct.pack_into('<I', self.data, 4, h_crc)
        
        # 2. Recalculate Body CRC
        # Body starts after header [Size][CRC][Data]
        body_prefix_pos = 8 + self.header_size
        body_size = struct.unpack('<I', self.data[body_prefix_pos:body_prefix_pos+4])[0]
        body_data = self.data[body_prefix_pos+8 : body_prefix_pos+8+body_size]
        body_crc = self.calculate_ue3_crc(body_data)
        struct.pack_into('<I', self.data, body_prefix_pos+4, body_crc)
        
        with open(path, 'wb') as f:
            f.write(self.data)
