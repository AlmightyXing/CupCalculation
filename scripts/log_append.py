import codecs

with codecs.open('logs/log-260705.md', 'a', 'utf-8') as f:
    f.write('- 2026-07-05 15:59: 根据更新后的《后端技能伤害计算逻辑.md》文件中的规则（包括包含“部署后”的持续/瞬发判定，以及区分了 auto 和 manual 中的弹药类技能处理逻辑）修改了 update_skills.py 脚本，并重新扫描执行，成功更新了 10 个文件。\n')
