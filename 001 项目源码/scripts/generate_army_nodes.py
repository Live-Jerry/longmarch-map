#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成包含四支军队的完整 node_data.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# =============================================================================
# 读取现有节点数据
# =============================================================================
json_path = config.NODE_DATA_JSON
with open(json_path, "r", encoding="utf-8") as f:
    existing_nodes = json.load(f)

print(f"现有节点数: {len(existing_nodes)}")

# =============================================================================
# 给现有节点添加 army 字段
# =============================================================================
for node in existing_nodes:
    # 根据 node_id 判断归属
    node_id = node["node_id"]
    if node_id in ("14.1", "14.2"):
        # 会宁和将台堡是多军会师节点
        node["army"] = "中央红军"
    else:
        node["army"] = "中央红军"

# =============================================================================
# 红二方面军节点（E1.1 ~ E7.2）
# =============================================================================

red2_nodes = [
    {
        "node_id": "E1.1",
        "title": "湖南桑植",
        "location": "湖南桑植",
        "lat": 29.4,
        "lng": 110.17,
        "time": "1935年11月19日",
        "army": "红二方面军",
        "core_numbers": "红二方面军（红2军团、红6军团）",
        "famous_battle": "无。桑植为红二方面军长征出发地，红军主动撤离根据地开始长征。",
        "important_meeting": "无",
        "history_event": "红二、红六军团长征出发地。1935年11月19日，贺龙、任弼时、关向应、萧克、王震等率领红2、红6军团共1.7万余人，从桑植刘家坪出发开始长征。桑植是湘鄂川黔革命根据地的中心区域，贺龙元帅的故乡。出发前部队进行了整编，留下红18师坚持根据地斗争。",
        "core_site": "桑植县刘家坪红二方面军长征出发地纪念碑、中国工农红军第二方面军长征纪念馆、贺龙故居和纪念馆",
        "poem_article": "无",
        "typical_story": "桑植出发时，许多战士是贺龙家乡的子弟兵。一位母亲送儿子参军时说：「跟着贺胡子走，没错！」出发那天，桑植百姓万人空巷送别红军。贺龙面对乡亲们说：「我们一定还会回来的！」",
        "typical_people": "贺龙：红二方面军总指挥，从桑植出发长征。任弼时：红二方面军政委。关向应：红二方面军副政委。萧克：红6军团军团长。王震：红6军团政委。",
        "historical_significance": "桑植是红二方面军长征的起点，也是贺龙等革命家战斗过的故乡。红二、红六军团的长征是三大主力长征的重要组成部分，历时11个月转战9省行程两万余里。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E2.1",
        "title": "贵州石阡",
        "location": "贵州石阡",
        "lat": 27.52,
        "lng": 108.23,
        "time": "1936年1月",
        "army": "红二方面军",
        "core_numbers": "红二方面军（红2军团、红6军团）",
        "famous_battle": "突破乌江（1936年1月）。红二、红六军团在贵州石阡地区突破乌江天险，进入黔西地区。此前红6军团曾在石阡地区与敌军激战，完成策应中央红军长征的任务。",
        "important_meeting": "石阡会议（1936年1月）。决定继续西进，创建川滇黔边根据地。",
        "history_event": "红二、红六军团从桑植出发后突破敌军封锁线，1936年1月进入贵州石阡地区。在石阡短暂休整后继续西进。石阡是红6军团1934年西征时艰苦战斗过的地方，当年红6军团在甘溪遭遇强敌，部队遭受重大损失。",
        "core_site": "石阡红军长征纪念馆、甘溪红军烈士纪念碑、困牛山红军战斗遗址",
        "poem_article": "无",
        "typical_story": "「困牛山壮举」——1934年红6军团西征途经石阡困牛山时遭敌军包围。100余名红军战士宁死不屈，集体跳下悬崖壮烈牺牲。1976年当地农民在悬崖下发现红军遗骨，烈士的英灵才得以安息。",
        "typical_people": "贺龙：率红2军团突破乌江。任弼时：主持召开石阡会议。萧克：1934年率红6军团在石阡苦战。",
        "historical_significance": "石阡是红二、红六军团西征进入贵州的第一站。突破乌江后红军进入黔西地区，为创建川滇黔边根据地创造了条件。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E3.1",
        "title": "贵州黔西（大定/毕节）",
        "location": "贵州黔西（大定/毕节）",
        "lat": 27.3,
        "lng": 105.3,
        "time": "1936年2月",
        "army": "红二方面军",
        "core_numbers": "红二方面军（红2军团、红6军团）",
        "famous_battle": "乌蒙山回旋战（1936年2月—3月）。贺龙指挥红二、红六军团在乌蒙山区与国民党军10万兵力周旋一个多月。红军在大山中来回穿插以少打多，最终跳出包围圈。",
        "important_meeting": "黔西会议（1936年2月）。决定建立川滇黔边革命根据地。创建中华苏维埃人民共和国川滇黔省革命委员会。",
        "history_event": "红二、红六军团突破乌江后占领黔西、大定（今大方）、毕节地区，创建了长征中唯一一块革命根据地——川滇黔边根据地。红军在黔大毕地区扩红5000余人，建立各级革命政权和抗日救国会。一个月后因敌军重兵围攻主动撤离。",
        "core_site": "毕节市黔西县革命遗址、中华苏维埃川滇黔省革命委员会旧址（大方）、毕节市红军长征纪念馆",
        "poem_article": "无",
        "typical_story": "在黔大毕地区红二、红六军团严格执行民族政策，纪律严明受到各族群众拥护。当地苗族、彝族群众主动为红军带路、送粮。仅一个月扩红5000余人，补充了大量兵员和物资。许多贫苦青年踊跃参军，「当红军去」成为当地最响亮的口号。",
        "typical_people": "贺龙：指挥乌蒙山回旋战。任弼时：黔西会议上主持创建根据地。萧克、王震：率部在黔大毕地区做群众工作。",
        "historical_significance": "黔大毕根据地是红二、红六军团长征中创建的唯一一块根据地。乌蒙山回旋战是贺龙军事指挥艺术的杰作，与四渡赤水、巧渡金沙江齐名。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E4.1",
        "title": "云南盘县",
        "location": "云南盘县",
        "lat": 25.63,
        "lng": 104.63,
        "time": "1936年3月30日",
        "army": "红二方面军",
        "core_numbers": "红二方面军（红2军团、红6军团）",
        "famous_battle": "无",
        "important_meeting": "盘县会议（1936年3月30日）。红二、红六军团在盘县召开会议，讨论红军总部要求北上与红四方面军会合的电令。会议决定放弃在南北盘江建立根据地的计划，北上甘孜与红四方面军会师。这是红二方面军长征中的重要转折点。",
        "history_event": "红二、红六军团乌蒙山回旋战后进入云南盘县。原计划在南北盘江建立根据地，但接到朱德、张国焘以红军总部名义发来的北上电令。盘县会议上经过讨论决定服从总部命令北上。会后红军主动撤离盘县，兵分两路向滇中挺进。",
        "core_site": "盘县会议会址（贵州盘县）、红军长征过盘县纪念馆",
        "poem_article": "无",
        "typical_story": "盘县会议上争论激烈。一部分人认为应在南北盘江建立根据地休整，另一部分人主张北上。最终贺龙、任弼时决定服从红军总部的命令北上。这一决策使红二、红六军团最终实现了与兄弟部队的会师，走上了与中央红军会合的正确道路。",
        "typical_people": "贺龙：盘县会议后率部北上。任弼时：赞成北上与四方面军会合。",
        "historical_significance": "盘县会议是红二方面军长征方向的重要转折。放弃在盘江建立根据地的计划北上会师，使红二方面军最终实现了与兄弟部队的会合、完成了长征。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E5.1",
        "title": "云南中甸",
        "location": "云南中甸",
        "lat": 27.82,
        "lng": 99.7,
        "time": "1936年4月",
        "army": "红二方面军",
        "core_numbers": "红二方面军（红2军团、红6军团）",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "红二、红六军团从盘县地区北上，分两路挺进云南。贺龙率红2军团经滇中北上，萧克、王震率红6军团经滇西北进。1936年4月底进入云南中甸（今香格里拉）藏区。红军严格执行党的民族宗教政策，尊重藏族群众的风俗习惯和宗教信仰，赢得了藏族同胞的信任和支持。",
        "core_site": "中甸红军长征纪念馆、香格里拉红军长征遗址、归化寺",
        "poem_article": "无",
        "typical_story": "红军到达中甸藏区时严格执行纪律。贺龙亲自到归化寺拜访活佛，赠送「兴盛番族」锦幛。红军向藏族群众宣传革命道理，买卖公平。藏族同胞从最初的害怕、躲避转变为欢迎、支援红军，为红军筹集粮食和物资。",
        "typical_people": "贺龙：到归化寺拜访活佛，赠送锦幛。归化寺活佛：接受红军政策，帮助红军筹集粮草。",
        "historical_significance": "中甸是红二方面军进入藏区的第一站。红军在藏区的民族宗教政策实践，为后续长征部队进入藏区积累了宝贵经验。红二方面军成为唯一同时经过云南、四川藏区的长征部队。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E5.2",
        "title": "四川甘孜",
        "location": "四川甘孜",
        "lat": 31.62,
        "lng": 100.0,
        "time": "1936年6月",
        "army": "红二方面军",
        "core_numbers": "红二方面军、红四方面军",
        "famous_battle": "无",
        "important_meeting": "甘孜会议（1936年6月）。红二、红六军团与红四方面军举行会师大会。朱德、任弼时、贺龙、张国焘等出席。会上朱德提出要团结一致北上抗日。任弼时、贺龙等坚决支持党中央北上方针。",
        "history_event": "1936年6月，红二、红六军团到达四川甘孜地区，与红四方面军胜利会师。两军将士在经历了各自的艰难转战后终于相聚，情绪十分激动。7月2日举行了隆重的会师大会。按照中央指令，红二、红六军团和红32军合编组成中国工农红军第二方面军，贺龙任总指挥，任弼时任政委。",
        "core_site": "甘孜红军会师遗址、甘孜县朱德总司令和五世格达活佛纪念馆",
        "poem_article": "无",
        "typical_story": "红二方面军到达甘孜时已极度疲惫。红四方面军指战员把自己的粮食、衣物送给远道而来的战友。红二方面军总指挥贺龙看到四方面军战友送来的物资时动情地说：「天下红军是一家！」甘孜会师中朱德和五世格达活佛建立了深厚友谊，成为民族团结的佳话。",
        "typical_people": "贺龙：红二方面军总指挥。朱德：红四方面军领导人（被张国焘挟持期间）。任弼时：坚决支持党中央北上方针。张国焘：此时在各方面压力下被迫同意北上。",
        "historical_significance": "甘孜会师是红二、红四方面军长征中的重要里程碑。在朱德、任弼时、贺龙等人的努力下，红四方面军最终放弃了南下方针走上北上正确道路。红二方面军的正式成立标志着三大主力红军建制的基本完备。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "important_meeting", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E6.1",
        "title": "四川阿坝",
        "location": "四川阿坝",
        "lat": 32.9,
        "lng": 101.7,
        "time": "1936年7月",
        "army": "红二方面军",
        "core_numbers": "红二方面军",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "甘孜会师后红二、红四方面军共同北上。红二方面军从甘孜出发向北行进，进入阿坝地区。这里地处高原平均海拔3500米以上，7月虽是夏季但天气仍然寒冷。部队穿越荒原和沼泽地带，断粮情况严重。战士们不得不以野菜、草根充饥。这是红二方面军长征中最艰苦的一段路程。",
        "core_site": "阿坝红军长征纪念馆、红二方面军北上途经地遗址群",
        "poem_article": "无",
        "typical_story": "过草地时红二方面军同样遭遇了中央红军过草地时的困难。断粮的战士们吃野菜、草根、树皮，甚至把牛皮腰带煮着吃。许多战士因饥饿和疾病倒在草地上。一位老红军回忆：「每天出发时一个班的人，到傍晚宿营时就少了好几个。」",
        "typical_people": "贺龙：率红二方面军过草地，把自己的马让给伤兵骑。全体红二方面军将士：以顽强意志穿越草地。",
        "historical_significance": "阿坝是红二方面军过草地的关键地段。红二方面军以巨大牺牲穿越草地北上，打破了张国焘试图把他们留在南方的企图。过草地是红二方面军长征中最艰苦的考验。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E6.2",
        "title": "甘肃岷县（哈达铺）",
        "location": "甘肃岷县（哈达铺）",
        "lat": 34.4,
        "lng": 104.0,
        "time": "1936年8月",
        "army": "红二方面军",
        "core_numbers": "红二方面军",
        "famous_battle": "岷洮西战役（1936年8月）。红二、红四方面军进入甘肃后发起岷洮西战役，攻克岷县、洮州、西固等地。红二方面军与敌人激战多日，打开了进入甘肃的通路。",
        "important_meeting": "无",
        "history_event": "红二方面军过草地后进入甘肃南部。1936年8月到达岷县哈达铺地区。哈达铺是中央红军1935年到达过的地方，这里物资丰富使补给得到改善。红二方面军在此休整、筹粮。随即奉命东进向陕甘宁边区挺进。",
        "core_site": "哈达铺红军长征纪念馆（红二方面军陈列）、岷县红军长征旧址",
        "poem_article": "无",
        "typical_story": "到达哈达铺时红二方面军指战员已衣衫褴褛、面黄肌瘦。当地百姓看到红军如此艰苦十分感动，纷纷拿出粮食、衣物支援。一位老乡说：「去年过去的那些红军（中央红军）也是这个样子，你们都是好人呐！」",
        "typical_people": "贺龙：率红二方面军进入甘肃。全体红二方面军将士：从1.7万人出发到此时已减员过半。",
        "historical_significance": "进入甘肃是红二方面军长征从艰苦跋涉转向胜利在望的转折。哈达铺的补给使极度疲惫的红二方面军得到了喘息和恢复。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E7.1",
        "title": "甘肃会宁",
        "location": "甘肃会宁",
        "lat": 35.6937,
        "lng": 105.0523,
        "time": "1936年10月",
        "army": "红二方面军",
        "core_numbers": "红一、红二、红四方面军",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "1936年10月，红二方面军到达甘肃会宁，与红一、红四方面军胜利会师。三大主力红军终于汇合。会宁城红旗招展、锣鼓喧天。红二方面军指战员与兄弟们激动相拥，许多人热泪盈眶。至此，红二方面军历时11个月、转战9省的长征胜利结束。",
        "core_site": "会宁县红军长征会师旧址（含会师楼、会师纪念塔、会师纪念馆）、三军会师广场",
        "poem_article": "无",
        "typical_story": "会宁会师时红二方面军许多战士已衣不蔽体。红一方面军的战友们将自己的军装、鞋帽分给他们。会师大会上三军将士齐声欢呼，红旗如海歌声如潮。贺龙在大会上说：「我们终于到家了！」",
        "typical_people": "贺龙：红二方面军总指挥。任弼时：红二方面军政委。萧克、王震：率部参加会师。",
        "historical_significance": "会宁会师是红二方面军长征的终点。红二方面军从桑植出发1.7万人到会师时仅剩约7000余人，但保存了红2、红6军团的骨干力量，为后来的抗日战争和解放战争做出了重大贡献。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "E7.2",
        "title": "宁夏将台堡",
        "location": "宁夏西吉（将台堡）",
        "lat": 35.82,
        "lng": 105.87,
        "time": "1936年10月22日",
        "army": "红二方面军",
        "core_numbers": "红二方面军、红一方面军",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "将台堡会师（1936年10月22日）。红二方面军与红一方面军在宁夏西吉将台堡胜利会师。这是红军三大主力长征中的最后一次会师，标志着红二方面军长征的最终完成。将台堡会师纪念碑由江泽民题写碑名。1996年将台堡被列为全国重点文物保护单位。",
        "core_site": "将台堡红军会师纪念碑（宁夏西吉）、红军会师纪念馆",
        "poem_article": "毛泽东在长征结束后总结：「长征是宣言书，长征是宣传队，长征是播种机。」",
        "typical_story": "将台堡会师时红二方面军的许多战士赤脚行军，衣衫褴褛。红一方面军战友将自己的衣服鞋帽送给他们。红二方面军从出发时1.7万人到会师时仅剩约7000人。会师当天当地百姓载歌载舞欢迎红军，杀猪宰羊慰劳将士。",
        "typical_people": "贺龙：红二方面军总指挥。任弼时：红二方面军政委。关向应：红二方面军副政委。左权：红一方面军代表。",
        "historical_significance": "将台堡会师是红二方面军长征的收官之战，也是三大主力红军的最后一次会师。至此红一、红二、红四方面军全部完成长征，中国革命力量实现了空前的大团结。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "poem_article", "typical_story", "typical_people"
        ]
    }
]

