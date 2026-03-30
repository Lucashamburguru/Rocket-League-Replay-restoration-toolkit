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

def surgical_patch_v2(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        # 1. Header Analysis
        old_h_sz = struct.unpack('<I', data[0:4])[0]
        header_data = data[8:8+old_h_sz]
        
        # Binary find the ball in the header
        old_name = b'Archetypes.Ball.Ball_BasketBall\x00'
        new_name = b'Archetypes.Ball.ball_luminousairplane\x00'
        old_token = struct.pack('<i', len(old_name)) + old_name
        new_token = struct.pack('<i', len(new_name)) + new_name
        
        pos_in_header = header_data.find(old_token)
        if pos_in_header == -1:
            return False, "Old ball archetype not found in header"

        # 2. Update Net Version in header
        struct.pack_into('<I', header_data, 8, 11) # NetVersion is ~8 bytes into header data (after Major/Minor)
        
        # 3. Rename ball in header
        new_header_data = header_data[:pos_in_header] + new_token + header_data[pos_in_header+len(old_token):]
        diff = len(new_token) - len(old_token)
        
        # 4. Finalize Header
        new_h_sz = len(new_header_data)
        new_h_crc = calculate_ue3_crc(new_header_data)
        
        # 5. Body Analysis
        # Body starts immediately after header
        body_prefix_pos = 8 + old_h_sz
        body_size = struct.unpack('<I', data[body_prefix_pos:body_prefix_pos+4])[0]
        body_data = data[body_prefix_pos+8 : body_prefix_pos+8+body_size]
        
        # We don't need to change the body data, but we must re-sign it 
        # because the game might be picky about the section offsets.
        # Actually, the body CRC is independent.
        new_b_crc = calculate_ue3_crc(body_data)
        
        # 6. Assemble Final File
        final_data = bytearray()
        final_data += struct.pack('<I', new_h_sz)
        final_data += struct.pack('<I', new_h_crc)
        final_data += new_header_data
        
        final_data += struct.pack('<I', body_size)
        final_data += struct.pack('<I', new_b_crc)
        final_data += body_data
        
        # Append anything trailing (optional, but boxcars says Footer is after body)
        trailing_start = body_prefix_pos + 8 + body_size
        final_data += data[trailing_start:]

        with open(output_path, 'wb') as f:
            f.write(final_data)

        return True, f"Surgical Patch v2 Success! Header: {new_h_sz} bytes CP: {new_h_crc:08X}. Body: {body_size} bytes CP: {new_b_crc:08X}."
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 surgical_patch_v2.py <replay_file>")
        sys.exit(1)

    path = sys.argv[1]
    output = "surgical_v2_test.replay"
    success, msg = surgical_patch_v2(path, output)
    print(f"Result: {msg}")
