# -*- coding: utf-8 -*-
import os, glob, re

sessions_dir = r'C:\Users\RP Conference\.openclaw\agents\cz\sessions'

# Search trajectory files and main jsonl files
sources = sorted(glob.glob(os.path.join(sessions_dir, '*.trajectory.jsonl')))
sources += sorted(glob.glob(os.path.join(sessions_dir, '????????-*.jsonl')))
sources = [s for s in sources if not s.endswith('.lock')]

print(f'Searching {len(sources)} files...')

keywords = [
    'route-point-label', 'routePointLabel', 'routePointLabel',
    '\u6f2b\u6e38\u70b9.*\u540d\u5b57', '\u6f2b\u6e38\u70b9.*\u663e\u793a',
    '\u53d1\u5149', 'glow',
    '\u5e95\u8272.*\u53bb\u6389', '\u53bb\u6389.*\u5e95\u8272',
    '\u4e91\u77f3\u5c71', '\u9a6c\u9053\u53e3.*\u6807\u6ce8',
    '\u8def\u7ebf\u70b9.*\u6807\u6ce8', '\u8def\u7ebf\u70b9.*\u540d\u5b57',
    'pt_labels', 'text-shadow', 'RoutePointLabel',
]

for fpath in sources:
    fname = os.path.basename(fpath)
    try:
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except:
        continue

    for kw in keywords:
        idx = content.find(kw)
        if idx >= 0:
            start = max(0, idx - 200)
            end = min(len(content), idx + 400)
            snippet = content[start:end].replace('\r\n', '\n').replace('\r', '\n')
            lines = snippet.split('\n')
            cleaned = '\n'.join(l[:300] for l in lines)
            print(f'\n=== {fname} (found: {kw}) ===')
            print(cleaned[:2000])

print('\n=== SEARCH DONE ===')