# =============================================================================
# 红四方面军节点（S1.1 ~ S8.2）
# =============================================================================

red4_nodes = [
    {
        "node_id": "S1.1",
        "title": "四川苍溪（强渡嘉陵江）",
        "location": "四川苍溪",
        "lat": 31.73,
        "lng": 105.93,
        "time": "1935年3月28日",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "嘉陵江战役（1935年3月28日—4月21日）。红四方面军集中主力在苍溪至阆中200里江面上强渡嘉陵江，歼敌1万余人，攻占9座县城。这是红四方面军开始长征的标志性战役，也是长征开始前大兵团强渡江河的经典战例。",
        "important_meeting": "无",
        "history_event": "1935年3月28日，红四方面军总指挥徐向前指挥渡江作战。红军在苍溪塔山湾、阆中涧溪口等地分三路强渡嘉陵江。渡江后攻克剑门关，控制了嘉陵江以西大片地区。此后红四方面军开始长征，向西向北挺进。",
        "core_site": "苍溪红军渡纪念馆、苍溪红军强渡嘉陵江纪念碑、塔山湾渡口遗址、剑门关战斗遗址",
        "poem_article": "无",
        "typical_story": "强渡嘉陵江时，红军造船工人在短短一个月内秘密造出100多只木船和3座竹筏浮桥。渡江当晚70多岁的老船工主动要求为红军摆渡。第一批突击队员在火力掩护下冲向对岸，后续部队通过浮桥冲过江面。",
        "typical_people": "徐向前：红四方面军总指挥，指挥嘉陵江战役。王树声：红四方面军副总指挥，率部争夺剑门关。李先念：红30军政委，率部担任主攻方向。",
        "historical_significance": "强渡嘉陵江是红四方面军长征的开端。嘉陵江战役的胜利使红四方面军摆脱了川陕根据地的困境，开始了战略转移。此役也是红军战史上大规模强渡江河的经典战例。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S2.1",
        "title": "四川茂县",
        "location": "四川茂县",
        "lat": 31.68,
        "lng": 103.85,
        "time": "1935年5月",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "土门战役（1935年5月）。红四方面军为打通进占岷江流域的通道，在茂县土门地区与川军展开激战。红军攻占土门后打开了进入川西的通道，占领了茂县、理县、汶川等大片地区。",
        "important_meeting": "无",
        "history_event": "红四方面军强渡嘉陵江后向川西北挺进。1935年5月，红军在茂县土门地区与川军激战，攻占土门要隘后占领茂县县城。茂县是进入岷江上游的咽喉。红军占领茂县后控制了岷江以西大片区域，建立临时后方基地。红四方面军总部设于茂县。",
        "core_site": "茂县红军长征纪念馆、土门战役遗址、茂县红军桥",
        "poem_article": "无",
        "typical_story": "红军占领茂县后严格执行党的民族政策。红四方面军发布了《红军对番民十大约法》布告，尊重羌族、藏族群众风俗习惯。当地羌族群众从开始躲避转变为给红军送粮带路。一位羌族老人说：「从没见过对百姓这么好的军队。」",
        "typical_people": "徐向前：指挥土门战役占领茂县。张国焘：红四方面军主要负责人。",
        "historical_significance": "茂县是红四方面军向川西北进军的关键节点。攻占茂县使红四方面军控制了岷江上游，为迎接中央红军北上和懋功会师创造了条件。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S3.1",
        "title": "四川懋功（达维）",
        "location": "四川小金（懋功/达维）",
        "lat": 31.0,
        "lng": 102.4,
        "time": "1935年6月18日",
        "army": "红四方面军",
        "core_numbers": "红一方面军、红四方面军",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "懋功会师（1935年6月18日）。徐向前率红四方面军先头部队在达维桥与中央红军胜利会师。红四方面军从川陕根据地出发，转战数千里到达川西，终于与中央红军会合。两军将士欢呼拥抱，热泪盈眶。红四方面军为中央红军准备了大量粮食、衣物和弹药。",
        "core_site": "达维会师纪念碑、小金县红军会师广场、懋功会师遗址",
        "poem_article": "无",
        "typical_story": "红四方面军得知中央红军到来的消息后，全军振奋。徐向前亲自布置迎接工作，指示「要热情周到，把最好的东西送给兄弟部队」。红四方面军将士把自己珍贵的粮食、盐巴、衣物、子弹分给衣衫褴褛的中央红军战友。当两军先头部队在达维桥相遇时，欢呼声响彻山谷。",
        "typical_people": "徐向前：红四方面军总指挥，安排迎接中央红军。李先念：率部迎接中央红军。张国焘：红四方面军主要负责人。",
        "historical_significance": "懋功会师是红军两大主力的历史性会合。两支大军汇合使红军力量从不足3万人猛增至10万余人。会师增强了革命力量，但也暴露了张国焘与中央之间的路线分歧。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S4.1",
        "title": "四川两河口",
        "location": "四川小金（两河口镇）",
        "lat": 31.2,
        "lng": 102.5,
        "time": "1935年6月26日",
        "army": "红四方面军",
        "core_numbers": "红一方面军、红四方面军",
        "famous_battle": "无",
        "important_meeting": "两河口会议（1935年6月26日）。懋功会师后中共中央在两河口召开政治局扩大会议，确定北上建立川陕甘根据地的战略方针。会上毛泽东与张国焘就北上还是南下发生激烈争论。张国焘以红四方面军人数占优为由主张南下川康。最终会议通过北上决议。",
        "history_event": "两河口会议在关帝庙内召开。毛泽东、周恩来等坚持北上，张国焘主张南下。会议虽然通过了北上决议，但张国焘心有不甘。这是懋功会师后中央与张国焘第一次正面交锋，为后来张国焘的分裂行为埋下伏笔。",
        "core_site": "两河口会议会址（小金县两河口镇关帝庙）、两河口会议纪念馆",
        "poem_article": "无",
        "typical_story": "两河口会议上张国焘以其红四方面军兵力众多为由要求改组中央。毛泽东、周恩来等耐心做团结工作。会上争论异常激烈，张国焘甚至以「不干了」相威胁。会议最终还是通过了北上方针。毛泽东后来回忆：「那是最困难的一段时期。」",
        "typical_people": "张国焘：两河口会议上坚持南下主张。毛泽东：力主北上方针。周恩来：在两军之间做团结工作。徐向前：执行北上方针但理解张国焘的顾虑。",
        "historical_significance": "两河口会议是懋功会师后中央与红四方面军第一次战略方针之争。会议确定的北上方针是长征最终胜利的战略保障。张国焘的两面态度为后面的分裂行为埋下了伏笔。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "important_meeting", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S5.1",
        "title": "四川卓克基",
        "location": "四川马尔康（卓克基）",
        "lat": 31.9,
        "lng": 102.2,
        "time": "1935年7月",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "翻越雪山——红四方面军从茂县、理县地区翻越多座雪山向卓克基、马尔康方向前进。红四方面军翻越了虹桥山、梦笔山、长板山等多座海拔4000米以上的雪山。连续翻越雪山使部队极度疲惫，许多战士因高原反应和严寒牺牲。在卓克基土司官寨进行了休整和筹粮。",
        "core_site": "卓克基土司官寨、马尔康红军长征纪念馆、雪山红军小道",
        "poem_article": "无",
        "typical_story": "红四方面军翻越夹金山、虹桥山等雪山时同样经历了中央红军的艰难。许多战士是南方人从未见过雪，穿着单衣草鞋在冰雪中行进。一名红四方面军老战士回忆：「冻掉手指脚趾的人很多，但没有人后退一步。」在卓克基土司官寨，中央和红军总部曾在此驻扎。",
        "typical_people": "徐向前：率红四方面军翻越雪山。全体红四方面军将士：以顽强意志翻越多座雪山。",
        "historical_significance": "卓克基是红四方面军翻越雪山后的重要休整地。红军在雪山的经历证明这支军队具有战胜任何困难的意志力。卓克基土司官寨也是毛泽东、周恩来等中央领导人的驻地。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S6.1",
        "title": "四川阿坝",
        "location": "四川阿坝",
        "lat": 32.9,
        "lng": 101.7,
        "time": "1935年8月",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "包座战役（1935年8月29日—31日）。红四方面军第30军在包座地区歼灭国民党军胡宗南部第49师5000余人。这是红一、红四方面军会师后第一次重大胜利，为红军北上打开了通道。",
        "important_meeting": "阿坝会议（1935年9月）。张国焘率左路军到达阿坝后召开会议，公开反对中央北上方针，提出南下川康的另立主张。这是张国焘分裂主义公开化的标志。",
        "history_event": "毛儿盖会议后红军分左右两路军北上。张国焘率左路军（红四方面军主力及红一方面军第5、第32军）到达阿坝后拒绝执行北上命令。他以噶曲河涨水为由停止北上，随后召开阿坝会议公开反对中央。张国焘在阿坝宣布成立「临时中央」，走上了分裂党和红军的道路。",
        "core_site": "阿坝红军长征纪念馆、包座战役遗址、阿坝会议遗址",
        "poem_article": "无",
        "typical_story": "张国焘在阿坝拒不北上。朱德、刘伯承等坚持党中央的北上方针。朱德在阿坝会议上正气凛然地说：「中央的北上决定是正确的，我拥护中央！」张国焘的人马举枪威胁，朱德从容不迫：「你们可以把我劈成两半，但绝对割不断我和党的关系！」",
        "typical_people": "张国焘：在阿坝公开分裂党和红军。朱德：在阿坝会议上坚持党的立场。刘伯承：随左路军行动，支持朱德。徐向前：身处左路军处境艰难。",
        "historical_significance": "阿坝是张国焘分裂主义公开化的核心地点。阿坝会议标志着张国焘与党中央的公开决裂。朱德、刘伯承等人在阿坝的坚持，为最终挫败张国焘分裂主义、团结红军奠定了基础。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S6.2",
        "title": "四川金川（绥靖）",
        "location": "四川金川（绥靖）",
        "lat": 31.48,
        "lng": 102.07,
        "time": "1935年10月",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "百丈关战役（1935年11月）。张国焘率部南下的关键战役。红四方面军与川军激战七昼夜，歼敌1.5万余人但自身也损失近万人。因敌军不断增援被迫后撤。此战的失败彻底宣告了张国焘南下方针的破产。",
        "important_meeting": "卓木碉会议（1935年10月5日）。张国焘在四川金川卓木碉（今马尔康脚木足）另立「中共中央」、「中央政府」和「中央军委」，自封主席。这是张国焘分裂主义登峰造极的表现。",
        "history_event": "张国焘率左路军南下回到阿坝以南地区。10月5日在卓木碉召开会议，宣布另立中央。1935年11月发动百丈关战役，与川军决战，遭受重创。南下方针的失败使红四方面军由南下时的8万余人锐减到4万余人。1936年2月被迫后撤。",
        "core_site": "金川县红军长征纪念馆、卓木碉会议遗址（马尔康脚木足）、百丈关战斗遗址（四川名山）",
        "poem_article": "无",
        "typical_story": "百丈关战役是张国焘南下方针的豪赌。红四方面军将士英勇奋战，但面对优势敌军和不利地形伤亡惨重。战斗最激烈时，红军伤员自己滚下悬崖也不愿被俘。战后红军士气低落，张国焘的「打到成都吃大米」的口号彻底落空。",
        "typical_people": "张国焘：另立中央的分裂主义者。徐向前：指挥百丈关战役但无力回天。陈昌浩：红四方面军政委，支持张国焘。",
        "historical_significance": "金川（绥靖）是张国焘南下失败和另立中央的核心地点。百丈关战役的失败从军事上证明了南下方针的错误。红四方面军由8万锐减至4万余，付出了惨痛代价。张国焘分裂主义从此走向末路。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S7.1",
        "title": "炉霍道孚",
        "location": "四川炉霍道孚",
        "lat": 31.5,
        "lng": 100.67,
        "time": "1936年3月",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "无",
        "important_meeting": "道孚会议（1936年3月）。南下失败后红四方面军退入川西道孚、炉霍地区。会议决定执行中共中央北上方针。张国焘被迫宣布取消第二中央，这是张国焘分裂主义的最终失败。",
        "history_event": "南下失败后红四方面军损失惨重，被迫退入康北地区。在道孚、炉霍、甘孜一带休整。张国焘在内外压力下被迫取消第二中央。红四方面军开始准备第三次北上。在炉霍道孚休整期间，红军建立了博巴政府（藏族人民革命政府），扩大红军影响。",
        "core_site": "炉霍红军长征纪念馆、道孚红军遗址、博巴政府遗址",
        "poem_article": "无",
        "typical_story": "退到炉霍道孚时红四方面军将士极度疲惫。南下时8万余人的部队损失近半。指战员们思想混乱，对张国焘南下方针产生严重怀疑。朱德、刘伯承等抓紧做团结工作。一位营长晚年回忆：「那时候大家心里都明白，只有北上才有出路。」",
        "typical_people": "张国焘：被迫取消第二中央。朱德：在四方面军中做团结工作。刘伯承：坚持北上方针。徐向前：率部退入康北。",
        "historical_significance": "道孚炉霍是张国焘南下失败后的落脚地。取消第二中央标志着张国焘分裂主义的彻底破产。红四方面军从此走上了北上与中央红军会合的正确道路。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "important_meeting", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S7.2",
        "title": "四川甘孜",
        "location": "四川甘孜",
        "lat": 31.62,
        "lng": 100.0,
        "time": "1936年6月",
        "army": "红四方面军",
        "core_numbers": "红二方面军、红四方面军",
        "famous_battle": "无",
        "important_meeting": "甘孜会议（1936年6月）。红二、红四方面军在甘孜举行会师大会。朱德、任弼时、贺龙等坚决拥护党中央北上方针。张国焘在红二方面军的压力下被迫同意共同北上。",
        "history_event": "1936年6月，红二、红六军团到达甘孜与红四方面军会师。红四方面军为远道而来的兄弟部队准备了大量物资。两军会师后力量重新壮大。在朱德、任弼时、贺龙等人的努力下，张国焘被迫同意共同北上。7月初红二、红四方面军从甘孜出发北上。",
        "core_site": "甘孜红军会师遗址、甘孜县朱德总司令和五世格达活佛纪念馆",
        "poem_article": "无",
        "typical_story": "甘孜会师后朱德和五世格达活佛建立了深厚友谊。格达活佛组织藏族群众为红军筹集粮食。朱德赠给格达活佛一面红旗，上面写着「拥护红军」四个大字。格达活佛后来为促成西藏和平解放做出重大贡献。",
        "typical_people": "朱德：在甘孜做团结工作。张国焘：被迫同意北上。徐向前：率红四方面军与红二方面军会师。李先念：接待红二方面军。",
        "historical_significance": "甘孜会师是红四方面军从南下失败到北上正确道路的转折点。在红二方面军和朱德等人的压力下，张国焘分裂主义被彻底克服。红四方面军从此走上了北上与中央红军会合的正确道路。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "important_meeting", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S8.1",
        "title": "甘肃岷县",
        "location": "甘肃岷县",
        "lat": 34.42,
        "lng": 104.02,
        "time": "1936年8月",
        "army": "红四方面军",
        "core_numbers": "红四方面军",
        "famous_battle": "岷洮西战役（1936年8月）。红四方面军主力发起岷洮西（岷县、洮州、西固）战役，歼灭敌军3000余人。红军攻占岷县县城和周围广大地区，控制了甘肃南部大片区域。",
        "important_meeting": "岷州会议（1936年9月）。讨论红军下一步行动方向。张国焘再次提出西进青海的主张。朱德、任弼时等坚持北上与中央红军会合。会议最终通过了北上会师的方针。",
        "history_event": "红二、红四方面军从甘孜北上通过草地，1936年8月到达甘肃岷县。岷县是红军进入甘肃的第一站。红军在岷县周边展开攻势，占领漳县、临洮大片区域。张国焘在岷州会议上再次试图西进，但遭到朱德等人坚决反对。红军继续向会宁方向前进。",
        "core_site": "岷县红军长征纪念馆、岷州会议遗址、二郎山战斗遗址",
        "poem_article": "无",
        "typical_story": "岷州会议上张国焘再次提出西进主张，与朱德、任弼时激烈争论。朱德拍案而起：「中央在陕北等着我们，我们必须北上会师！」张国焘愤而离场。会后在徐向前、陈昌浩等人的努力下，部队继续向东向会宁方向前进。",
        "typical_people": "朱德：在岷州会议上坚持北上。张国焘：再次提出西进主张。徐向前：主张北上会师。任弼时：支持朱德，压制张国焘。",
        "historical_significance": "岷县是红四方面军北上甘肃后的关键节点。岷州会议最终粉碎了张国焘最后一次分裂企图。红军继续东进为会宁会师创造了条件。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "S8.2",
        "title": "甘肃会宁",
        "location": "甘肃会宁",
        "lat": 35.6937,
        "lng": 105.0523,
        "time": "1936年10月",
        "army": "红四方面军",
        "core_numbers": "红一、红二、红四方面军",
        "famous_battle": "无",
        "important_meeting": "无",
        "history_event": "1936年10月，红四方面军到达甘肃会宁，与红一方面军胜利会师。这是三大主力红军的历史性会师。红四方面军从1935年3月强渡嘉陵江开始长征，历时一年半转战川康甘数省，历经南下失败的挫折和北上长征的艰苦，终于与中央红军会合。会宁城一片欢腾。",
        "core_site": "会宁县红军长征会师旧址（含会师楼、会师纪念塔、会师纪念馆）、三军会师广场",
        "poem_article": "无",
        "typical_story": "会宁会师时红四方面军的许多战士衣衫褴褛。从开始的8万余人到会师时仅剩3万余人，红四方面军经历了最曲折最艰难的长征之路。会师大会上三军将士紧紧握手拥抱。徐向前感慨地说：「历经千难万险，我们终于到家了！」",
        "typical_people": "徐向前：红四方面军总指挥。陈昌浩：红四方面军政委。李先念：红30军政委。朱德：以红军总司令身份出席会师大会。",
        "historical_significance": "会宁会师标志着红四方面军长征的最终完成。红四方面军经历了南下失败的曲折，但最终回到党中央的正确路线。三大主力的会师使红军力量空前壮大。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    }
]

# =============================================================================
# 红25军节点（H1.1 ~ H6.2）
# =============================================================================

red25_nodes = [
    {
        "node_id": "H1.1",
        "title": "河南罗山（何家冲）",
        "location": "河南罗山（何家冲）",
        "lat": 31.88,
        "lng": 114.37,
        "time": "1934年11月16日",
        "army": "红25军",
        "core_numbers": "红25军",
        "famous_battle": "无。何家冲是红25军长征出发地，在此集结誓师出发。",
        "important_meeting": "无",
        "history_event": "红25军长征出发地。1934年11月16日，红25军2980余名将士在军长程子华、政委吴焕先、副军长徐海东率领下，从罗山县何家冲出发开始长征。红25军是四支长征队伍中平均年龄最小的一支（多数战士不到18岁），被称为「娃娃军」。出发前红25军进行了整编。",
        "core_site": "罗山何家冲红25军长征出发地、红25军军部旧址（何氏祠）、红军碾",
        "poem_article": "无",
        "typical_story": "何家冲有一棵300年树龄的古银杏树，红25军出发前在此集合。一位老红军回忆：「出发那天银杏树下站满了人，都是十几岁的娃娃。」当地百姓含泪送别这些「娃娃兵」踏上漫漫征途。出发时全军2980人，大多是十四五岁的少年。",
        "typical_people": "程子华：红25军军长。吴焕先：红25军政委。徐海东：红25军副军长。整支红25军：「娃娃军」的传奇。",
        "historical_significance": "何家冲是红25军长征的起点。红25军是四支长征队伍中最早到达陕北的一支，也是唯一一支出发后不减反增的红军部队。何家冲见证了这支「娃娃军」踏上伟大征程的起点。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "H2.1",
        "title": "河南方城（独树镇）",
        "location": "河南方城（独树镇）",
        "lat": 33.25,
        "lng": 112.97,
        "time": "1934年11月26日",
        "army": "红25军",
        "core_numbers": "红25军",
        "famous_battle": "独树镇战斗（1934年11月26日）。红25军在河南方城独树镇遭国民党军伏击，在极端不利条件下血战一日突出重围。此战是红25军长征中的第一场恶仗，与四渡赤水、嘉陵江战役等并列为长征十大著名战役之一。",
        "important_meeting": "无",
        "history_event": "红25军从何家冲出发后突破敌军多道封锁线，11月26日在方城独树镇遭国民党军第40军和骑兵团伏击。时值严寒大雪，我军因地形不利和天气恶劣损失惨重。吴焕先手持大刀高喊「跟我上」冲入敌阵稳定了阵脚。入夜后乘敌军包围圈尚未合拢，在村民带领下冒雪突出重围。",
        "core_site": "独树镇战斗纪念地（方城县）、红25军独树镇战斗纪念碑、红军长征鏖战独树镇纪念馆",
        "poem_article": "无",
        "typical_story": "独树镇战斗中政委吴焕先抽刀冲锋，大喊「共产党员跟我来！」稳定了即将溃散的部队。副军长徐海东率部增援，身先士卒。战斗中一挺机枪冻得打不响，战士用自己的体温焐热枪机继续射击。此战红军牺牲300余人。",
        "typical_people": "吴焕先：独树镇战斗中抽刀冲锋稳定军心。徐海东：率部增援扭转危局。程子华：红25军军长。",
        "historical_significance": "独树镇战斗是红25军长征中最凶险的战斗之一。此战展现了红25军将士顽强战斗意志，吴焕先带头冲锋的事迹成为红25军军魂的象征。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "H3.1",
        "title": "陕西庾家河",
        "location": "陕西丹凤（庾家河）",
        "lat": 33.7,
        "lng": 110.3,
        "time": "1934年12月10日",
        "army": "红25军",
        "core_numbers": "红25军",
        "famous_battle": "庾家河战斗（1934年12月10日）。红25军进入陕西后在庾家河与国民党军第60师遭遇激战。军长程子华、副军长徐海东均身负重伤。经反复冲杀血战半日将敌军击退。此战是创建鄂豫陕根据地的奠基之战。",
        "important_meeting": "庾家河会议（1934年12月10日）。在庾家河召开会议，决定创建鄂豫陕革命根据地。这是红25军长征中第一次明确的战略决策。会后红军以陕南为中心开展游击战争。",
        "history_event": "独树镇突围后红25军从河南转战进入陕西。12月10日在庾家河召开会议决定创建鄂豫陕根据地。当天中午会议尚未结束，国民党军60师突然袭来。红军仓促应战，双方在庾家河展开惨烈白刃战。红军尽管伤亡惨重但最终击溃敌军，站稳了脚跟。",
        "core_site": "庾家河战斗遗址（丹凤县）、鄂豫陕革命根据地纪念馆、红25军长征在陕西纪念馆",
        "poem_article": "无",
        "typical_story": "庾家河战斗是红25军最激烈的一次战斗。军长程子华双手被子弹击穿，副军长徐海东头部中弹伤及眼底。战斗最危急时刻担架上的徐海东挣扎着要起来继续指挥。一位排长说：「副军长你放心躺着，我们一定把敌人打下去！」最终红军以血肉之躯击退了敌军。",
        "typical_people": "程子华：红25军军长，双手负重伤。徐海东：红25军副军长，头部重伤险些致命。吴焕先：政委，指挥战后整顿。",
        "historical_significance": "庾家河战斗是红25军生存与发展的关键之战。击败敌军后红25军在鄂豫陕边区站稳脚跟。鄂豫陕根据地的创建是红25军长征的重要成果。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "H4.1",
        "title": "陕西蓝田（葛牌镇）",
        "location": "陕西蓝田（葛牌镇）",
        "lat": 34.05,
        "lng": 109.33,
        "time": "1935年2月",
        "army": "红25军",
        "core_numbers": "红25军",
        "famous_battle": "葛牌镇战斗（1935年2月）。红25军在蓝田葛牌镇击溃国民党军两个团，攻占葛牌镇。葛牌镇成为鄂豫陕革命根据地的重要据点。红军在此建立了区苏维埃政府。",
        "important_meeting": "葛牌镇会议（1935年2月）。红25军在此召开会议，总结创建根据地的经验，进一步扩大根据地和红军力量。",
        "history_event": "1935年2月，红25军在蓝田葛牌镇击溃敌军后在此建立鄂豫陕根据地的重要据点。葛牌镇是红军在关中地区的重要活动区域。红军在葛牌镇建立区苏维埃政府，打土豪分田地。红25军在此扩红，部队得到了补充。葛牌镇成为红25军的重要后方基地。",
        "core_site": "葛牌镇区苏维埃政府旧址（蓝田县）、红25军葛牌镇纪念馆",
        "poem_article": "无",
        "typical_story": "红25军在葛牌镇建立了苏维埃政府，实行打土豪分田地政策。当地贫苦农民踊跃参军。一位老汉把三个儿子都送去当了红军。红军在镇上刷写标语：「红军是穷人的队伍」「打倒土豪劣绅」。至今葛牌镇仍保留着当年的红军标语。",
        "typical_people": "吴焕先：政委，领导在葛牌镇建立政权。徐海东：伤愈后继续领导扩红。",
        "historical_significance": "葛牌镇是鄂豫陕根据地的重要据点。红25军在葛牌镇的实践证明了「先扎根再长征」策略的成功。建立根据地使红25军得以休整和补充。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "important_meeting", "history_event",
            "historical_significance", "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "H5.1",
        "title": "陕西长安（沣峪口）",
        "location": "陕西长安（沣峪口）",
        "lat": 34.03,
        "lng": 108.85,
        "time": "1935年7月",
        "army": "红25军",
        "core_numbers": "红25军",
        "famous_battle": "无",
        "important_meeting": "沣峪口会议（1935年7月15日）。红25军得知中央红军和红四方面军已在川西会师且可能北上的消息后，召开紧急会议决定西征北上，策应中央红军行动。这是红25军战略方向的重大转变。",
        "history_event": "红25军在葛牌镇等地的鄂豫陕根据地经过半年发展力量壮大。1935年7月，原鄂豫皖省委交通员石建民带来中央文件和中央红军与红四方面军会师的消息。红25军当即决定留部分力量坚持根据地，主力西征北上策应中央红军并会合陕北红军。",
        "core_site": "沣峪口会议遗址（西安长安区）、红25军长安活动遗址",
        "poem_article": "无",
        "typical_story": "沣峪口会议上程子华、吴焕先、徐海东等人讨论决定：「我们红25军要西征北上，去接应中央红军！」消息传出全军振奋。第二天全军从沣峪口出发踏上西征之路。一位小战士说：「中央红军是我们的老大哥，我们要去接应他们！」",
        "typical_people": "程子华：红25军军长，主持沣峪口会议。吴焕先：政委，决定西征北上。徐海东：副军长。",
        "historical_significance": "沣峪口会议是红25军从就地建政转向北上会师的关键决策。红25军主动西征北上策应中央红军，体现了革命的全局观念和主动担当精神。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "important_meeting", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "H6.1",
        "title": "甘肃泾川（王村镇）",
        "location": "甘肃泾川（王村镇）",
        "lat": 35.32,
        "lng": 107.35,
        "time": "1935年8月21日",
        "army": "红25军",
        "core_numbers": "红25军",
        "famous_battle": "泾川战斗（1935年8月21日）。红25军在甘肃泾川王村镇的汭河附近遭国民党军袭击。战斗中红25军政委吴焕先亲率部队冲锋，不幸中弹牺牲，年仅28岁。此战是红25军长征中最沉痛的损失。",
        "important_meeting": "无",
        "history_event": "红25军从沣峪口西征，经甘肃两当、天水等地北上。1935年8月21日在泾川王村镇以南的汭河附近遭马鸿宾部35师袭击。红25军指战员正在渡河，被敌骑兵突袭后路。政委吴焕先率领军部直属分队从侧翼出击，在打退敌军冲锋时不幸中弹牺牲。此战给红25军造成了不可挽回的损失。",
        "core_site": "泾川吴焕先烈士纪念馆、王村镇红25军战斗遗址、吴焕先烈士陵墓",
        "poem_article": "无",
        "typical_story": "吴焕先牺牲时年仅28岁，是红25军最敬爱的政委。他牺牲后全军悲痛不已，徐海东泪流满面。当地群众将吴焕先的遗体秘密安葬。新中国成立后吴焕先被追认为革命烈士。毛泽东曾评价：「红25军远征为中国革命立了大功，吴焕先功不可没。」",
        "typical_people": "吴焕先：红25军政委，牺牲在泾川战斗，年仅28岁。徐海东：接替吴焕先继续率部北上。程子华：负伤后仍坚持指挥。",
        "historical_significance": "吴焕先的牺牲是红25军长征中最大的损失。他是红25军的灵魂人物，他的牺牲使全军悲愤交加但更加坚定北上决心。泾川战斗后红25军继续北上，终于在永坪镇与陕北红军会师。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "famous_battle", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    },
    {
        "node_id": "H6.2",
        "title": "陕西永坪镇",
        "location": "陕西延川（永坪镇）",
        "lat": 36.85,
        "lng": 110.05,
        "time": "1935年9月15日",
        "army": "红25军",
        "core_numbers": "红25军、陕北红军",
        "famous_battle": "无",
        "important_meeting": "永坪镇会师（1935年9月15日）。红25军与刘志丹率领的陕北红军在延川县永坪镇胜利会师。会师后红25军编入红15军团，徐海东任军团长，刘志丹任副军团长。",
        "history_event": "红25军从泾川继续北上，经陕北保安进入陕甘边区。1935年9月15日到达延川县永坪镇，与陕北红军会师。红25军是四支长征队伍中最早到达陕北的一支。从出发时的2980人到会师时约3400人，兵力不减反增，是唯一一支人数增加的队伍。9月18日两军召开会师大会，合编为红15军团。",
        "core_site": "永坪镇红军会师旧址（延川县）、永坪会师纪念馆、红15军团成立地",
        "poem_article": "无",
        "typical_story": "永坪镇会师时陕北红军和当地群众敲锣打鼓热烈欢迎。刘志丹与徐海东紧紧握手。毛泽东后来高度评价红25军的贡献：「徐海东部由陕南经陇东到陕北，最先与陕北红军会合，为中央红军陕北落脚奠定了基础。」红25军出发时2980人，此时3400人，创造了长征史上的奇迹。",
        "typical_people": "徐海东：率红25军到达永坪镇。刘志丹：陕北红军领袖。程子华：红15军团政委。习仲勋：陕甘边区领导人。",
        "historical_significance": "永坪镇会师是红军长征中第一次大会师。红25军最先到达陕北，为中央红军后来的落脚提供了重要基础。红15军团的成立大大增强了陕北红军的力量。红25军的成功证明「边走边建根据地」的灵活策略是可以成功的。",
        "status": "active",
        "spark_remains": None,
        "active_sections": [
            "time", "history_event", "historical_significance",
            "core_site", "typical_story", "typical_people"
        ]
    }
]

# =============================================================================
# 合并所有节点
# =============================================================================
all_nodes = existing_nodes + red2_nodes + red4_nodes + red25_nodes

# 统计
from collections import Counter
army_counts = Counter(n["army"] for n in all_nodes)
print(f"生成后总节点数: {len(all_nodes)}")
print(f"各军节点数: {dict(army_counts)}")

# 写入文件
output_path = json_path  # 直接覆盖
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_nodes, f, ensure_ascii=False, indent=2)

print(f"已写入: {output_path}")
print("完成！")
