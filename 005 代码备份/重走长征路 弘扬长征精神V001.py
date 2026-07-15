"""🚩 长征路线 - 卫星地图 + 真实照片版

生成交互式卫星地图的 Python 脚本。
使用 Leaflet.js 在 ArcGIS 卫星影像上绘制长征路线，
每个节点包含历史信息、毛主席诗词、真实照片和语音朗读功能。

用法:
    直接运行脚本，自动启动 HTTP 服务器并打开浏览器。

依赖:
    Python 标准库 (webbrowser, http.server, threading, socketserver)
    无需第三方库。

属性:
    IMAGES: dict[str, str] — 站点名称到真实照片 URL 的映射
    html: str — Leaflet.js 交互式地图的完整 HTML 模板
"""
import webbrowser, os, http.server, threading, socketserver

# 从360图片找到的真实照片（国内CDN，稳定加载）
IMAGES = {
  "瑞金": "https://p2.ssl.qhimgs1.com/sdr/400__/t0496cff67f7060c898.jpg",
  "湘江战役": "https://img.pconline.com.cn/images/upload/upc/tx/itbbs/2112/16/c3/287505551_1639626940952.jpg",
  "遵义会议": "https://p2.ssl.qhimgs1.com/sdr/400__/t015bc09ac17b594c42.jpg",
  "四渡赤水": "https://p5.ssl.qhimgs1.com/sdr/400__/t015b1107aebafbb875.jpg",
  "飞夺泸定桥": "https://p3.ssl.qhimgs1.com/sdr/400__/t01ffad666a4ee5c703.jpg",
  "过草地": "https://p1.ssl.qhimgs1.com/t040ed0a944793ee6b7.jpg",
}

