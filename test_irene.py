import json
import os
import sys

# Add project root to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.function.logic.operators.ii07_艾丽妮 import Ii07艾丽妮
from backend.function.battle.enemy import Enemy

def main():
    # 1. Load Irene's parsed JSON data
    json_path = os.path.join("data", "parsed_data", "II07_艾丽妮.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        irene_data = json.load(f)
        
    # 2. Instantiate Irene
    irene = Ii07艾丽妮(irene_data)
    print(f"[{irene.profession}] {irene.name} 实例化成功!")
    print(f"基础攻击力: {irene.base_atk} | 信赖攻击力: {irene.trust_atk} | 最终攻击力面板: {irene.final_base_atk}")
    print(f"攻击速度: {irene.attack_speed} | 攻击间隔: {irene.attack_interval}s")
    print("-" * 50)
    
    # 3. Create Enemies
    enemies = []
    for i in range(6):
        def_val = i * 1000
        res_val = i * 20
        enemy = Enemy(f"test_enemy_{i}", f"测试靶机_{i}", base_hp=100000, base_def=def_val, base_res=res_val)
        enemies.append(enemy)
        
    # 4. Calculate DPS and Damage for each skill and enemy
    skills_to_test = [
        (-1, "普通攻击"),
        (0, "技能1 (起风)"),
        (1, "技能2 (裂潮)"),
        (2, "技能3 (判决)")
    ]
    
    for enemy in enemies:
        print(f"目标: {enemy.name} (防御: {enemy.current_def}, 法抗: {enemy.current_res})")
        for skill_idx, skill_name in skills_to_test:
            result = irene.calculate_dps(enemy, skill_index=skill_idx)
            
            if skill_idx == -1:
                print(f"  {skill_name}: 期望单次普攻总伤 = {result['total_damage']:.2f}, 期望 DPS = {result.get('dps', 0):.2f}")
            else:
                out_str = f"  {skill_name}: 期望爆发总伤 = {result['total_damage']:.2f}"
                if 'cycle_dps' in result:
                    out_str += f" | 回转周期总伤 = {result['cycle_total_damage']:.2f}, 周期用时 = {result['cycle_time']:.2f}s, 周期DPS = {result['cycle_dps']:.2f}"
                print(out_str)
        print("-" * 50)

if __name__ == "__main__":
    main()
