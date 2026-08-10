# -*- coding: utf-8 -*-
"""生成道德经 81 章目录页"""
import io, json, os

BASE = r'D:\长征文化\009 知常轩\002 项目资源\道德经'
SRC = os.path.join(BASE, '结构化数据', '道德经_结构化_81章.json')
OUT = os.path.join(BASE, '页面_81章', '00_目录.html')

with io.open(SRC, encoding='utf-8') as f:
    data = json.load(f)

TITLES = {
 1:'众妙之门', 2:'美恶相形', 3:'不尚贤', 4:'道冲而用', 5:'天地不仁', 6:'谷神不死',
 7:'天长地久', 8:'上善若水', 9:'功遂身退', 10:'载营魄抱一', 11:'无之为用', 12:'五色令人目盲',
 13:'宠辱若惊', 14:'视之不见', 15:'古之善为道者', 16:'致虚守静', 17:'太上不知有之', 18:'大道废',
 19:'绝圣弃智', 20:'唯之与阿', 21:'孔德之容', 22:'曲则全', 23:'希言自然', 24:'企者不立',
 25:'有物混成', 26:'重为轻根', 27:'善行无辙', 28:'知其雄', 29:'将欲取天下', 30:'以道佐人主',
 31:'夫兵者', 32:'道常无名', 33:'知人者智', 34:'大道泛兮', 35:'执大象', 36:'将欲歙之',
 37:'道恒无为', 38:'上德不德', 39:'昔之得一者', 40:'反者道之动', 41:'上士闻道', 42:'道生一',
 43:'天下之至柔', 44:'名与身孰亲', 45:'大成若缺', 46:'天下有道', 47:'不出户', 48:'为学日益',
 49:'圣人常无心', 50:'出生入死', 51:'道生之德畜之', 52:'天下有始', 53:'使我介然有知', 54:'善建者不拔',
 55:'含德之厚', 56:'知者不言', 57:'以正治国', 58:'其政闷闷', 59:'治人事天', 60:'治大国若烹小鲜',
 61:'大国者下流', 62:'道者万物之奥', 63:'为无为', 64:'其安易持', 65:'古之善为道者', 66:'江海能为百谷王',
 67:'天下皆谓我道大', 68:'善为士者不武', 69:'用兵有言', 70:'吾言甚易知', 71:'知不知上', 72:'民不畏威',
 73:'勇于敢则杀', 74:'民不畏死', 75:'民之饥', 76:'人之生也柔弱', 77:'天之道', 78:'天下莫柔弱于水',
 79:'和大怨', 80:'小邦寡民', 81:'信言不美',
}

def num_to_cn(n):
    cn = '零一二三四五六七八九'
    if n <= 10: return '十' if n == 10 else cn[n]
    if n < 20: return '十' + cn[n-10]
    if n < 100: return cn[n//10] + '十' + (cn[n%10] if n%10 else '')
    return cn[n//10] + '十' + (cn[n%10] if n%10 else '')

rows = []
for d in data:
    ch = int(d['chapter'])
    cn = num_to_cn(ch)
    title = TITLES.get(ch, '')
    rows.append(f'<a class="row" href="{ch:02d}章.html"><span class="no">{cn}</span><span class="t">{title}</span></a>')

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>道德经 · 目录 · 知常轩</title>
<style>
  :root {{ --xuan-qing:#1C1C2E; --xiang-huang:#E8C547; --jiang-chi:#C73E3A; --cui-qing:#2D6A4F; --shuang-bai:#F5F0E8; --yue-bai:#E8EEF2; --mo-hei:#1A1A1A; --qing-ci:#7BA3A8; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--shuang-bai); color:var(--mo-hei); font-family:"Songti SC","SimSun","Noto Serif CJK SC",serif; }}
  .top-band {{ background:var(--xuan-qing); color:var(--xiang-huang); text-align:center; padding:30px 16px 24px; position:relative; overflow:hidden; }}
  .top-band::before,.top-band::after {{ content:"☰☰☰☰☰☰☰☰☰☰"; position:absolute; left:0; right:0; color:rgba(232,197,71,.18); letter-spacing:6px; font-size:12px; }}
  .top-band::before {{ top:8px; }} .top-band::after {{ bottom:8px; }}
  .top-band h1 {{ font-size:30px; letter-spacing:14px; }}
  .top-band p {{ font-size:13px; letter-spacing:4px; margin-top:8px; color:var(--yue-bai); opacity:.8; }}
  .container {{ max-width:860px; margin:0 auto; padding:28px 20px 60px; }}
  .grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }}
  @media (max-width:600px) {{ .grid {{ grid-template-columns:1fr; }} }}
  .row {{ display:flex; align-items:baseline; gap:14px; background:#fff; border:1px solid #e5ddd0; border-radius:6px; padding:12px 18px; text-decoration:none; color:var(--mo-hei); transition:all .15s; }}
  .row:hover {{ border-color:var(--xiang-huang); box-shadow:0 2px 10px rgba(28,28,46,.08); transform:translateY(-1px); }}
  .no {{ font-size:18px; font-weight:700; color:var(--jiang-chi); letter-spacing:1px; min-width:56px; }}
  .t {{ font-size:16px; letter-spacing:2px; color:#333; }}
  footer {{ text-align:center; color:#999; font-size:12px; letter-spacing:3px; padding:20px 0 40px; border-top:1px solid #e0d8c8; }}
</style>
</head>
<body>

<div class="top-band">
  <h1>道德经</h1>
  <p>知常轩 · 儒与道 · 儿童精读系列</p>
</div>

<div class="container">
  <div class="grid">
{chr(10).join(rows)}
  </div>
</div>

<footer>知常轩 · 公益教育平台<div style="font-size:12px;color:#aaa;margin-top:6px;">底本说明：原文据帛书本（用「恒」字），第四十七章据通行本补入；译文为白话对照。仅供学习参考。</div></footer>

</body>
</html>"""

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('目录已生成:', OUT)
