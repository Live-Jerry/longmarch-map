# -*- coding: utf-8 -*-
import os, glob, json

sessions_dir = r'C:\Users\RP Conference\.openclaw\agents\cz\sessions'

# Session 58c52909 = implementation session - find the map.js code that was applied
fpath = os.path.join(sessions_dir, '58c52909-c048-4d19-b5dd-8716743268f8.trajectory.jsonl')
with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            obj = json.loads(line)
        except:
            continue
        
        content = str(obj)
        if 'route-point-label' in content or 'divIcon' in content.lower():
            # Print relevant snippets
            if isinstance(obj, dict):
                msg = obj.get('message', obj)
                if isinstance(msg, dict):
                    c = msg.get('content', '')
                    if isinstance(c, list):
                        for item in c:
                            if isinstance(item, dict) and 'text' in item:
                                if 'route-point-label' in item['text'] or 'divIcon' in item['text'].lower():
                                    text = item['text'][:2000]
                                    print(f'--- Found in trajectory ---')
                                    print(text)
                                    print()
        if 'route-point-label' in content:
            pass  # found

print('=== DONE ===')