html = r'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>🚩 红军长征路线图</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{margin:0;padding:0}#map{width:100vw;height:100vh}
.leaflet-popup-content-wrapper{border-radius:14px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,0.35);padding:0}
.leaflet-popup-content{margin:0 !important;width:340px}
.pop-img{width:100%;height:150px;overflow:hidden;position:relative}
.pop-img img{width:100%;height:100%;object-fit:cover}
.pop-img .pop-label{position:absolute;bottom:8px;left:10px;font-size:14px;background:rgba(0,0,0,0.6);padding:3px 14px;border-radius:12px;color:#fff}
.pop-body{padding:12px 15px 15px}
.pop-body h3{font-size:20px;margin:0 0 6px 0;display:flex;align-items:center;gap:8px}
.pop-body h3 .tag{display:inline-block;padding:2px 10px;border-radius:10px;font-size:12px;color:#fff}
.tag-mtg{background:#8E44AD}.tag-btl{background:#E74C3C}.tag-arv{background:#27AE60}.tag-ev{background:#2980B9}
.pop-body .info{font-size:14px;color:#444;margin:6px 0;line-height:1.7}
.pop-body .poem{padding:10px;background:#fef9e7;border-left:3px solid #e67e22;border-radius:4px;margin:8px 0;font-size:14px;color:#7d6608;line-height:1.9;white-space:pre-line;font-family:"楷体",serif}
.pop-body .btn-read{width:100%;margin-top:6px;padding:7px;background:#2c3e50;color:#fff;border:none;border-radius:20px;font-size:14px;cursor:pointer;text-align:center}
.pop-body .btn-read.speaking{background:#e74c3c;animation:pulse .8s infinite}
@keyframes pulse{0%{opacity:1}50%{opacity:.6}100%{opacity:1}}
.title{position:absolute;top:15px;left:50%;transform:translateX(-50%);z-index:1000;background:rgba(0,0,0,0.75);color:#fff;padding:10px 30px;border-radius:30px;font-size:18px;text-align:center}
.layers{position:absolute;bottom:20px;left:15px;z-index:1000;background:rgba(255,255,255,0.9);padding:7px 12px;border-radius:8px;font-size:12px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.2)}
</style></head><body>
<div class="title">🚩 红军长征路线图 · 瑞金→延安 1934-1935</div>
<div id="map"></div>
<div class="layers" id="swBtn">🛰️ 卫星地图</div>
<script>
var layers = {
  "🛰️ 卫星影像": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:18}),
  "🗺️ 标准地图": L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',{maxZoom:19}),
  "🌙 深色地图": L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',{maxZoom:19}),
};
var keys=Object.keys(layers),cur=0;
var map=L.map('map',{center:[31.5,108.5],zoom:6,layers:[layers[keys[0]]]});
document.getElementById('swBtn').onclick=function(){
  cur=(cur+1)%keys.length;
  map.eachLayer(function(l){if(l._url)map.removeLayer(l);});
  layers[keys[cur]].addTo(map);this.textContent=keys[cur];
};

function speakText(text,btn){
  if(speechSynthesis.speaking){speechSynthesis.cancel();if(btn)btn.className='btn-read';return;}
  var u=new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g,'').replace(/\n+/g,'。'));
  u.lang='zh-CN';u.rate=0.9;
  if(btn)btn.className='btn-read speaking';
  u.onend=function(){if(btn)btn.className='btn-read';};
  speechSynthesis.speak(u);
}

// 站点数据: [名称, 纬度, 经度, 标签样式, 标签名, 简介, 诗词, 图片URL/emoji, 图片描述, 颜色]
var stops = [
  ["瑞金",25.88,116.03,"tag-arv","出发",
   "瑞金是中央苏区的中心，1934年10月红军从瑞金出发。",
   "《七律·长征》\n\n红军不怕远征难，万水千山只等闲。\n五岭逶迤腾细浪，乌蒙磅礴走泥丸。\n金沙水拍云崖暖，大渡桥横铁索寒。\n更喜岷山千里雪，三军过后尽开颜。",
   "https://p2.ssl.qhimgs1.com/sdr/400__/t0496cff67f7060c898.jpg","#27AE60"],
  ["湘江战役",25.30,110.50,"tag-btl","重要战役",
   "1934年11月27日至12月1日，红军与国民党军血战五昼夜，从8万余人锐减至3万余人。",
   "《忆秦娥·娄山关》\n\n西风烈，长空雁叫霜晨月。\n霜晨月，马蹄声碎，喇叭声咽。\n雄关漫道真如铁，而今迈步从头越。\n从头越，苍山如海，残阳如血。",
   "https://img.pconline.com.cn/images/upload/upc/tx/itbbs/2112/16/c3/287505551_1639626940952.jpg","#E74C3C"],
  ["遵义会议",27.73,106.93,"tag-mtg","重要会议",
   "1935年1月15日至17日，遵义会议确立了毛泽东的领导地位。",
   "《十六字令三首》\n\n山，快马加鞭未下鞍。惊回首，离天三尺三。\n山，倒海翻江卷巨澜。奔腾急，万马战犹酣。\n山，刺破青天锷未残。天欲堕，赖以拄其间。",
   "https://p2.ssl.qhimgs1.com/sdr/400__/t015bc09ac17b594c42.jpg","#8E44AD"],
  ["四渡赤水",28.50,106.00,"tag-btl","重要战役",
   "毛泽东指挥红军四次渡过赤水河，甩开40万敌军，被誉为「得意之笔」。",
   "《清平乐·会昌》\n\n东方欲晓，莫道君行早。\n踏遍青山人未老，风景这边独好。\n会昌城外高峰，颠连直接东溟。\n战士指看南粤，更加郁郁葱葱。",
   "https://p5.ssl.qhimgs1.com/sdr/400__/t015b1107aebafbb875.jpg","#2980B9"],
  ["巧渡金沙江",26.50,102.50,"tag-ev","重要事件",
   "7条小船7天7夜渡3万人，跳出敌军包围圈。",
   "《七律·长征》节选\n\n金沙水拍云崖暖，大渡桥横铁索寒。",
   "https://newbbs-fd.zol-img.com.cn/t_s1200x5000/g4/M06/0D/0F/ChMlzF2gD7aIY1nDAAnhKh86gIoAAYGJwB_ze0ACeFC749.jpg","#1ABC9C"],
  ["飞夺泸定桥",29.92,102.23,"tag-btl","重要战役",
   "22名勇士攀爬13根铁索，冒着枪林弹雨夺取泸定桥。",
   "《七律·长征》节选\n\n金沙水拍云崖暖，大渡桥横铁索寒。",
   "https://p3.ssl.qhimgs1.com/sdr/400__/t01ffad666a4ee5c703.jpg","#D35400"],
  ["翻越夹金山",30.80,102.50,"tag-ev","重要事件",
   "翻越海拔4114米的夹金山，穿着单衣草鞋爬雪山。",
   "《念奴娇·昆仑》\n\n横空出世，莽昆仑，阅尽人间春色。\n飞起玉龙三百万，搅得周天寒彻。",
   "https://newbbs-fd.zol-img.com.cn/t_s1200x5000/g5/M00/06/04/ChMkJ1vbphCIUE6AAARNE-sFA-wAAs5zgHvs-QABE0r231.jpg","#95A5A6"],
  ["懋功会师",31.00,102.40,"tag-ev","胜利会师",
   "1935年6月18日，中央红军与红四方面军在懋功（今小金县）胜利会师。",
   "两大红军主力会师，壮大了革命力量。",
   "🤝","#F39C12"],
  ["过草地",33.58,102.97,"tag-ev","重要事件",
   "穿越松潘草地，七天七夜泥潭沼泽，上万人牺牲。",
   "《清平乐·六盘山》\n\n天高云淡，望断南飞雁。\n不到长城非好汉，屈指行程二万。\n六盘山上高峰，红旗漫卷西风。\n今日长缨在手，何时缚住苍龙？",
   "https://p1.ssl.qhimgs1.com/t040ed0a944793ee6b7.jpg","#7F8C8D"],
  ["腊子口战役",34.10,104.30,"tag-btl","重要战役",
   "腊子口天险一夫当关万夫莫开，红军奇袭攻克。",
   "六盘山上高峰，红旗漫卷西风。\n今日长缨在手，何时缚住苍龙？",
   "http://lzkzyjng.com/uploadfile/2019/0829/20190829023732598.jpg","#C0392B"],
  ["吴起镇",36.92,107.30,"tag-arv","长征胜利",
   "1935年10月19日长征胜利！历时一年，行程二万五千里。出发8.6万人，到达约7000人。",
   "《七律·长征》\n\n红军不怕远征难，万水千山只等闲。\n五岭逶迤腾细浪，乌蒙磅礴走泥丸。\n金沙水拍云崖暖，大渡桥横铁索寒。\n更喜岷山千里雪，三军过后尽开颜。",
   "https://n.sinaimg.cn/sinacn10116/108/w1024h684/20191109/289f-iieqapt0403381.jpg","#27AE60"],
  ["直罗镇战役",36.00,109.40,"tag-btl","重要战役",
   "1935年11月，红军在直罗镇全歼东北军第109师，为党中央把革命大本营放在西北举行了奠基礼。",
   "《沁园春·雪》\n\n北国风光，千里冰封，万里雪飘。\n望长城内外，惟余莽莽；大河上下，顿失滔滔。\n山舞银蛇，原驰蜡象，欲与天公试比高。\n须晴日，看红装素裹，分外妖娆。\n\n江山如此多娇，引无数英雄竞折腰。\n惜秦皇汉武，略输文采；唐宗宋祖，稍逊风骚。\n一代天骄，成吉思汗，只识弯弓射大雕。\n俱往矣，数风流人物，还看今朝。",
   "https://n.sinaimg.cn/sinacn10116/108/w1024h684/20200724/6040-ixttihw9920672.jpg","#C0392B"]
];

var colors=['#27AE60','#E74C3C','#8E44AD','#2980B9','#1ABC9C','#D35400','#95A5A6','#F39C12','#7F8C8D','#C0392B','#27AE60','#E74C3C'];
var pts=[];

stops.forEach(function(d,i){
  var n=d[0],la=d[1],lo=d[2],tc=d[3],tag=d[4],info=d[5],poem=d[6],img=d[7],bg=d[8];
  pts.push([la,lo]);

  // 图片区: 有真实照片就用照片，没有就用emoji+渐变
  var imgHtml;
  if(img && img.indexOf('http')==0){
    imgHtml = '<div class="pop-img"><img src="'+img+'" alt="'+n+'"><span class="pop-label">'+n+' · '+tag+'</span></div>';
  } else {
    imgHtml = '<div class="pop-img" style="background:linear-gradient(135deg,'+bg+','+colors[i]+');display:flex;align-items:center;justify-content:center;font-size:70px"><span>'+img+'</span><span class="pop-label">'+n+' · '+tag+'</span></div>';
  }

  var pop = imgHtml +
    '<div class="pop-body"><h3>📍 '+n+'</h3>'+
    '<div class="info">'+info+'</div><div class="poem">📜 '+poem+'</div>'+
    '<button class="btn-read" onclick="speakText(\''+
    info.replace(/'/g,'').replace(/"/g,'')+'。'+poem.replace(/'/g,'').replace(/"/g,'').replace(/\n/g,'。')+
    '\',this)">🔊 朗读全文</button></div>';

  L.marker([la,lo],{icon:L.divIcon({html:'<div style="background:'+colors[i]+';width:32px;height:32px;border-radius:50%;border:3px solid white;box-shadow:0 3px 12px rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;color:#fff;font-size:15px;font-weight:bold">'+(i+1)+'</div>',iconSize:[32,32],className:'',popupAnchor:[0,-18]})})
   .addTo(map).bindPopup(pop,{maxWidth:350});
});

var route = L.polyline(pts,{color:'#E74C3C',weight:4,dashArray:'10,8'}).addTo(map);
for(var i=0;i<pts.length-1;i++){
  var p1=pts[i],p2=pts[i+1],mid=[(p1[0]+p2[0])/2,(p1[1]+p2[1])/2];
  var ang=Math.atan2(p2[0]-p1[0],p2[1]-p1[1])*180/Math.PI;
  L.marker(mid,{icon:L.divIcon({html:'<div style="transform:rotate('+ang+'deg);font-size:20px;color:#E74C3C;text-shadow:0 0 6px #000">➤</div>',iconSize:[20,20],className:''}),interactive:false}).addTo(map);
}
map.fitBounds(route.getBounds(),{padding:[50,50]});
</script></body></html>'''

if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "长征路线.html")
    with open(html_path, "w", encoding="utf-8") as f: f.write(html)
    PORT = 8089
    try:
        httpd = socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler)
    except:
        PORT = 8090
        httpd = socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://localhost:{PORT}/{os.path.basename(html_path)}"
    webbrowser.open(url)
    print(f"✅ 启动！{url}")
    print("📸 12个站点有真实照片，1个插图占位")
    input("回车退出...")
