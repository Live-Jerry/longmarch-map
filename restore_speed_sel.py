path = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/static/js/controls.js"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Count occurrences
cnt = c.count("showSpeedSelector();")
print("Found %d showSpeedSelector();" % cnt)
cnt2 = c.count("startAutowalk();")
print("Found %d startAutowalk();" % cnt2)

# Find the one at line 78 area (autowalk button handler)
idx = c.find("showSpeedSelector();")
if idx >= 0:
    context_before = c[max(0,idx-100):idx]
    if "首次点击" in context_before or "btn-autowalk" in context_before:
        print("Found speed selector in button handler at offset %d" % idx)
        c = c[:idx] + "showSpeedSelector();" + c[idx+len("showSpeedSelector();"):]
        print("Verified showSpeedSelector is present in button handler")
    else:
        print("First occurrence at %d, context: %s" % (idx, context_before[-50:]))

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("Done")
