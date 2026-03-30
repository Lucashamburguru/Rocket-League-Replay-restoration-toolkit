import os
import rl_replay_upgrader

def batch_convert():
    if not os.path.exists('analysis.txt'):
        print("analysis.txt not found. Run analyze_headers.py first.")
        return

    os.makedirs('converted', exist_ok=True)
    
    replays_to_convert = []
    with open('analysis.txt', 'r') as f:
        # Skip header lines
        lines = f.readlines()[2:]
        for line in lines:
            if '|' not in line: continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 3: continue
            
            filename = parts[0]
            net_version = parts[2]
            
            if net_version == '10':
                replays_to_convert.append(filename)

    print(f"Found {len(replays_to_convert)} Net 10 replays to convert.")
    
    success_count = 0
    for filename in replays_to_convert:
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found.")
            continue
            
        output_path = os.path.join('converted', filename)
        success, msg = rl_replay_upgrader.upgrade_replay(filename, output_path, target_net_version=11)
        if success:
            success_count += 1
        else:
            print(f"Failed to convert {filename}: {msg}")

    print("-" * 30)
    print(f"Batch conversion complete: {success_count}/{len(replays_to_convert)} successful.")
    print("Files saved in 'converted/' directory.")

if __name__ == '__main__':
    batch_convert()
