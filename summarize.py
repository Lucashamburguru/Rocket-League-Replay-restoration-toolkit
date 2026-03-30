import sys
import os

def summarize():
    maps = {}
    if not os.path.exists('analysis.txt'):
        print("analysis.txt not found")
        return

    with open('analysis.txt', 'r') as f:
        lines = f.readlines()

    for line in lines:
        if '|' not in line: continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 5 or parts[0] == 'Filename': continue
        
        m = parts[3]
        d = parts[4]
        v = parts[1]
        
        if m not in maps:
            maps[m] = {'dates': [], 'versions': set()}
        
        maps[m]['dates'].append(d)
        maps[m]['versions'].add(v)

    print(f"{'Map Name':<25} | {'Count':<5} | {'Earliest Date':<20} | {'Latest Date':<20} | {'Versions'}")
    print("-" * 100)
    for m, data in sorted(maps.items()):
        dates = sorted(data['dates'])
        versions = ", ".join(sorted(list(data['versions'])))
        print(f"{m:<25} | {len(dates):<5} | {dates[0]:<20} | {dates[-1]:<20} | {versions}")

if __name__ == '__main__':
    summarize()
