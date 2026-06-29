import os
import json
import glob
import importlib.util
import inspect
from typing import Type
from backend.function.logic.base_operator import Operator
from backend.function.battle.enemy import Enemy
from backend.function.battle.engine import BattleEnvironment

def load_operator_class_from_path(file_path: str) -> Type[Operator]:
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Operator) and obj.__module__ == module.__name__:
            return obj
    raise Exception(f"No Operator subclass found in {file_path}")

def get_operator_data(op_name: str) -> dict:
    for f in os.listdir('data/parsed_data'):
        if op_name in f:
            with open(os.path.join('data/parsed_data', f), 'r', encoding='utf-8') as file:
                return json.load(file)
    raise Exception(f"JSON not found for {op_name}")

def main():
    print("="*50)
    print("启动战斗环境协同测试: 仇白 + 逻各斯 + 铃兰")
    print("="*50)
    
    # 1. 动态加载干员类和数据
    r172_path = glob.glob('backend/function/logic/operators/r172_*.py')[0]
    re03_path = glob.glob('backend/function/logic/operators/re03_*.py')[0]
    yd20_path = glob.glob('backend/function/logic/operators/yd20_*.py')[0]
    
    SuzuranClass = load_operator_class_from_path(r172_path)
    LogosClass = load_operator_class_from_path(re03_path)
    QiubaiClass = load_operator_class_from_path(yd20_path)
    
    op_suzuran = SuzuranClass(get_operator_data("铃兰"))
    op_logos = LogosClass(get_operator_data("逻各斯"))
    op_qiubai = QiubaiClass(get_operator_data("仇白"))
    
    # 目标：测试 2000防 40抗 的中重甲敌人
    enemy = Enemy.get_dummy_target(99)
    print(f"测试目标: {enemy}")
    print("-" * 50)
    
    # 【单打独斗测试】
    print("[单打独斗测试]")
    # 测试各自三技能 (skill_index = 2)
    qiubai_solo = op_qiubai.calculate_dps(enemy, skill_index=2)
    logos_solo = op_logos.calculate_dps(enemy, skill_index=2)
    suzuran_solo = op_suzuran.calculate_dps(enemy, skill_index=2)
    
    print(f"仇白 (S3): 总伤 {qiubai_solo.get('total_damage', 0):.1f}, DPS {qiubai_solo.get('dps', 0):.1f}")
    print(f"逻各斯 (S3): 总伤 {logos_solo.get('total_damage', 0):.1f}, DPS {logos_solo.get('dps', 0):.1f}")
    print(f"铃兰 (S3): 总伤 {suzuran_solo.get('total_damage', 0):.1f}, DPS {suzuran_solo.get('dps', 0):.1f}")
    
    solo_total = qiubai_solo.get('total_damage', 0) + logos_solo.get('total_damage', 0) + suzuran_solo.get('total_damage', 0)
    print(f"【单打独斗团队总伤】: {solo_total:.1f}")
    print("-" * 50)
    
    # 【环境协同测试】
    print("[协同战斗环境测试 - 动态面板注入]")
    env = BattleEnvironment()
    env.add_enemy(enemy)
    
    # 统一切换到三技能
    env.add_operator(op_suzuran, skill_index=2)
    env.add_operator(op_logos, skill_index=2)
    env.add_operator(op_qiubai, skill_index=2)
    
    result = env.simulate()
    
    combat_report = result['combat_report']
    applied_buffs = result['applied_buffs']
    
    print("【环境自动提取的全队 Buff 面板】:")
    for k, v in applied_buffs.items():
        print(f" - {k}: {v}")
    
    print("\n【环境注入后各干员实际表现】:")
    synergy_total = 0.0
    
    for op_id, rep in combat_report.items():
        # rep 是一个 list，因为可以对应多个 enemy，我们这里只有一个 enemy
        dmg = rep[0].get('total_damage', 0)
        dps = rep[0].get('dps', 0)
        synergy_total += dmg
        # 用 ID 查找名字打印
        name = "未知"
        if op_id == op_qiubai.character_id: name = "仇白 (S3)"
        if op_id == op_logos.character_id: name = "逻各斯 (S3)"
        if op_id == op_suzuran.character_id: name = "铃兰 (S3)"
            
        print(f"{name}: 总伤 {dmg:.1f}, DPS {dps:.1f}")
        
    print(f"【协同团队总伤】: {synergy_total:.1f}")
    
    improvement = (synergy_total - solo_total) / solo_total * 100 if solo_total > 0 else 0
    print(f"【协同增伤幅度】: +{improvement:.1f}%")
    print("="*50)

if __name__ == "__main__":
    main()
