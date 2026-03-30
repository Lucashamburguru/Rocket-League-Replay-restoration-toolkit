import struct
import os
import sys

# Exact Rocket League/UE3 CRC32 Algorithm
# Based on Boxcars (Rust) and CPPRP implementation
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
    # Initial: !(0xefcb_f201.swap_bytes()) = 0xFE0D3410
    crc = 0xFE0D3410
    for byte in data:
        crc = (crc >> 8) ^ UNREAL_TABLE[(byte ^ (crc & 0xFF)) & 0xFF]
    
    # Final: (!crc).swap_bytes()
    final_crc = (~crc) & 0xFFFFFFFF
    final_swapped = struct.unpack('<I', struct.pack('>I', final_crc))[0]
    return final_swapped

def upgrade_replay(input_path, output_path, target_net_version=11):
    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        if len(data) < 20:
            return False, "File too small"

        header_size = struct.unpack('<I', data[0:4])[0]
        old_net_version = struct.unpack('<I', data[16:20])[0]

        # 1. Update Net Version Token (Fixed Header)
        struct.pack_into('<I', data, 16, target_net_version)

        # 2. Recalculate CRC using the UE3 bit-perfect algorithm
        # Data scope: bytes from index 8 up to (8 + header_size)
        header_data = data[8:8+header_size]
        new_crc = calculate_ue3_crc(header_data)
        
        struct.pack_into('<I', data, 4, new_crc)

        with open(output_path, 'wb') as f:
            f.write(data)

        return True, f"Upgraded Net {old_net_version} -> {target_net_version}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rl_replay_upgrader.py <replay_file> [...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        if not path.endswith(".replay"): continue
        if ".converted.replay" in path: continue
        
        output = path.replace(".replay", ".converted.replay")
        success, msg = upgrade_replay(path, output)
        print(f"{path:<40} | {msg}")
