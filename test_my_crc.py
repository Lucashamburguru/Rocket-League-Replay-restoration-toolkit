import struct
import rl_replay_upgrader

def test_on_existing(path):
    with open(path, 'rb') as f:
        data = f.read()
    header_size = struct.unpack('<I', data[0:4])[0]
    file_crc_val = struct.unpack('<I', data[4:8])[0]
    header_data = data[8:8+header_size]
    calc_crc = rl_replay_upgrader.calculate_crc(header_data)
    print(f"File: {path}")
    print(f"Header Size: {header_size}")
    print(f"File CRC: {file_crc_val:08X}")
    print(f"Calc CRC: {calc_crc:08X}")
    print(f"Match: {file_crc_val == calc_crc}")
    print("-" * 20)

if __name__ == "__main__":
    test_on_existing('36BE614746BB61DC8DE974AD7046ECA8.replay')
    test_on_existing('0308A3E64A7FE845257EDF8F71C0A323.replay')
