# -*- coding: utf-8 -*-
"""知常轩建站方案 V2.2 md -> docx 转换（含 GFM 表格/代码块/引用/列表）"""
import re, sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = r'004 项目文档\知常轩_网站建站方案_V2.2_定稿版.md'
DST = r'004 项目文档\知常轩_网站建站方案_V2.2_定稿版.docx'

def set_font(run, name='宋体', size=None, bold=None, italic=None, color=None, mono=False):
    if mono:
        run.font.name = 'Consolas'
        r = run._element.rPr.rFonts
        r.set(qn('w:eastAsia'), '宋体')
    else:
        run.font.name = name
        r = run._element.rPr.rFonts
        r.set(qn('w:eastAsia'), name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color: run.font.color.rgb = RGBColor(*color)

def add_inline(par, text, base_bold=False):
    """解析 **bold** / `code` / *italic*，普通文本按宋体 11pt"""
    tokens = re.split(r'(\*\*.*?\*\*|`[^`]*`|\*[^*]+?\*)', text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**'):
            r = par.add_run(tok[2:-2]); set_font(r, bold=True)
        elif tok.startswith('`') and tok.endswith('`'):
            r = par.add_run(tok[1:-1]); set_font(r, mono=True, size=10)
        elif tok.startswith('*') and tok.endswith('*'):
            r = par.add_run(tok[1:-1]); set_font(r, italic=True)
        else:
            r = par.add_run(tok); set_font(r, bold=base_bold if base_bold else None)

def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill)
    tcPr.append(shd)

def add_table(doc, rows):
    ncols = max(len(r) for r in rows)
    t = doc.add_table(rows=len(rows), cols=ncols)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j in range(ncols):
            cell = t.cell(i, j)
            txt = row[j] if j < len(row) else ''
            # 单元格内 \n 转真实换行（分段）
            parts = txt.split('\\n')
            first = True
            for part in parts:
                p = cell.paragraphs[0] if first else cell.add_paragraph()
                first = False
                add_inline(p, part)
                if i == 0:
                    for r in p.runs:
                        r.font.bold = True
            if i == 0:
                shade_cell(cell, 'D9D9D9')
    return t

def main():
    with open(SRC, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    doc = Document()
    # 默认样式
    normal = doc.styles['Normal']
    normal.font.name = '宋体'; normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    for sname in ['Heading 1','Heading 2','Heading 3','Heading 4']:
        st = doc.styles[sname]
        st.font.name = '黑体'
        st.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        st.font.color.rgb = RGBColor(0x1C, 0x1C, 0x2E)

    i = 0
    n = len(lines)
    in_code = False
    code_buf = []
    while i < n:
        line = lines[i].rstrip('\n')
        if in_code:
            if line.strip().startswith('```'):
                # 输出代码块：等宽字体 + 浅灰底
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.2)
                for k, cl in enumerate(code_buf):
                    r = p.add_run(cl)
                    set_font(r, mono=True, size=9)
                    if k < len(code_buf) - 1:
                        r.add_break()
                in_code = False; code_buf = []
            else:
                code_buf.append(line)
            i += 1; continue
        if line.strip().startswith('```'):
            in_code = True; code_buf = []; i += 1; continue
        s = line.strip()
        if not s:
            i += 1; continue
        # 水平分隔线
        if re.fullmatch(r'-{3,}', s):
            i += 1; continue
        # 表格
        if s.startswith('|') and i + 1 < n and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not re.fullmatch(r'[\s:|-]+', cells[0]) or not any(re.search(r'-', c) for c in cells):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            continue
        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            level = len(m.group(1))
            p = doc.add_heading('', level=min(level, 4))
            add_inline(p, m.group(2))
            i += 1; continue
        # 引用
        if s.startswith('>'):
            text = s.lstrip('>').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            add_inline(p, text)
            for r in p.runs:
                r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
            i += 1; continue
        # 列表
        m = re.match(r'^[-*]\s+(.*)$', s)
        if m:
            p = doc.add_paragraph(style='List Bullet')
            add_inline(p, m.group(1))
            i += 1; continue
        m = re.match(r'^(\d+)[.、]\s+(.*)$', s)
        if m:
            p = doc.add_paragraph(style='List Number')
            add_inline(p, m.group(2))
            i += 1; continue
        # 普通段落
        p = doc.add_paragraph()
        add_inline(p, s)
        i += 1

    doc.core_properties.title = '知常轩 网站建站方案 V2.2（定稿版）'
    doc.core_properties.author = '知常轩项目组'
    doc.save(DST)
    print('saved:', DST)

if __name__ == '__main__':
    main()
