with open(r'D:\长征文化\_controls_check.js', encoding='utf-8') as f:
    content = f.read()

old = '''            pcEl4.style.display = "";
            pcEl4.classList.add("visible");
            // 速度选择器移到控制框下方（不重叠）
            var btn4 = document.getElementById("btn-autowalk");
            if (btn4) {
                var pcRect4 = pcEl4.getBoundingClientRect();
                ss.style.top = (pcRect4.bottom + 4) + "px";
                ss.style.right = (window.innerWidth - btn4.getBoundingClientRect().left + 8) + "px";
            }'''

new = '''            // 先给播放控制框定位（和速度选择器一样靠按钮）
            var btn4 = document.getElementById("btn-autowalk");
            if (btn4) {
                var rect4 = btn4.getBoundingClientRect();
                pcEl4.style.top = rect4.top + "px";
                pcEl4.style.right = (window.innerWidth - rect4.left + 8) + "px";
                pcEl4.style.left = "auto";
                pcEl4.style.bottom = "auto";
            }
            pcEl4.style.display = "";
            pcEl4.classList.add("visible");
            // 速度选择器移到控制框下方（不重叠）
            if (btn4) {
                var pcRect4 = pcEl4.getBoundingClientRect();
                ss.style.top = (pcRect4.bottom + 4) + "px";
                ss.style.right = (window.innerWidth - btn4.getBoundingClientRect().left + 8) + "px";
            }'''

count = content.count(old)
print(f'Found {count} matches')

if count == 1:
    content = content.replace(old, new, 1)
    with open(r'D:\长征文化\_controls_fixed.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed play-controls positioning')
else:
    # Debug: show the actual text around that area
    idx = content.find('pcEl4.style.display')
    if idx >= 0:
        print(f'Text around match ({idx}):')
        print(repr(content[idx:idx+350]))
