"""Fix Doxyfile EXCLUDE properly"""
import os

infile = r'D:\长征文化\Doxyfile'
with open(infile, 'r', encoding='utf-8') as f:
    content = f.read()

# Set EXCLUDE with absolute paths to agent files
exclude = [
    r'./AGENTS.md',
    r'./SOUL.md',
    r'./IDENTITY.md',
    r'./TOOLS.md',
    r'./USER.md',
    r'./HEARTBEAT.md',
    r'./MEMORY.md',
    r'./memory/',
    r'./fix_doxygen.py',
    r'./docs/',
    r'./docs_doxygen/',
]

# Replace EXCLUDE_PATTERNS setting
old = 'EXCLUDE_PATTERNS       =\n'
new = f'EXCLUDE                = {" ".join(exclude)}\n'
content = content.replace(old, new)

with open(infile, 'w', encoding='utf-8') as f:
    f.write(content)

print('EXCLUDE set')

# Regenerate
doxygen_exe = r'D:\长征文化\007 项目工具\doxygen-1.17.0.windows.x64.bin\doxygen.exe'
os.chdir(r'D:\长征文化')
os.system(f'"{doxygen_exe}" Doxyfile')
print('Doxygen regenerated')
