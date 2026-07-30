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

# Verify the old text exists
if old not in content:
    # Try with different whitespace
    print('Direct match failed. Looking for similar text...')
    idx = content.find('pcEl4.style.display = ""')
    if idx >= 0:
        print('Found at', idx)
        end = content.find('}', idx)
        print(repr(content[idx:end+1]))
        print()
        print(f'Characters at idx: {[ord(c) for c in content[idx:idx+30]]}')
else:
    print('Found exact match')
