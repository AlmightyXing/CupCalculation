with open('e:/Local_AI_Station/CupCalculation/logs/log-260704.md', 'a', encoding='utf-8') as f:
    f.write('\n- 18:35 前端优化与配置：\n')
    f.write('  - 修复“沙盒模拟”导航按钮的激活样式。\n')
    f.write('  - 将沙盒职业筛选界面的术语从“大职业-小职业”更正为“职业-子职业”。\n')
    f.write('  - 提取了 .form-select CSS 类，修复了暗色模式下下拉框文字与背景融合的问题。\n')
    f.write('  - 修复沙盒界面初始化逻辑，使得选择主职业后能正常筛选并展示子职业和干员列表。\n')
    f.write('  - 在 main_app.py 中关闭了 pywebview 的开发者工具窗口 (debug=False)。\n')
