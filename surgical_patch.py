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

def surgical_patch_ball(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        # Old Ball: Archetypes.Ball.Ball_BasketBall (29 chars)
        # New Ball: Archetypes.Ball.ball_luminousairplane (35 chars)
        old_name = b'Archetypes.Ball.Ball_BasketBall\x00'
        new_name = b'Archetypes.Ball.ball_luminousairplane\x00'
        
        # UE3 Strings are [Length (4)] + [String + Null]
        old_token = struct.pack('<i', len(old_name)) + old_name
        new_token = struct.pack('<i', len(new_name)) + new_name
        
        pos = data.find(old_token)
        if pos == -1:
            return False, "Old ball archetype not found in header"

        # 1. Update Net Version Token (Fixed Header at offset 16)
        struct.pack_into('<I', data, 16, 11)

        # 2. String Injection & Data Shift
        # Insert the new name and shift everything after it
        diff = len(new_token) - len(old_token)
        new_data = data[:pos] + new_token + data[pos + len(old_token):]
        # Data became 'bytes' after slicing. Re-convert back to bytearray.
        new_data = bytearray(new_data)

        # 3. Update Header Size (Field at Byte 0)
        old_h_sz = struct.unpack('<I', new_data[0:4])[0]
        new_h_sz = old_h_sz + diff
        struct.pack_into('<I', new_data, 0, new_h_sz)

        # 4. Recalculate CRC using the UE3 bit-perfect algorithm
        # Header starts at byte 8 and ends at new_h_sz
        header_data = new_data[8:8+new_h_sz]
        new_crc = calculate_ue3_crc(header_data)
        
        # Binary update of the CRC field
        struct.pack_into('<I', new_data, 4, new_crc)

        with open(output_path, 'wb') as f:
            f.write(new_data)

        return True, f"Surgical Patch Success! Ball index updated, header shifted by {diff} bytes, CRC verified."
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 surgical_patch.py <replay_file>")
        sys.exit(1)

    path = sys.argv[1]
    output = "surgical_test.replay"
    success, msg = surgical_patch_ball(path, output)
    print(f"Result: {msg}")
