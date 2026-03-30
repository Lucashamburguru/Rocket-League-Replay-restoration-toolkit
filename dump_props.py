import os
import struct
from analyze_headers import analyze_replay

def dump_props(path):
    print(f"\n--- {path} ---")
    data = analyze_replay(path)
    if not data:
        print("Error analyzing")
        return
    for k, v in data['Properties'].items():
        print(f"  {k}: {v}")

if __name__ == '__main__':
    dump_props('36BE614746BB61DC8DE974AD7046ECA8.replay')
    dump_props('0308A3E64A7FE845257EDF8F71C0A323.replay')
