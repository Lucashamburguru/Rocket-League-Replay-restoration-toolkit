import struct
import os

def find_netstream_header(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    # The properties end with the 'None' string.
    # In RL replays, strings are (Length + 4, String + null).
    # 'None' = [0x5, 0x0, 0x0, 0x0] + 'None\x00'
    none_marker = b'\x05\x00\x00\x00None\x00'
    offset = data.find(none_marker)
    if offset == -1:
        return "None marker not found"
    
    # After 'None', there are:
    # 4 bytes for Replay Class (usually 'TAGame.Replay_Soccar_TA')
    # No, wait. The 'None' marker is the END of the properties list.
    # After properties, we have:
    # 4 bytes: Number of frames
    # 4 bytes: Number of netstream frames?
    # No, let's look at boxcars:
    # After properties, it reads 4 bytes for 'num_frames'
    # Then 4 bytes for 'netstream_size'
    # Then 'net_version' if engine >= 868 and licensee >= 18.
    
    # Let's dump 64 bytes after 'None'
    after_none = data[offset + len(none_marker):offset + len(none_marker) + 64]
    
    return {
        'offset': offset,
        'marker_len': len(none_marker),
        'hex_after': after_none.hex()
    }

if __name__ == "__main__":
    print(f"March 11 (Net 11): {find_netstream_header('36BE614746BB61DC8DE974AD7046ECA8.replay')}")
    print(f"Legacy (Net 10): {find_netstream_header('0308A3E64A7FE845257EDF8F71C0A323.replay')}")
