import struct
import os

def check_header(path):
    try:
        with open(path, 'rb') as f:
            f.read(8) # header_len, crc
            engine = struct.unpack('<I', f.read(4))[0]
            licensee = struct.unpack('<I', f.read(4))[0]
            net = struct.unpack('<I', f.read(4))[0]
            return engine, licensee, net
    except Exception as e:
        return str(e)

old_file = '0308A3E64A7FE845257EDF8F71C0A323.replay'
new_file = '36BE614746BB61DC8DE974AD7046ECA8.replay'

print(f"Old ({old_file}): {check_header(old_file)}")
print(f"New ({new_file}): {check_header(new_file)}")
