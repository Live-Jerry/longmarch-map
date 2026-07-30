import os, subprocess

# Get the old version of map.js (from HEAD~5 - before the V2.1.0 changes)
result = subprocess.run(
    ['git', 'show', 'HEAD~5:001 项目源码/static/js/map.js'],
    capture_output=True, text=True, cwd='D:\\长征文化'
)
old_code = result.stdout

# Find loadRoutes function in old code
lines = old_code.split('\n')
in_func = False
func_lines = []
for i, line in enumerate(lines, 1):
    if 'function loadRoutes' in line:
        in_func = True
    if in_func:
        func_lines.append(f'{i}: {line}')
        if in_func and line.strip() == '}' and func_lines and func_lines[-1].strip().endswith('}'):
            if len(func_lines) > 5:
                break

for l in func_lines[:60]:
    print(l)
