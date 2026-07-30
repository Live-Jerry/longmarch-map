import json
import re

path = r"C:\Users\RP Conference\.openclaw\agents\cz\sessions\afb5d8e9-1672-490c-b9e1-4e2e2e316737.jsonl.reset.2026-07-28T01-02-47.465Z"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find lines in timestamp range 07:50-09:20 UTC (15:50-17:20 CST)
start_line = -1
end_line = -1
for i, line in enumerate(lines):
    m = re.search(r'"timestamp":"2026-07-27T0(7:[5-9]|8:|9:[0-2])', line)
    if m:
        if start_line == -1:
            start_line = i
        end_line = i

print(f"Time range 07:50-09:20 UTC (15:50-17:20 CST): lines {start_line} to {end_line}")
print(f"Lines in range: {end_line - start_line + 1}")

# Search for messages about EC table rules
keywords = ["列", "不能动", "不能写", "不能修改", "变更跟踪表", "影响模块", "原因分析", "变更方案"]
for i in range(start_line, min(end_line + 1, start_line + 800)):
    line = lines[i]
    matched = False
    for kw in keywords:
        if kw in line:
            matched = True
            break
    if matched and ('"role":"user"' in line or '"role":"assistant"' in line):
        try:
            obj = json.loads(line)
            msg = obj.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", "")
            if isinstance(content, list):
                for c in content:
                    if "text" in c:
                        content = c["text"]
            ts = obj.get("timestamp", "")
            text = str(content)[:500]
            print(f"\n=== {ts} [{role}] ===")
            print(text)
        except:
            pass
