import struct
import os
import sys

def read_string(f):
    try:
        size_data = f.read(4)
        if not size_data:
            return None
        size = struct.unpack('<I', size_data)[0]
        if size == 0:
            return ""
        # Handle cases where size might be negative or too large
        if size > 1024 * 1024:
            return None
        data = f.read(size)
        return data.decode('utf-8', errors='ignore').rstrip('\x00')
    except Exception as e:
        return None

def analyze_replay(path):
    try:
        with open(path, 'rb') as f:
            # Header length
            header_len_data = f.read(4)
            if not header_len_data: return None
            header_len = struct.unpack('<I', header_len_data)[0]
            
            # CRC
            crc_data = f.read(4)
            if not crc_data: return None
            crc = struct.unpack('<I', crc_data)[0]
            
            # Engine version
            engine_v_data = f.read(4)
            if not engine_v_data: return None
            engine_v = struct.unpack('<I', engine_v_data)[0]
            
            # Licensee version
            licensee_v_data = f.read(4)
            if not licensee_v_data: return None
            licensee_v = struct.unpack('<I', licensee_v_data)[0]
            
            # In newer versions, there's a net version
            net_v = None
            if engine_v >= 868 and licensee_v >= 18:
                net_v_data = f.read(4)
                if net_v_data:
                    net_v = struct.unpack('<I', net_v_data)[0]
                
            # Replay class
            cls = read_string(f)
            
            # Properties
            properties = {}
            while True:
                prop_name = read_string(f)
                if prop_name is None or prop_name == 'None':
                    break
                
                prop_type = read_string(f)
                data_size_data = f.read(8)
                if not data_size_data: break
                data_size = struct.unpack('<Q', data_size_data)[0]
                
                val = None
                if prop_type == 'IntProperty':
                    val_data = f.read(4)
                    if val_data: val = struct.unpack('<I', val_data)[0]
                elif prop_type == 'StrProperty':
                    val = read_string(f)
                elif prop_type == 'FloatProperty':
                    val_data = f.read(4)
                    if val_data: val = struct.unpack('<f', val_data)[0]
                elif prop_type == 'NameProperty':
                    val = read_string(f)
                elif prop_type == 'ArrayProperty':
                    # Skip for now
                    f.seek(data_size, os.SEEK_CUR)
                    val = '<Array>'
                elif prop_type == 'ByteProperty':
                    # Skip for now
                    f.seek(data_size, os.SEEK_CUR)
                    val = '<Byte>'
                elif prop_type == 'QWordProperty':
                    val_data = f.read(8)
                    if val_data: val = struct.unpack('<Q', val_data)[0]
                elif prop_type == 'BoolProperty':
                    val_data = f.read(1)
                    if val_data: val = struct.unpack('<B', val_data)[0]
                else:
                    f.seek(data_size, os.SEEK_CUR)
                    val = f'<Unknown type {prop_type}>'
                
                properties[prop_name] = val
                
            return {
                'EngineVersion': engine_v,
                'LicenseeVersion': licensee_v,
                'NetVersion': net_v,
                'Class': cls,
                'Properties': properties
            }
    except Exception as e:
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        replays = sys.argv[1:]
    else:
        replays = [f for f in os.listdir('.') if f.endswith('.replay')]
    
    print(f"{'Filename':<40} | {'Version':<10} | {'Net':<10} | {'Map':<20} | {'Date'}")
    print("-" * 110)
    for p in sorted(replays):
        if not os.path.exists(p): continue
        data = analyze_replay(p)
        filename = os.path.basename(p)
        if not data:
            continue
        
        map_name = data['Properties'].get('MapName', 'Unknown')
        date_str = data['Properties'].get('Date', 'Unknown')
        version_str = f"{data['EngineVersion']}.{data['LicenseeVersion']}"
        net_str = str(data['NetVersion']) if data['NetVersion'] is not None else "N/A"
        
        print(f"{filename:<40} | {version_str:<10} | {net_str:<10} | {map_name:<20} | {date_str}")
