fpath = "/opt/longmarch-dev/001 项目源码/static/js/controls.js"
content = open(fpath, "r", encoding="utf-8").read()
content = content.replace(
    "window.selectAutowalkSpeed = selectAutowalkSpeed;\nwindow.jumpAutowalkToNode = jumpAutowalkToNode;\nwindow.autowalkState = autowalkState;",
    "window.selectAutowalkSpeed = selectAutowalkSpeed;\nwindow.jumpAutowalkToNode = jumpAutowalkToNode;"
)
open(fpath, "w", encoding="utf-8").write(content)
print("Reverted: autowalkState export removed")
