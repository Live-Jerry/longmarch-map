#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build CHM from Doxygen output.
Usage:
  python build_chm.py          # convert to GBK + compile (existing files)
  python build_chm.py --doxy   # re-run Doxygen + convert + compile
"""
import os, glob, subprocess, shutil

DOX_DIR = r'D:\长征文化\004 项目文档\doxygen\html'
HHC = r'C:\Program Files (x86)\HTML Help Workshop\hhc.exe'
DOXYGEN = r'D:\长征文化\007 项目工具\doxygen-1.17.0.windows.x64.bin\doxygen.exe'
DOXYFILE = r'D:\长征文化\Doxyfile'

def clean_output(dirpath):
    """Remove all files and subdirectories in dirpath."""
    for name in os.listdir(dirpath):
        fp = os.path.join(dirpath, name)
        if os.path.isfile(fp) or os.path.islink(fp):
            os.unlink(fp)
        elif os.path.isdir(fp):
            shutil.rmtree(fp)

def run_doxygen():
    """Re-run Doxygen to regenerate all HTML + index files."""
    print('=== Running Doxygen ===')
    clean_output(DOX_DIR)
    result = subprocess.run(
        [DOXYGEN, 'Doxyfile'],
        capture_output=True, timeout=300,
        cwd=r'D:\长征文化'
    )
    out = result.stdout.decode('gbk', errors='replace')
    err = result.stderr.decode('gbk', errors='replace')
    for line in err.split('\n'):
        if 'finished' in line:
            print(f'  {line.strip()}')
    print('  Doxygen done')

def convert_file(fp):
    """Convert one file from UTF-8 to GBK if it contains non-ASCII."""
    with open(fp, 'rb') as f:
        raw = f.read()
    
    if not any(b > 127 for b in raw):
        return False
    
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = raw.decode('gbk')
        except:
            return False
    
    ext = os.path.splitext(fp)[1].lower()
    if ext == '.html':
        text = text.replace('charset=UTF-8', 'charset=GB2312')
        text = text.replace('charset=utf-8', 'charset=GB2312')
    elif ext == '.hhc':
        if 'charset=' not in text[:500].lower():
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
    
    try:
        gbk = text.encode('gbk')
    except UnicodeEncodeError as e:
        bad_chars = set()
        for i in range(e.start, min(e.start + 100, len(text))):
            try:
                text[i].encode('gbk')
            except:
                bad_chars.add(f'U+{ord(text[i]):04X}')
        print(f'  WARN: {os.path.basename(fp)} has non-GBK chars: {bad_chars}')
        clean = ''.join(c for c in text if _is_gbk(c))
        gbk = clean.encode('gbk')
    
    with open(fp, 'wb') as f:
        f.write(gbk)
    return True

def _post_doxygen_cleanup(directory):
    """Fix known Doxygen CSS issues before GBK conversion."""
    css_path = os.path.join(directory, "doxygen.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            text = f.read()
        text = text.replace(chr(0x2610), "[ ]").replace(chr(0x2611), "[x]")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(text)

def _is_gbk(c):
    try:
        c.encode('gbk')
        return True
    except:
        return False

def convert_to_gbk(directory):
    """Convert all relevant files from UTF-8 to GBK."""
    count = 0
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

def main():
    import sys
    
    if '--doxy' in sys.argv:
        run_doxygen()
    
    chm = os.path.join(DOX_DIR, 'longmarch.chm')
    if os.path.exists(chm):
        os.remove(chm)
        print('Removed old CHM')
    
    print('Converting files from UTF-8 to GBK...')
    _post_doxygen_cleanup(DOX_DIR)
    converted = convert_to_gbk(DOX_DIR)
    print(f'Converted {converted} files to GBK')
    
    print('Running HHC...')
    rc = run_hhc(DOX_DIR)
    print(f'HHC exit code: {rc}')
    
    if os.path.exists(chm):
        print(f'CHM created: {os.path.getsize(chm)} bytes')
    else:
        print('CHM NOT created!')

if __name__ == '__main__':
    main()
