from backend.function.logic.professions import Summoner
from backend.function.logic.formulas import calculate_arts_damage

class Nm03令(Summoner):
    """
    干员：令
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：挑灯问梦 (召唤物相关，不直接影响令自身的伤害计算)
        pass 

        # 天赋 2：随付笺咏醉屠苏 (召唤物被击倒/吸收/回收时令攻击力+3%，最多叠加5层)
        # 按照最大层数叠加到攻击力中
        max_stacks = 5
        atk_increase_per_stack = 0.03
        self.final_base_atk *= (1 + atk_increase_per_stack * max_stacks)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 令的攻击造成法术伤害
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (重进酒)：持续25秒，自身与召唤物攻击力+50%，攻击速度+50
            duration = 25
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + 0.50)
            
            # 计算强化后的攻击速度和实际攻击间隔
            buffed_attack_speed = self.attack_speed + 50
            buffed_actual_atk_interval = self.attack_interval * 100 / buffed_attack_speed
            
            # 技能持续期间的普攻次数
            num_attacks = duration / buffed_actual_atk_interval
            
            # 单次普攻伤害
            dmg_per_hit = calculate_arts_damage(buffed_atk, enemy.current_res)
            
            total_damage = num_attacks * dmg_per_hit
            dps = dmg_per_hit / buffed_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (笑鸣瑟)：瞬发，对攻击范围内两名敌人造成450%攻击力的法术伤害
            # 瞬发技能，总伤即为爆发伤害
            atk_multiplier = 4.50
            burst_atk_val = self.final_base_atk * atk_multiplier
            
            total_damage = calculate_arts_damage(burst_atk_val, enemy.current_res)
            
            # 瞬发技能的DPS计算方式：总伤除以干员的攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (宁作吾)：持续30秒，自身与召唤物攻击力+100%，防御力+100%
            # 召唤物造成的持续伤害不计入令自身的伤害计算
            duration = 30
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + 1.00)
            
            # 技能持续期间的普攻次数 (令的攻速未受此技能影响，仍使用基础攻速)
            num_attacks = duration / actual_atk_interval
            
            # 单次普攻伤害
            dmg_per_hit = calculate_arts_damage(buffed_atk, enemy.current_res)
            
            total_damage = num_attacks * dmg_per_hit
            dps = dmg_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)