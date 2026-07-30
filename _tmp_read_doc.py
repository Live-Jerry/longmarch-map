# -*- coding: utf-8 -*-
import docx
d = docx.Document(r'D:\长征文化\004 项目文档\长征文化数字地图_版本管理方案_V3.1.docx')
for p in d.paragraphs:
    t = p.text.strip()
    if t:
        print(t)
