with open("logs/log-260629.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    stripped = line.strip()
    if not stripped:
        clean_lines.append(line)
    elif stripped.startswith("-") or stripped.startswith("#"):
        clean_lines.append(line)

with open("logs/log-260629.md", "w", encoding="utf-8") as f:
    f.writelines(clean_lines)
