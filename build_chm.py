#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Post-process doxygen output for CHM compatibility.
Old HTML Help Workshop requires GBK-encoded HTML content.

Fix: Doxyfile OUTPUT_ENCODING and CHM_INDEX_ENCODING are both UTF-8,
so Doxygen produces all files (HTML, CSS, JS, HHC, HHK, HHP) in UTF-8.
This script converts them ALL to GBK for HTML Help Workshop.
"""
import os, glob, subprocess

DOX_DIR = r'D:\长征文化\004 项目文档\doxygen\html'
HHC = r'C:\Program Files (x86)\HTML Help Workshop\hhc.exe'

def convert_file(fp):
    """Convert one file from UTF-8 to GBK if it contains non-ASCII."""
    with open(fp, 'rb') as f:
        raw = f.read()
    
    # Only process if file has non-ASCII bytes
    if not any(b > 127 for b in raw):
        return False
    
    # Some files already have META charset declaration, some don't.
    # We decode as UTF-8 (which is what Doxygen now writes), then re-encode as GBK.
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        # Try GBK as fallback
        try:
            text = raw.decode('gbk')
        except:
            return False  # Can't handle this file
    
    # Update charset declarations in HTML files
    ext = os.path.splitext(fp)[1].lower()
    if ext == '.html':
        text = text.replace('charset=UTF-8', 'charset=GB2312')
        text = text.replace('charset=utf-8', 'charset=GB2312')
    elif ext == '.hhc':
        # HHC files: also add/update charset param if missing
        # HTML Help Workshop needs charset=gb2312 in the HTML header
        if 'charset=' not in text[:500].lower():
            # Insert charset after <HEAD>
            text = text.replace('<HEAD>', '<HEAD><meta http-equiv="Content-Type" content="text/html; charset=GB2312">')
        else:
            text = text.replace('charset=UTF-8', 'charset=GB2312')
            text = text.replace('charset=utf-8', 'charset=GB2312')
    elif ext == '.hhk':
        if 'charset=' not in text[:500].lower():
            text = text.replace('<HEAD>', '<HEAD><meta http-equiv="Content-Type" content="text/html; charset=GB2312">')
        else:
            text = text.replace('charset=UTF-8', 'charset=GB2312')
            text = text.replace('charset=utf-8', 'charset=GB2312')
    
    # Encode as GBK (superset of GB2312, handles more Chinese chars)
    try:
        gbk = text.encode('gbk')
    except UnicodeEncodeError as e:
        # Find and report the specific bad chars
        bad_chars = set()
        for i in range(e.start, min(e.start + 100, len(text))):
            try:
                text[i].encode('gbk')
            except:
                cp = ord(text[i])
                bad_chars.add(f'U+{cp:04X}')
        print(f'  WARN: {os.path.basename(fp)} has non-GBK chars: {bad_chars}')
        # Strip non-GBK characters instead of replacing with ?
        clean = ''
        for c in text:
            try:
                c.encode('gbk')
                clean += c
            except:
                pass  # strip it entirely
        gbk = clean.encode('gbk')
    
    with open(fp, 'wb') as f:
        f.write(gbk)
    return True

def convert_to_gbk(directory):
    """Convert all relevant files from UTF-8 to GBK."""
    count = 0
    # Files to convert: HTML, CSS, JS, HHC, HHK, HHP
    patterns = ['*.html', '*.css', '*.js', '*.hhc', '*.hhk', '*.hhp']
    for pattern in patterns:
        for fp in glob.glob(os.path.join(directory, pattern)):
            if convert_file(fp):
                count += 1
                if count % 50 == 0:
                    print(f'  ... converted {count} files')
    return count

def run_hhc(project_dir):
    """Run HTML Help Workshop compiler."""
    old_cwd = os.getcwd()
    os.chdir(project_dir)
    try:
        result = subprocess.run(
            [HHC, 'index.hhp'],
            capture_output=True, text=True, encoding='gbk', errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print('STDERR:', result.stderr)
        return result.returncode
    finally:
        os.chdir(old_cwd)

# Step 1: Clean old CHM
chm = os.path.join(DOX_DIR, 'longmarch.chm')
if os.path.exists(chm):
    os.remove(chm)
    print('Removed old CHM')

# Step 2: Convert all files to GBK
print('Converting files from UTF-8 to GBK...')
converted = convert_to_gbk(DOX_DIR)
print(f'Converted {converted} files to GBK')

# Step 3: Run HHC
print('Running HHC...')
rc = run_hhc(DOX_DIR)
print(f'HHC exit code: {rc}')

# Step 4: Verify
if os.path.exists(chm):
    size = os.path.getsize(chm)
    print(f'CHM created: {size} bytes')
else:
    print('CHM NOT created!')
