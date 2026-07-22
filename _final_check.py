#!/usr/bin/env python
"""Final CHM verification."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

html_dir = r'D:\长征文化\004 项目文档\doxygen\html'

# CHANGELOG page
f = open(os.path.join(html_dir, 'md__c_h_a_n_g_e_l_o_g.html'), 'rb')
raw = f.read()
f.close()
text = raw.decode('gbk')
q = text.count('?')
print(f'CHANGELOG page: {q} question marks, {len(text)} chars')
for s in ['V2.0.0', '重走长征路', '长征文化数字地图']:
    print(f'  "{s}" found: {s in text}')

# HHC
f = open(os.path.join(html_dir, 'index.hhc'), 'rb')
raw = f.read()
f.close()
text = raw.decode('gbk')
q = text.count('?')
print(f'HHC: {q} question marks')
if q > 0:
    idx = text.find('?')
    print(f'  First ? context: {text[max(0,idx-20):idx+20]}')

# Index page
f = open(os.path.join(html_dir, 'index.html'), 'rb')
raw = f.read()
f.close()
text = raw.decode('gbk')
q = text.count('?')
print(f'index.html: {q} question marks')

# CHM
chm = os.path.join(html_dir, 'longmarch.chm')
if os.path.exists(chm):
    print(f'CHM: {os.path.getsize(chm)} bytes - READY')
else:
    print('CHM: NOT FOUND')
