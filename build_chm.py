# -*- coding: utf-8 -*-
"""
Fix CHM encoding: convert UTF-8 encoded Chinese in .hhc/.hhk to GBK,
then compile CHM using hhc.exe.

Usage:
  python build_chm.py          # fix + compile
  python build_chm.py --doxy   # re-run Doxygen first, then fix + compile
"""
import os
import sys
import subprocess

HTML_DIR = os.path.abspath('D:/长征文化/004 项目文档/doxygen/html')
HHC_EXE = r'C:\Program Files (x86)\HTML Help Workshop\hhc.exe'
NAME_PATTERN = b'<param name="Name" value="'
PREFIX_LEN = len(NAME_PATTERN)  # 26


def fix_file(path):
    """Convert UTF-8 encoded Name values to GBK in .hhc/.hhk files."""
    with open(path, 'rb') as f:
        raw = bytearray(f.read())

    idx = 0
    fixed = 0
    while True:
        idx = raw.find(NAME_PATTERN, idx)
        if idx < 0:
            break
        value_start = idx + PREFIX_LEN
        value_end = raw.find(b'"', value_start)
        if value_end < 0:
            break

        val_bytes = bytes(raw[value_start:value_end])

        # Already valid GBK? Leave as-is.
        try:
            val_bytes.decode('gbk')
            idx = value_end + 1
            continue
        except UnicodeDecodeError:
            pass

        # Try UTF-8 decoding
        try:
            utf8_text = val_bytes.decode('utf-8')
        except UnicodeDecodeError:
            idx = value_end + 1
            continue

        # Convert to GBK (replace emoji characters with ?)
        gbk_bytes = utf8_text.encode('gbk', errors='replace')
        raw[value_start:value_end] = gbk_bytes
        idx = value_start + len(gbk_bytes) + 1
        fixed += 1
        if fixed <= 3:
            print(f'  [{fixed}] "{utf8_text[:50]}"')

    with open(path, 'wb') as f:
        f.write(raw)
    return fixed


def compile_chm():
    """Run hhc.exe via cmd.exe to avoid subprocess path resolution bug."""
    chm = os.path.join(HTML_DIR, 'longmarch.chm')
    if os.path.exists(chm):
        os.remove(chm)

    # hhc.exe has a path resolution issue when called via Python subprocess
    # directly; using cmd.exe /c wrapper solves it.
    cmd = f'cd /d "{HTML_DIR}" && "{HHC_EXE}" index.hhp'
    proc = subprocess.run(
        ['cmd.exe', '/c', cmd],
        capture_output=True,
        timeout=120
    )
    out = proc.stdout.decode('gbk', errors='replace').strip()
    if out:
        # Show summary lines only
        for line in out.split('\n'):
            if any(k in line for k in ('Compiling', 'Created', 'Topics', 'Compression',
                                        'Compile time', 'Error:', 'HHC5')):
                print(f'  {line.strip()}')

    if os.path.exists(chm):
        print(f'\nCHM: {os.path.getsize(chm)} bytes ✓')
        return True
    else:
        print('\nCHM NOT GENERATED ✗')
        if out:
            print(f'  Last output: {out[-200:]}')
        return False


def run_doxygen():
    """Re-run Doxygen to regenerate HTML + .hhc/.hhk/.hhp."""
    print('=== Running Doxygen ===')
    # Clean output first
    for f in os.listdir(HTML_DIR):
        fp = os.path.join(HTML_DIR, f)
        if os.path.isfile(fp) or os.path.islink(fp):
            os.unlink(fp)
        elif os.path.isdir(fp):
            import shutil
            shutil.rmtree(fp)
    
    doxy = os.path.join(os.path.dirname(os.path.dirname(HTML_DIR)), '..', '..', 'Doxyfile')
    if not os.path.exists(doxy):
        doxy = 'D:/长征文化/Doxyfile'
    
    result = subprocess.run(
        [os.path.join(os.path.dirname(HTML_DIR), '..', '..',
                       '007 项目工具/doxygen-1.17.0.windows.x64.bin/doxygen.exe'),
         doxy],
        capture_output=True, text=True, timeout=300
    )
    for line in result.stderr.split('\n'):
        if 'html help compiler' in line or 'finished' in line:
            print(f'  {line.strip()}')
    print('  Doxygen done')


def main():
    if '--doxy' in sys.argv:
        run_doxygen()

    print('=== Fixing .hhc ===')
    n = fix_file(os.path.join(HTML_DIR, 'index.hhc'))
    print(f'Fixed {n} entries')

    print('\n=== Fixing .hhk ===')
    n = fix_file(os.path.join(HTML_DIR, 'index.hhk'))
    print(f'Fixed {n} entries')

    print('\n=== Compiling CHM ===')
    compile_chm()


if __name__ == '__main__':
    main()
