import re
with open(r'D:\长征文化\_idx_check.html', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find all script tags with src
for m in re.finditer(r'<script[^>]*src="([^"]+)"[^>]*>', content):
    print(f'SCRIPT: {m.group(1)}')
# Find inline script sections
for m in re.finditer(r'<script>(.*?)</script>', content, re.DOTALL):
    snippet = m.group(1)[:100].replace('\n', ' ').strip()
    print(f'INLINE: {snippet}')
