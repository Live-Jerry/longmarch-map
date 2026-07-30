path = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/static/js/controls.js"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("showSpeedSelector();", "startAutowalk();", 1)
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("Patched restartAutowalk to call startAutowalk directly")
