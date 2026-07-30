# -*- coding: utf-8 -*-
import os, json

sessions_dir = r'C:\Users\RP Conference\.openclaw\agents\cz\sessions'

# Session af8f9bce - look for route-point-label code
fpath = os.path.join(sessions_dir, 'af8f9bce-c1bf-4a86-815a-cd8abb9589cb.trajectory.jsonl')
if not os.path.exists(fpath):
    print(f'File not found: {fpath}')
else:
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line: continue
            if 'route-point-label' in line:
                try:
                    obj = json.loads(line)
                except:
                    print(f'Line {i}: JSON parse error (but matched)')
                    print(line[:500])
                    print()
                    continue
                
                # Try to extract text content
                content = str(obj)
                
                # Find the divIcon code section
                idx = content.find('route-point-label')
                start = max(0, idx - 500)
                end = min(len(content), idx + 500)
                snippet = content[start:end]
                
                # Decode unicode escapes for readability
                snippet = snippet.replace('\\u003c', '<').replace('\\u003e', '>').replace('\\u0027', "'").replace('\\n', '\n').replace('\\r', '')
                
                print(f'=== Line {i} ==')
                print(snippet)
                print()

# Also check the reset file for same session
fpath2 = os.path.join(sessions_dir, 'af8f9bce-c1bf-4a86-815a-cd8abb9589cb.jsonl.reset.2026-07-28T09-21-14.641Z')
if os.path.exists(fpath2):
    with open(fpath2, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        idx = content.find('route-point-label')
        if idx >= 0:
            start = max(0, idx - 800)
            end = min(len(content), idx + 800)
            snippet = content[start:end].replace('\\u003c', '<').replace('\\u003e', '>').replace('\\u0027', "'").replace('\\n', '\n').replace('\\r', '')
            print('=== RESET file ==')
            print(snippet)

print('\n=== DONE ===')
