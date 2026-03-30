import struct
import zlib

def get_crc_info(path):
    with open(path, 'rb') as f:
        data = f.read()
    sz = struct.unpack('<I', data[0:4])[0]
    fcrc = struct.unpack('<I', data[4:8])[0]
    hdata = data[8:8+sz]
    z = zlib.crc32(hdata) & 0xFFFFFFFF
    return fcrc, z, len(hdata)

def test():
    files = ['36BE614746BB61DC8DE974AD7046ECA8.replay', '9C1A576740406EE9EBB6FCABD115A440.replay']
    for p in files:
        if not os.path.exists(p): continue
        fcrc, z, l = get_crc_info(p)
        print(f"File: {p}")
        print(f"  Target CRC: {fcrc:08X}")
        print(f"  Zlib (Ref): {z:08X}")
        print(f"  Zlib XOR:   {(z ^ 0xFFFFFFFF) & 0xFFFFFFFF:08X}")

if __name__ == "__main__":
    import os
    test()
