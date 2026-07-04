from backend.function.logic.professions import Alchemist
from backend.function.logic.formulas import calculate_arts_damage

class Ii02引星棘刺(Alchemist):
    """
    干员：引星棘刺
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.alchemy_unit_duration_extension = 0 # 炼金单元持续时间延长，默认为0
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：心相 (攻击力+10%，攻击范围内存在其他干员时，自身投掷的炼金单元持续时间延长3秒)
        # 攻击力+10%
        self.final_base_atk *= (1 + 0.10)
        # 炼金单元持续时间延长3秒 (计算时假设满足条件)
        self.alchemy_unit_duration_extension += 3
        
        # 天赋 2：视界 (在场时，所有友方单位攻击速度+5，敌方单位攻击速度-5；位于连续6格或以上直线道路的友方和敌方单位受到的效果翻倍)
        # 自身攻击速度+5
        self.attack_speed += 5
        # 敌方攻速降低和“翻倍”效果不直接影响引星棘刺自身的伤害计算，故不在此处体现。

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 引星棘刺是“炼金师”，其技能均造成法术伤害。
        # 默认普攻也为法术伤害，若无特殊说明，则按此计算。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔，主要用于DPS计算，对于持续伤害技能，DPS即为每秒伤害。
        # actual_atk_interval = self.attack_interval * 100 / self.attack_speed 
        
        if skill_index == 0:
            # 技能 1 (度算浪波)：向友方单位投掷炼金单元，提供防御和生命回复，对敌人无伤害。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (解构涌潮)：每秒受到相当于攻击力180%的法术伤害
            # 技能持续时间：15秒 + 天赋延长
            skill_duration = 15 + self.alchemy_unit_duration_extension
            
            # 每秒法术伤害
            dmg_per_sec = calculate_arts_damage(self.final_base_atk * 1.80, enemy.current_res)
            
            total_damage = dmg_per_sec * skill_duration
            # 对于持续伤害技能，DPS即为每秒伤害
            dps = dmg_per_sec
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (“我的海疆”)：被动效果攻击范围扩大。主动开启后，持续23秒，
            # 区域内敌人每秒受到攻击力210%的法术伤害，效果逐渐提升（15秒后达到最大，每秒伤害390%），
            # 同时敌人防御力-35%/-50%，法术抗性-35%/-50%。
            
            # 技能持续时间：23秒 + 天赋延长
            extended_duration = 23 + self.alchemy_unit_duration_extension
            
            total_damage = 0.0
            
            # 第一阶段：0-15秒，伤害和减抗效果逐渐提升
            segment1_duration = min(15.0, extended_duration)
            if segment1_duration > 0:
                # 伤害倍率从2.10提升至3.90，平均倍率为 (2.10 + 3.90) / 2 = 3.00
                # 法术抗性削弱从35%提升至50%，平均削弱比例为 (0.35 + 0.50) / 2 = 0.425
                
                avg_s1_dmg_per_sec = calculate_arts_damage(
                    self.final_base_atk * 3.00,
                    enemy.current_res,
                    res_ignore_ratio=0.425 # 应用平均法术抗性削弱
                )
                total_damage += avg_s1_dmg_per_sec * segment1_duration
            
            # 第二阶段：15秒后，效果达到最大值
            segment2_duration = max(0.0, extended_duration - 15.0)
            if segment2_duration > 0:
                # 伤害倍率为3.90
                # 法术抗性削弱比例为50%
                
                s2_dmg_per_sec = calculate_arts_damage(
                    self.final_base_atk * 3.90,
                    enemy.current_res,
                    res_ignore_ratio=0.50 # 应用最大法术抗性削弱
                )
                total_damage += s2_dmg_per_sec * segment2_duration
            
            # 技能期间总DPS
            dps = total_damage / extended_duration if extended_duration > 0 else 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
