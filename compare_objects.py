import struct
import sys

def extract_objects(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    # After properties, the 'None' marker ends the dictionary.
    none_marker = b'\x05\x00\x00\x00None\x00'
    none_pos = data.find(none_marker)
    if none_pos == -1:
        return []
    
    # After properties, there is a list of strings (Objects).
    # Format: [Number of Objects (4)] + [Length (4) + String + Null]*Number
    # But wait! The Object list is part of the header, BEFORE 'None'?
    # No, boxcars says: properties -> objects -> names -> class_indices
    # Let's re-read the UE3 Header structure.
    
    # Properties are at the beginning. They end with 'None'.
    # Following 'None', there is a 4-byte count of 'Objects'.
    obj_count_pos = none_pos + len(none_marker)
    obj_count = struct.unpack('<I', data[obj_count_pos:obj_count_pos+4])[0]
    
    objects = []
    curr = obj_count_pos + 4
    for _ in range(min(obj_count, 2000)): # Safety limit
        l = struct.unpack('<i', data[curr:curr+4])[0]
        curr += 4
        if l > 0:
            s = data[curr:curr+l-1].decode('utf-8', errors='ignore')
            curr += l
            objects.append(s)
        elif l < 0:
            l = -l * 2
            s = data[curr:curr+l-2].decode('utf-16', errors='ignore')
            curr += l
            objects.append(s)
        else:
            objects.append("")
            
    return objects

if __name__ == "__main__":
    working = extract_objects('36BE614746BB61DC8DE974AD7046ECA8.replay')
    legacy = extract_objects('0308A3E64A7FE845257EDF8F71C0A323.replay')
    
    print(f"Working objects: {len(working)}")
    print(f"Legacy objects:  {len(legacy)}")
    
    # Find a common object and compare its index
    ball_name = "Archetypes.Ball.ball_luminousairplane"
    w_idx = working.index(ball_name) if ball_name in working else -1
    l_idx = legacy.index(ball_name) if ball_name in legacy else -1
    
    print(f"Ball ({ball_name}) index:")
    print(f"  Working: {w_idx}")
    print(f"  Legacy:  {l_idx}")
    
    # Dump first 20 for diff
    print("\n--- First 20 Objects Comparison ---")
    for i in range(20):
        w = working[i] if i < len(working) else "N/A"
        l = legacy[i] if i < len(legacy) else "N/A"
        print(f"{i:03}: {w:<40} | {l}")
