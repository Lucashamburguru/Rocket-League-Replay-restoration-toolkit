import struct
import os
import sys

# Exact Rocket League/UE3 CRC32 Algorithm
def make_unreal_table():
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

UNREAL_TABLE = make_unreal_table()

def calculate_ue3_crc(data):
    crc = 0xFE0D3410
    for byte in data:
        crc = (crc >> 8) ^ UNREAL_TABLE[(byte ^ (crc & 0xFF)) & 0xFF]
    final_crc = (~crc) & 0xFFFFFFFF
    final_swapped = struct.unpack('<I', struct.pack('>I', final_crc))[0]
    return final_swapped

def surgical_patch_v3(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        # 1. Header Section (Bytes 0-8 control the header)
        h_sz = struct.unpack('<I', data[0:4])[0]
        h_data = data[8:8+h_sz]
        
        # Patch NetVersion in Header
        # Usually offset 16 in the WHOLE file is the NetVersion
        # (4 bytes SZ + 4 bytes CRC + 4 bytes Major + 4 bytes Minor + 4 bytes Net)
        struct.pack_into('<I', data, 16, 11)
        # Re-calc Header CRC
        h_data_patched = data[8:8+h_sz]
        h_crc = calculate_ue3_crc(h_data_patched)
        struct.pack_into('<I', data, 4, h_crc)

        # 2. Body Section (Immediately follows header)
        body_prefix_pos = 8 + h_sz
        body_size = struct.unpack('<I', data[body_prefix_pos:body_prefix_pos+4])[0]
        body_data = data[body_prefix_pos+8 : body_prefix_pos+8+body_size]
        
        # 3. Find the Ball in the Body (it's in the Object Table at the end)
        old_name = b'Archetypes.Ball.Ball_BasketBall\x00'
        new_name = b'Archetypes.Ball.ball_luminousairplane\x00'
        old_token = struct.pack('<i', len(old_name)) + old_name
        new_token = struct.pack('<i', len(new_name)) + new_name
        
        pos_in_body = body_data.find(old_token)
        if pos_in_body == -1:
            return False, f"Ball name not found in Body (offset {body_prefix_pos})"

        # 4. Inject and Shift Body
        new_body_data = body_data[:pos_in_body] + new_token + body_data[pos_in_body+len(old_token):]
        diff = len(new_token) - len(old_token)
        
        # 5. Finalize Body
        new_body_size = len(new_body_data)
        new_body_crc = calculate_ue3_crc(new_body_data)
        
        # 6. Rebuild File
        final_data = bytearray()
        # Header (Size, CRC, Data)
        final_data += data[0:8+h_sz]
        # Body Prefix (Size, CRC)
        final_data += struct.pack('<I', new_body_size)
        final_data += struct.pack('<I', new_body_crc)
        # Body Data
        final_data += new_body_data
        
        # Append anything trailing (Footer)
        trailing_start = body_prefix_pos + 8 + body_size
        final_data += data[trailing_start:]

        with open(output_path, 'wb') as f:
            f.write(final_data)

        return True, f"Final Surgery Success! Body shifted by {diff} bytes. CRC: {new_body_crc:08X}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 surgical_patch_v3.py <replay_file>")
        sys.exit(1)

    path = sys.argv[1]
    output = "surgical_v3_test.replay"
    success, msg = surgical_patch_v3(path, output)
    print(f"Result: {msg}")
