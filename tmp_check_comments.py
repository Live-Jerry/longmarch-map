# -*- coding: utf-8 -*-
"""Find Doxygen comment patterns in Python source that create heading-like structures."""
import re, os

src_dir = 'D:/长征文化/001 项目源码'

for root, dirs, files in os.walk(src_dir):
    for f in sorted(files):
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
        
        for i, line in enumerate(lines, 1):
            s = line.strip()
            
            # Check for Doxygen grouping/page commands that create top-level headings
            if any(cmd in s for cmd in ['@defgroup', '@addtogroup', '@page', '@mainpage',
                                         '@section', '@subsection', '@subsubsection',
                                         '@heading', '@name']):
                print(f'{f}:{i}: {s[:80]}')
            
            # Check for ## that might be parsed as markdown heading level 2
            if '## ' in s and not s.startswith('#'):
                # Inside a docstring, ## could be interpreted as a heading
                idx = s.index('## ')
                rest = s[idx+3:]
                if rest and not rest.startswith('@') and not rest.startswith('#'):
                    print(f'{f}:{i}: POSSIBLE ## heading -> "{rest[:60]}"')
            
            # Check for single # at start of line that might look like h1 markdown
            # (outside of docstrings)
