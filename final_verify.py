import struct
import rl_replay_upgrader

def verify(path):
    with open(path, 'rb') as f:
        data = f.read()
    sz = struct.unpack('<I', data[0:4])[0]
    fcrc = struct.unpack('<I', data[4:8])[0]
    hdata = data[8:8+sz]
    ccrc = rl_replay_upgrader.calculate_crc(hdata)
    print(f"File: {path}")
    print(f"File CRC: {fcrc:08X}")
    print(f"Calc CRC: {ccrc:08X}")
    print(f"Match: {fcrc == ccrc}")
    print("-" * 20)

verify('36BE614746BB61DC8DE974AD7046ECA8.replay')
verify('0308A3E64A7FE845257EDF8F71C0A323.converted.replay')
