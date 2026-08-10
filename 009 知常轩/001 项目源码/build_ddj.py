# -*- coding: utf-8 -*-
"""
知常轩 · 道德经 80 章批量生产脚本
读取 道德经_结构化.json -> 生成 80 个单章 HTML（五段式：原文注音/译文/注音对照/儿童解读/想一想 + 音频）
用法: python build_ddj.py
"""
import json, os, re, io, sys
from pypinyin import pinyin, Style
from duoyin_fix import DUOYIN_FIX

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 009 知常轩/
SRC_JSON = os.path.join(BASE, '002 项目资源', '道德经', '结构化数据', '道德经_结构化_81章.json')
AUDIO_DIR = os.path.join(BASE, '002 项目资源', '道德经', '音频_81章')
OUT_DIR = os.path.join(BASE, '002 项目资源', '道德经', '页面_81章')

# ---------- 章题与标签映射（通行本章题，适配儿童理解） ----------
TITLES = {
 1:('众妙之门','全书总纲'), 2:('美恶相形','对立统一'), 3:('不尚贤','无为而治'),
 4:('道冲而用','虚怀若谷'), 5:('天地不仁','顺其自然'), 6:('谷神不死','道的永恒'),
 7:('天长地久','无私成私'), 8:('上善若水','处世智慧'), 9:('功遂身退','知足常乐'),
 10:('载营魄抱一','身心合一'), 11:('无之为用','空的作用'), 12:('五色令人目盲','物欲警醒'),
 13:('宠辱若惊','宠辱不惊'), 14:('视之不见','道不可名'), 15:('古之善为道者','谨慎深远'),
 16:('致虚守静','知常曰明'), 17:('太上不知有之','最好的治理'), 18:('大道废','仁义的出现'),
 19:('绝圣弃智','回归淳朴'), 20:('唯之与阿','特立独行'), 21:('孔德之容','德与道'),
 22:('曲则全','委曲求全'), 23:('希言自然','少说多做'), 24:('企者不立','戒骄戒躁'),
 25:('有物混成','道法自然'), 26:('重为轻根','稳重为本'), 27:('善行无辙','不露痕迹'),
 28:('知其雄','知雄守雌'), 29:('将欲取天下','不可强为'), 30:('以道佐人主','不好战'),
 31:('夫兵者','慎用武力'), 32:('道常无名','朴与名'), 33:('知人者智','认识自己'),
 34:('大道泛兮','道无处不在'), 35:('执大象','平淡是真'), 36:('将欲歙之','欲擒故纵'),
 37:('道恒无为','无为而无不为'), 38:('上德不德','德的高下'), 39:('昔之得一者','得一为贵'),
 40:('反者道之动','相反相成'), 41:('上士闻道','闻道三态'), 42:('道生一','万物生成'),
 43:('天下之至柔','柔弱胜刚强'), 44:('名与身孰亲','知足不辱'), 45:('大成若缺','大智若愚'),
 46:('天下有道','知足者富'), 47:('不出户','足不出户知天下'), 48:('为学日益','为道日损'),
 49:('圣人常无心','以百姓心为心'), 50:('出生入死','养生之道'), 51:('道生之德畜之','尊道贵德'),
 52:('天下有始','回归本源'), 53:('使我介然有知','大道与捷径'), 54:('善建者不拔','以身观身'),
 55:('含德之厚','赤子之心'), 56:('知者不言','大智若愚'), 57:('以正治国','无为而治'),
 58:('其政闷闷','宽厚为政'), 59:('治人事天','啬与积德'), 60:('治大国若烹小鲜','不乱折腾'),
 61:('大国者下流','谦下之道'), 62:('道者万物之奥','善人之宝'), 63:('为无为','大事从小做起'),
 64:('其安易持','千里之行始于足下'), 65:('古之善为道者','使民淳朴'), 66:('江海能为百谷王','谦下成王'),
 67:('天下皆谓我道大','我有三宝'), 68:('善为士者不武','不争之德'), 69:('用兵有言','哀兵必胜'),
 70:('吾言甚易知','知我者希'), 71:('知不知上','知道自己不知道'), 72:('民不畏威','自知自爱'),
 73:('勇于敢则杀','天道好还'), 74:('民不畏死','慎用刑罚'), 75:('民之饥','少生事端'),
 76:('人之生也柔弱','柔弱胜刚强'), 77:('天之道','损有余补不足'), 78:('天下莫柔弱于水','柔能克刚'),
 79:('和大怨','有德司契'), 80:('小邦寡民','理想社会'), 81:('信言不美','为而不争'),
}

