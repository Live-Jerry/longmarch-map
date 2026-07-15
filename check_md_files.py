import glob, os
files = sorted([os.path.basename(f) for f in glob.glob(r'D:\长征文化\004 项目文档\doxygen\html\md_*.html')])
for f in files:
    print(f)
print(f'\nTotal md doc pages: {len(files)}')
