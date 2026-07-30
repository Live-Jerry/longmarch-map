path = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/static/js/controls.js"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
for i, line in enumerate(lines):
    # Line 77-79: button handler that should call showSpeedSelector
    if "btn-autowalk" in line and "addEventListener" in line:
        # Check the next line for startAutowalk
        j = i
        while j < len(lines) and j < i + 5:
            stripped = lines[j].strip()
            if stripped == "startAutowalk();":
                lines[j] = lines[j].replace("startAutowalk();", "showSpeedSelector();")
                print("Changed line %d: startAutowalk -> showSpeedSelector" % (j + 1))
                found = True
                break
            j += 1
        if found:
            break

if not found:
    print("No match found - checking current state...")
    for i, line in enumerate(lines):
        if "btn-autowalk" in line and "addEventListener" in line:
            print("Found btn-autowalk listener at line %d: %s" % (i+1, line.rstrip()))
            for j in range(i, min(i+5, len(lines))):
                print("  Line %d: %s" % (j+1, lines[j].rstrip()))

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
