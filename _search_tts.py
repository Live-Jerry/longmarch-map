import os, glob

js_dir = r'D:\长征文化\001 项目源码\static\js'
for f in glob.glob(os.path.join(js_dir, '*.js')):
    with open(f, 'r', encoding='utf-8', errors='replace') as fh:
        content = fh.read()
        name = os.path.basename(f)
        if 'speech' in content.lower() or 'voice' in content.lower() or 'getVoices' in content or 'speak' in content:
            print(f'\n=== {name} ({len(content)} chars) ===')
            for i, line in enumerate(content.split('\n'), 1):
                if 'speech' in line.lower() or 'voice' in line.lower() or 'getVoices' in line or 'speak' in line.lower() or 'tts' in line.lower():
                    print(f'  L{i}: {line.strip()[:120]}')
