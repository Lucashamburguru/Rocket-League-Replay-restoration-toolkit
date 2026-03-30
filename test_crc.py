import struct
import zlib
import sys

def test_crc(path):
    with open(path, 'rb') as f:
        data = f.read()
        if len(data) < 8: return "File too small"
        
        header_size = struct.unpack('<I', data[0:4])[0]
        file_crc = struct.unpack('<I', data[4:8])[0]
        
        # Rocket League CRC is over the header data ONLY
        # The header data starts at offset 8 and has length 'header_size'
        header_data = data[8:8+header_size]
        
        # Calculate CRC
        # Note: Psyonix uses a custom CRC implementation in Unreal Engine 3
        # It is NOT standard zlib.crc32. It is based on a table-driven CRC32.
        # Let's see if zlib matches.
        calc_crc = zlib.crc32(header_data)
        
        return {
            'header_size': header_size,
            'file_crc': f"{file_crc:08X}",
            'zlib_crc': f"{calc_crc:08X}"
        }

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(f"{arg}: {test_crc(arg)}")