# ---------- 生僻字注音表（字: 拼音） ----------
ZHUYIN = {
 '徼':'jiào', '玄':'xuán', '渊':'yuān', '尤':'yóu', '恶':'wù', '几':'jī', '持':'chí',
 '兆':'zhào', '泮':'pàn', '毂':'gǔ', '埏':'shān', '牖':'yǒu', '兕':'sì', '狎':'xiá',
 '挫':'cuò', '锐':'ruì', '忿':'fèn', '涤':'dí', '疵':'cī', '窈':'yǎo', '冥':'míng',
 '绳':'mǐn', '刍':'chú', '狗':'gǒu', '橐':'tuó', '龠':'yuè', '穷':'qióng', '牝':'pìn',
 '根':'gēn', '绵':'mián', '若':'ruò', '存':'cún', '呵':'hē', '唯':'wěi', '阿':'ē',
 '美':'měi', '恶':'è', '荒':'huāng', '兮':'xī', '昭':'zhāo', '察':'chá', '忽':'hū',
 '惚':'hū', '恍':'huǎng', '惚':'hū', '窈':'yǎo', '冥':'míng', '精':'jīng', '真':'zhēn',
 '窾':'kuǎn', '纪':'jì', '甫':'fǔ', '枉':'wǎng', '敝':'bì', '少':'shǎo', '多':'duō',
 '飘':'piāo', '骤':'zhòu', '企':'qǐ', '跨':'kuà', '跂':'qì', '赘':'zhuì', '混':'hùn',
 '寂':'jì', '寥':'liáo', '逝':'shì', '反':'fǎn', '輜':'zī', '重':'zhòng', '躁':'zào',
 '辎':'zī', '辙':'zhé', '谪':'zhé', '数':'shù', '筹':'chóu', '扃':'jiōng', '牖':'yǒu',
 '袭':'xí', '雄':'xióng', '雌':'cí', '溪':'xī', '忒':'tè', '朴':'pǔ', '歙':'xī',
 '张':'zhāng', '弱':'ruò', '废':'fèi', '兴':'xīng', '夺':'duó', '与':'yǔ', '柔':'róu',
 '刚':'gāng', '辐':'fú', '载':'zài', '营':'yíng', '魄':'pò', '专':'zhuān', '柔':'róu',
 '婴':'yīng', '涤':'dí', '览':'lǎn', '疵':'cī', '爱':'ài', '民':'mín', '国':'guó',
 '治':'zhì', '阗':'tián', '闷':'mèn', '旷':'kuàng', '混':'hùn', '浊':'zhuó', '静':'jìng',
 '清':'qīng', '安':'ān', '久':'jiǔ', '容':'róng', '公':'gōng', '全':'quán', '天':'tiān',
 '道':'dào', '久':'jiǔ', '没':'mò', '殆':'dài', '啬':'sè', '蚤':'zǎo', '服':'fú',
 '重':'zhòng', '积':'jī', '德':'dé', '克':'kè', '极':'jí', '母':'mǔ', '长':'cháng',
 '久':'jiǔ', '根':'gēn', '柢':'dǐ', '烹':'pēng', '鲜':'xiān', '莅':'lì', '鬼':'guǐ',
 '神':'shén', '伤':'shāng', '交':'jiāo', '归':'guī', '牝':'pìn', '静':'jìng', '下':'xià',
 '取':'qǔ', '奥':'ào', '宝':'bǎo', '市':'shì', '尊':'zūn', '拱':'gǒng', '璧':'bì',
 '驷':'sì', '坐':'zuò', '进':'jìn', '此':'cǐ', '道':'dào', '莫':'mò', '贵':'guì',
 '易':'yì', '持':'chí', '谋':'móu', '脆':'cuì', '泮':'pàn', '微':'wēi', '散':'sàn',
 '毫':'háo', '末':'mò', '累':'lěi', '土':'tǔ', '足':'zú', '下':'xià', '败':'bài',
 '失':'shī', '慎':'shèn', '终':'zhōng', '始':'shǐ', '愚':'yú', '智':'zhì', '朴':'pǔ',
 '谷':'gǔ', '王':'wáng', '江':'jiāng', '海':'hǎi', '百':'bǎi', '善':'shàn', '下':'xià',
 '慈':'cí', '俭':'jiǎn', '敢':'gǎn', '勇':'yǒng', '广':'guǎng', '器':'qì', '长':'zhǎng',
 '武':'wǔ', '怒':'nù', '敌':'dí', '与':'yǔ', '配':'pèi', '古':'gǔ', '哀':'āi',
 '胜':'shèng', '易':'yì', '行':'xíng', '宗':'zōng', '君':'jūn', '知':'zhī', '希':'xī',
 '病':'bìng', '威':'wēi', '狎':'xiá', '居':'jū', '厌':'yàn', '生':'shēng', '爱':'ài',
 '贵':'guì', '杀':'shā', '活':'huó', '利':'lì', '害':'hài', '恶':'wù', '孰':'shú',
 '故':'gù', '难':'nán', '知':'zhī', '强':'qiáng', '柔':'róu', '弱':'ruò', '处':'chǔ',
 '上':'shàng', '弓':'gōng', '高':'gāo', '抑':'yì', '下':'xià', '举':'jǔ', '损':'sǔn',
 '补':'bǔ', '怨':'yuàn', '德':'dé', '契':'qì', '司':'sī', '彻':'chè', '美':'měi',
 '信':'xìn', '辩':'biàn', '博':'bó', '知':'zhì', '积':'jī', '善':'shàn', '为':'wéi',
 '利':'lì', '害':'hài', '徒':'tú', '十':'shí', '有':'yǒu', '三':'sān', '生':'shēng',
 '死':'sǐ', '摄':'shè', '魄':'pò', '耄':'mào', '惔':'tán', '怛':'dá', '兕':'sì',
 '虎':'hǔ', '甲':'jiǎ', '兵':'bīng', '无':'wú', '所':'suǒ', '投':'tóu', '角':'jiǎo',
 '措':'cuò', '爪':'zhǎo', '伤':'shāng', '厚':'hòu', '赤':'chì', '子':'zǐ', '毒':'dú',
 '虫':'chóng', '螫':'shì', '攫':'jué', '鸟':'niǎo', '搏':'bó', '骨':'gǔ', '弱':'ruò',
 '朘':'juān',
 '筋':'jīn', '柔':'róu', '握':'wò', '牝':'pìn', '牡':'mǔ', '会':'huì', '精':'jīng',
 '至':'zhì', '和':'hé', '常':'cháng', '知':'zhī', '明':'míng', '益生':'yì shēng',
 '祥':'xiáng', '心':'xīn', '使':'shǐ', '气':'qì', '强':'qiáng', '壮':'zhuàng',
}

