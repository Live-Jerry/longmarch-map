fpath = "/opt/longmarch-dev/001 项目源码/static/js/controls.js"
content = open(fpath, "r", encoding="utf-8").read()

# Fix #1: Export autowalkState to window so map.js marker click can trigger jumpAutowalkToNode
content = content.replace(
    "window.selectAutowalkSpeed = selectAutowalkSpeed;\nwindow.jumpAutowalkToNode = jumpAutowalkToNode;",
    "window.selectAutowalkSpeed = selectAutowalkSpeed;\nwindow.jumpAutowalkToNode = jumpAutowalkToNode;\nwindow.autowalkState = autowalkState;"
)

open(fpath, "w", encoding="utf-8").write(content)
print("Fix applied: autowalkState exported to window")
