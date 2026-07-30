import sys, json
data = json.load(sys.stdin)
if data.get('code') == 0:
    segs = data.get('data', {}).get('segments', [])
    print(f'Segments: {len(segs)}')
    wt = sum(1 for s in segs if s.get('title'))
    nt = sum(1 for s in segs if not s.get('title'))
    print(f'With title: {wt}, Without title: {nt}')
    for s in segs[:10]:
        print(f'  [{s.get("title") or "(no title)"}]')
else:
    print('API error:', data.get('message'))