# 常用字表（不注音）
COMMON = set('的一是了我不人在他有这上们来到时大地为子中你说生国年着就那和要她出也得里后自以会家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开美总从无情己面最女但现前些所同日手又行意动方期它头经长儿回位分爱老因很给名法间斯知世什两次使身者被高已亲其进此话常与活正感')

def get_pinyin(ch, chapter=None):
    """多音字修正表优先，其次生僻字表，再查常用字表，最后 pypinyin"""
    if chapter and (chapter, ch) in DUOYIN_FIX:
        return DUOYIN_FIX[(chapter, ch)]
    if ch in ZHUYIN:
        return ZHUYIN[ch]
    if ch in COMMON:
        return None
    try:
        p = pinyin(ch, style=Style.TONE)[0][0]
        return p
    except Exception:
        return None

def add_ruby(text, chapter=None):
    """正文注音已废弃：直接返回原文（不注音），注音对照由 gloss 部分承担"""
    return text

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第{cn}章 {title} · 道德经 · 知常轩</title>
<style>
  :root {{
    --xuan-qing: #1C1C2E; --xiang-huang: #E8C547; --jiang-chi: #C73E3A;
    --cui-qing: #2D6A4F; --shuang-bai: #F5F0E8; --yue-bai: #E8EEF2;
    --mo-hei: #1A1A1A; --qing-ci: #7BA3A8;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--shuang-bai); color: var(--mo-hei); font-family: "Songti SC","SimSun","Noto Serif CJK SC",serif; line-height: 1.9; }}
  .top-band {{ background: var(--xuan-qing); color: var(--xiang-huang); text-align: center; padding: 26px 16px 20px; position: relative; overflow: hidden; }}
  .top-band::before, .top-band::after {{ content: "☰☰☰☰☰☰☰☰☰☰"; position: absolute; left: 0; right: 0; color: rgba(232,197,71,0.18); letter-spacing: 6px; font-size: 12px; }}
  .top-band::before {{ top: 8px; }} .top-band::after {{ bottom: 8px; }}
  .top-band h1 {{ font-size: 26px; letter-spacing: 12px; }}
  .top-band p {{ font-size: 13px; letter-spacing: 4px; margin-top: 6px; color: var(--yue-bai); opacity: .8; }}
  .back-home {{ display: inline-block; margin-top: 10px; font-size: 12px; letter-spacing: 2px; color: var(--xiang-huang); border: 1px solid rgba(232,197,71,.5); border-radius: 14px; padding: 3px 14px; text-decoration: none; }}
  .back-home:hover {{ background: var(--xiang-huang); color: var(--xuan-qing); }}
  .container {{ max-width: 860px; margin: 0 auto; padding: 30px 20px 50px; }}
  .chapter {{ background: #fff; border: 1px solid #e5ddd0; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 12px rgba(28,28,46,.06); }}
  .chapter-head {{ background: linear-gradient(135deg, var(--xuan-qing), #2c2c44); color: var(--shuang-bai); padding: 18px 24px; display: flex; align-items: baseline; gap: 16px; }}
  .chapter-num {{ font-size: 30px; font-weight: 700; color: var(--xiang-huang); letter-spacing: 2px; }}
  .chapter-title {{ font-size: 19px; letter-spacing: 4px; }}
  .chapter-tag {{ margin-left: auto; font-size: 12px; background: var(--cui-qing); color: #fff; padding: 3px 10px; border-radius: 12px; letter-spacing: 1px; }}
  .chapter-body {{ padding: 24px 28px 28px; }}
  .section-label {{ font-size: 13px; color: var(--jiang-chi); letter-spacing: 6px; font-weight: 700; margin: 18px 0 10px; padding-left: 10px; border-left: 3px solid var(--jiang-chi); }}
  .section-label:first-child {{ margin-top: 0; }}
  .original {{ font-size: 20px; line-height: 2.2; letter-spacing: 2px; text-align: justify; color: #222; }}
  .translation {{ font-size: 16px; color: #444; background: var(--yue-bai); border-radius: 4px; padding: 14px 18px; line-height: 2; }}
  .gloss {{ display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 14px; color: #555; }}
  .gloss span b {{ color: var(--cui-qing); font-weight: 700; margin-right: 3px; }}
  .kid-talk {{ background: #fdf9ef; border: 1px dashed var(--xiang-huang); border-radius: 6px; padding: 16px 20px; font-size: 16px; color: #333; }}
  .kid-talk .lead {{ color: var(--jiang-chi); font-weight: 700; margin-bottom: 6px; letter-spacing: 2px; }}
  .think {{ background: var(--xuan-qing); color: var(--shuang-bai); border-radius: 6px; padding: 14px 20px; margin-top: 14px; display: flex; gap: 12px; align-items: flex-start; }}
  .think .icon {{ font-size: 20px; color: var(--xiang-huang); flex-shrink: 0; }}
  .think p {{ font-size: 15px; line-height: 1.8; }}
  .audio-row {{ margin-top: 14px; display: flex; align-items: center; gap: 10px; }}
  .audio-row audio {{ height: 36px; flex: 1; }}
  .audio-label {{ font-size: 12px; color: var(--qing-ci); letter-spacing: 1px; white-space: nowrap; }}
  .nav-row {{ display: flex; justify-content: space-between; margin: 18px 0 8px; font-size: 14px; }}
  .nav-row a {{ color: var(--cui-qing); text-decoration: none; }}
  .nav-row a:hover {{ text-decoration: underline; }}
  footer {{ text-align: center; color: #999; font-size: 12px; letter-spacing: 3px; padding: 20px 0 40px; border-top: 1px solid #e0d8c8; margin-top: 10px; }}
  .foot-note {{ font-size: 12px; color: #aaa; margin-top: 6px; letter-spacing: 1px; }}
</style>
</head>
<body>

<div class="top-band">
  <h1>道德经</h1>
  <p>知常轩 · 儒与道 · 儿童精读系列</p>
  <a class="back-home" href="../../" target="_top">← 返回知常轩主站</a>
</div>

<div class="container">

  <div class="nav-row">
    <a href="{prev_link}">← 上一章</a>
    <a href="00_目录.html">目录</a>
    <a href="{next_link}">下一章 →</a>
  </div>

  <div class="chapter">
    <div class="chapter-head">
      <span class="chapter-num">第{cn}章</span>
      <span class="chapter-title">{title}</span>
      <span class="chapter-tag">{tag}</span>
    </div>
    <div class="chapter-body">

      <div class="section-label">原文</div>
      <div class="original">
{original_html}
      </div>

      <div class="section-label">译文</div>
      <div class="translation">
{translation}
      </div>

      <div class="section-label">注音对照</div>
      <div class="gloss">
{gloss_html}
      </div>

      <div class="section-label">给孩子的解读</div>
      <div class="kid-talk">
        <p class="lead">{lead}</p>
        <p>{kid_talk}</p>
      </div>

      <div class="think">
        <span class="icon">问</span>
        <p><b>想一想：</b>{think}</p>
      </div>

      <div class="section-label">听一听</div>
      <div class="audio-row">
        <span class="audio-label">原文朗读</span>
        <audio controls src="音频_81章/{audio_file}"></audio>
      </div>

    </div>
  </div>

  <div class="nav-row">
    <a href="{prev_link}">← 上一章</a>
    <a href="00_目录.html">目录</a>
    <a href="{next_link}">下一章 →</a>
  </div>

  <footer>
    知常轩 · 公益教育平台
    <div class="foot-note">底本说明：原文据帛书本（用"恒"字），译文为白话对照。仅供学习参考。</div>
  </footer>

</div>
</body>
</html>
"""

def cn_to_num(s):
    """中文数字转阿拉伯数字，如 一->1, 十->10, 六十四->64；兼收阿拉伯数字字符串"""
    s = str(s).strip()
    if s.isascii() and s.isdigit():
        return int(s)
    cn = '零一二三四五六七八九'
    if s == '十':
        return 10
    if len(s) == 1:
        return cn.index(s)
    if s.startswith('十'):
        return 10 + (cn.index(s[1]) if len(s) > 1 else 0)
    if s.endswith('十'):
        return cn.index(s[0]) * 10
    return cn.index(s[0]) * 10 + cn.index(s[1])

def num_to_cn(n):
    cn = '零一二三四五六七八九'
    if n <= 10: return ('十' if n == 10 else cn[n])
    if n < 20: return '十' + cn[n-10]
    if n < 100: return cn[n//10] + '十' + (cn[n%10] if n%10 else '')
    return cn[n//10] + '十' + (cn[n%10] if n%10 else '')

def main():
    with io.open(SRC_JSON, encoding='utf-8') as f:
        data = json.load(f)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 加载儿童解读内容
    CONTENT_DIR = os.path.join(BASE, '002 项目资源', '道德经', '结构化数据')
    kid_content = {}
    for fn in ['解读内容_1_27.json', '解读内容_28_54.json', '解读内容_55_81.json']:
        fp = os.path.join(CONTENT_DIR, fn)
        if os.path.exists(fp):
            with io.open(fp, encoding='utf-8') as f:
                kid_content.update(json.load(f))
    print('已加载解读内容章数:', len(kid_content))

    # 预扫描每章生僻字，生成注音对照
    gloss_all = {}
    for d in data:
        ch = cn_to_num(d['chapter'])
        orig = d['original']
        seen = {}
        for c in orig:
            if not ('\u4e00' <= c <= '\u9fff'):
                continue
            p = get_pinyin(c, ch)
            if p and c not in seen:
                seen[c] = p
        gloss_all[ch] = seen

    for i, d in enumerate(data):
        ch_raw = d['chapter']
        ch = cn_to_num(ch_raw)
        title, tag = TITLES.get(ch, ('', ''))
        orig = d['original']
        trans = d['translation']
        cn = num_to_cn(ch)

        # 原文分行（按标点断句）
        orig_lines = re.split(r'(?<=[。；！？])', orig)
        orig_lines = [l.strip() for l in orig_lines if l.strip()]
        original_html = '<br>\n'.join(add_ruby(l, ch) for l in orig_lines)

        # 注音对照
        gloss_items = gloss_all.get(ch, {})
        gloss_html = '\n'.join(
            f'        <span><b>{c}</b>{p}</span>' for c, p in gloss_items.items()
        ) if gloss_items else '        <span>本篇生僻字较少，无需注音</span>'

        # 解读（来自内容库，未写的用占位）
        kc = kid_content.get(str(ch), {})
        lead = kc.get('lead', f'这一章，老子在讲「{title}」')
        kid_talk = kc.get('kid_talk', '（解读内容待补充）')
        think = kc.get('think', '读一读这一章，说说你的感受。')

        audio_file = f'{ch:02d}章.mp3'
        prev_link = f'{ch-1:02d}章.html' if ch > 1 else '00_目录.html'
        next_link = f'{ch+1:02d}章.html' if ch < 81 else '00_目录.html'

        html = TEMPLATE.format(
            cn=cn, title=title, tag=tag, original_html=original_html,
            translation=trans, gloss_html=gloss_html, lead=lead,
            kid_talk=kid_talk, think=think, audio_file=audio_file,
            prev_link=prev_link, next_link=next_link,
        )
        with io.open(os.path.join(OUT_DIR, f'{ch:02d}章.html'), 'w', encoding='utf-8') as f:
            f.write(html)

    print(f'生成完成: {len(data)} 章 -> {OUT_DIR}')

if __name__ == '__main__':
    main()
