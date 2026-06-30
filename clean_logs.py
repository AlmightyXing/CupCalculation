import io

with open("logs/log-260629.md", "rb") as f:
    content_bytes = f.read()

# PowerShell might have written UTF-16 LE with BOM, but mixed with UTF-8.
# We'll just read as utf-8 ignore, find the lines, and rebuild it.
text = content_bytes.decode('utf-8', errors='ignore')
lines = text.splitlines()

# Filter out the lines with weird null bytes or mojibake
clean_lines = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    if '\x00' in line or 'nx' in line or 'gbL' in line or 'vOS' in line:
        continue # skip garbled lines
    clean_lines.append(line)

# Add the repaired lines
clean_lines.append("- 15:21 确立了 Manager Agent 的项目协调员身份，并制定了阶段 1：前端架构 Agent 的执行计划 (implementation_plan.md)。")
clean_lines.append("- 15:26 执行了阶段 1，完成了前端微信小程序基建架构的骨架生成，配置了 Dark Mode 并在 frontend_stage1_delivery.md 交付了阶段报告。")
clean_lines.append("- 16:09 收到继续进行前端第二阶段的指令，创建了独立的阶段 2 执行计划 (logs\\implementation_plans\\implementation_plan_frontend_phase2.md) 准备提交审核。")

# Ensure the last line we added about phase 2 is still there if we accidentally stripped it.
if not any("16:15" in l for l in clean_lines):
    clean_lines.append("- 16:15 UI与数据Agent完成了阶段二的开发，集成了ECharts图表和排行榜卡片，生成了 delivery_frontend_phase2.md 报告。")

with open("logs/log-260629.md", "w", encoding="utf-8") as f:
    for l in clean_lines:
        f.write(l + "\n")
