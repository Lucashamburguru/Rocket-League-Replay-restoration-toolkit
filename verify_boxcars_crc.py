import struct

# Port of Boxcars/Unreal Engine 3 CRC32
# Polynomial: 0x04C11DB7
# Non-Reflected (Normal)
# Initial: !(0xefcb_f201.swap_bytes())
# Final: !crc.swap_bytes()

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
        # In boxcars, table entries are swapped immediately
        # table[0][i] = crc.swap_bytes();
        val = crc & 0xFFFFFFFF
        swapped = struct.unpack('<I', struct.pack('>I', val))[0]
        table[i] = swapped
    return table

UNREAL_TABLE = make_unreal_table()

def boxcars_crc(data):
    # let mut crc = !(0xefcb_f201_u32.swap_bytes());
    # 0xEF CB F2 01 -> Swap -> 01 F2 CB EF
    # !0x01F2CBEF = 0xFE0D3410
    crc = 0xFE0D3410
    
    # Simple byte-by-byte fold (non-optimized for clarity)
    # (acc >> 8) ^ CRC_TABLE[0][(u32::from(x) ^ (acc & 0xFF)) as usize]
    for x in data:
        crc = (crc >> 8) ^ UNREAL_TABLE[(x ^ (crc & 0xFF)) & 0xFF]
    
    # (!crc).swap_bytes()
    final_crc = (~crc) & 0xFFFFFFFF
    # Swap bytes
    final_swapped = struct.unpack('<I', struct.pack('>I', final_crc))[0]
    return final_swapped

if __name__ == "__main__":
    def test_on_existing(path):
        with open(path, 'rb') as f:
            data = f.read()
        sz = struct.unpack('<I', data[0:4])[0]
        fcrc = struct.unpack('<I', data[4:8])[0]
        hdata = data[8:8+sz]
        calc = boxcars_crc(hdata)
        print(f"File: {path}")
        print(f"  Target CRC: {fcrc:08X}")
        print(f"  Calc CRC:   {calc:08X}")
        print(f"  Match:      {fcrc == calc}")

    test_on_existing('36BE614746BB61DC8DE974AD7046ECA8.replay')
    test_on_existing('0308A3E64A7FE845257EDF8F71C0A323.replay')
