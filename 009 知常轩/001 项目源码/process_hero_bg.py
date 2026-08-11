# -*- coding: utf-8 -*-
"""知常轩首页 hero 背景图处理：黑白线稿 -> 金色线条 + 朱红印章，白底透明"""
from PIL import Image, ImageChops
import os

SRC = r"D:\长征文化\002 项目资源\知常轩\知常轩首页背景.png"
OUT = r"D:\长征文化\009 知常轩\001 项目源码\static\img\hero_bg.png"

GOLD = (212, 175, 95)      # 柔和暗金 #D4AF5F：比标题湘黄低一档，不抢标题
ZHU = (200, 90, 70)        # 朱红（降饱和）

img = Image.open(SRC).convert("RGBA")
w, h = img.size
# 压到 1600 宽（cover 足够，控制文件体积）
if w > 1600:
    img = img.resize((1600, int(h * 1600 / w)), Image.LANCZOS)
w, h = img.size
print("处理后尺寸:", (w, h))

r, g, b, a = img.split()
gray = img.convert("L")

# 1) 线条 alpha：反相灰度；乘 0.58——建筑清晰可见但不过分抢眼
inv = ImageChops.invert(gray)
alpha_ink = inv.point(lambda v: int(v * 0.58))

# 2) 红色 mask：R 显著高于 G/B 的像素（朱红印章文字）
red_diff = ImageChops.subtract(r, ImageChops.lighter(g, b))
red_mask = red_diff.point(lambda v: 255 if v > 36 else 0)

# 3) 合成：先金色线条铺在透明底上
transparent = Image.new("RGBA", (w, h), (0, 0, 0, 0))
gold_layer = Image.new("RGBA", (w, h), GOLD + (255,))
out = Image.composite(gold_layer, transparent, alpha_ink)

# 4) 红色区域覆盖朱红（印章也降 alpha，不抢戏）
red_layer = Image.new("RGBA", (w, h), ZHU + (150,))
out = Image.composite(red_layer, out, red_mask)

out.save(OUT)
# 转 WebP（体积小、支持透明）
out.save(OUT.replace('.png', '.webp'), 'WEBP', quality=82, method=6)
if os.path.exists(OUT):
    os.remove(OUT)
print("已输出:", OUT.replace('.png', '.webp'), round(os.path.getsize(OUT.replace('.png', '.webp')) / 1024), "KB")
