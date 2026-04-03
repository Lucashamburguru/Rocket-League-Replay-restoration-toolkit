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

def universal_patch(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        # 1. Header Analysis
        h_sz = struct.unpack('<I', data[0:4])[0]
        h_data = data[8:8+h_sz]
        
        # Determine if it's Hoops (Look for specialized basketball archetype or map names)
        is_hoops = b'Archetypes.Ball.Ball_BasketBall' in data or b'HoopsStadium' in data or b'hoopsStreet' in data
        
        # 2. Update NetVersion in Header (always)
        struct.pack_into('<I', data, 16, 11)
        h_data_patched = data[8:8+h_sz]
        h_crc = calculate_ue3_crc(h_data_patched)
        struct.pack_into('<I', data, 4, h_crc)

        # 3. Handle Body (Content)
        body_prefix_pos = 8 + h_sz
        body_size = struct.unpack('<I', data[body_prefix_pos:body_prefix_pos+4])[0]
        body_data = data[body_prefix_pos+8 : body_prefix_pos+8+body_size]
        
        final_body_data = body_data
        diff = 0
        
        if is_hoops:
            # Possible Hoops ball archetypes in legacy files
            candidates = [
                # (Old Name, New Name) 
                (b'Archetypes.Ball.Ball_BasketBall_Mutator\x00', b'Archetypes.Ball.ball_luminousairplane\x00'),
                (b'Archetypes.Ball.Ball_BasketBall\x00', b'Archetypes.Ball.ball_luminousairplane\x00'),
                (b'Archetypes.GameEvent.GameEvent_Basketball\x00', b'GameInfo_Basketball.GameInfo.GameInfo_Basketball:Archetype\x00'),
                (b'HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_TA_2.Goal_TA_0\x00', b'HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_Hoops_TA_0.Goal_Hoops_TA_0\x00'),
                (b'HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_TA_3.Goal_TA_0\x00', b'HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_Hoops_TA_1.Goal_Hoops_TA_0\x00')
            ]
            
            for old_name, new_name in candidates:
                old_token = struct.pack('<i', len(old_name)) + old_name
                new_token = struct.pack('<i', len(new_name)) + new_name
                
                pos_in_body = final_body_data.find(old_token)
                if pos_in_body != -1:
                    final_body_data = final_body_data[:pos_in_body] + new_token + final_body_data[pos_in_body+len(old_token):]
                    diff = len(new_token) - len(old_token)
        
        # 4. Finalize Body
        new_body_size = len(final_body_data)
        new_body_crc = calculate_ue3_crc(final_body_data)
        
        # 5. Rebuild Final Replay
        final_replay = bytearray()
        # Header block
        final_replay += data[0:8+h_sz]
        # Body prefix (Size, CRC)
        final_replay += struct.pack('<I', new_body_size)
        final_replay += struct.pack('<I', new_body_crc)
        # Body data
        final_replay += final_body_data
        
        # Trailing Footer data
        trailing_start = body_prefix_pos + 8 + body_size
        final_replay += data[trailing_start:]

        with open(output_path, 'wb') as f:
            f.write(final_replay)

        mode = "HOOPS-SHIFT" if is_hoops else "STANDARD-PATCH"
        return True, f"{mode}: {input_path} -> {output_path}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Universal Rocket League Replay Restorer (Net 10 -> 11)')
    parser.add_argument('--input', default='./input_replays', help='Directory containing the original .replay files')
    parser.add_argument('--output', default='./restored_replays', help='Directory to save the restored files')
    args = parser.parse_args()

    src_dir = os.path.abspath(args.input)
    dst_dir = os.path.abspath(args.output)
    
    if not os.path.exists(src_dir):
        print(f"Error: Input directory '{src_dir}' not found.")
        print("Please place your original .replay files in an 'input_replays' folder or use --input.")
        sys.exit(1)
        
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    files = [f for f in os.listdir(src_dir) if f.endswith('.replay')]
    if not files:
        print(f"No .replay files found in {src_dir}")
        sys.exit(0)

    print(f"--- Rocket League Replay Restorer (v1.0) ---")
    print(f"Input:  {src_dir}")
    print(f"Output: {dst_dir}")
    print(f"Processing {len(files)} replays...\n")
    
    success_count = 0
    for f in files:
        ok, msg = universal_patch(os.path.join(src_dir, f), os.path.join(dst_dir, f))
        if ok:
            success_count += 1
            print(f"[SUCCESS] {f}")
        else:
            print(f"[ FAILED ] {f}: {msg}")
            
    print(f"\nCompleted! {success_count}/{len(files)} replays successfully restored.")
    print(f"Files are located in: {dst_dir}")
