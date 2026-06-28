from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_arts_damage

class Rl10淬羽赫默(UnknownProfession):
    """
    干员：淬羽赫默
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1: 无声砥柱 (防御/治疗天赋，不直接提升自身伤害)
        # 天赋 2: 丰润羽翼 (治疗天赋，不直接提升自身伤害)
        # 淬羽赫默的天赋均不直接提升自身伤害，因此此处无需修改攻击力、攻击速度等属性。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 淬羽赫默的攻击造成法术伤害
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS和技能期间普攻次数
        # 注意：self.attack_speed 包含了天赋带来的攻速加成（如果有的话）
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (进取之心)：攻击力+80%，持续25秒
            duration = 25
            atk_multiplier = 1.80 # 1 + 80%
            
            # 技能期间的强化攻击力
            buffed_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的普攻次数
            hits_during_skill = duration / actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_damage = calculate_arts_damage(buffed_atk, enemy.current_res)
            
            total_damage = hits_during_skill * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (俯瞰视界)：攻击速度+60，持续12秒
            duration = 12
            atk_speed_buff = 60
            
            # 计算技能期间的实际攻击速度
            skill_atk_speed = self.attack_speed + atk_speed_buff
            skill_actual_atk_interval = self.attack_interval * 100 / skill_atk_speed
            
            # 技能期间攻击力无加成
            buffed_atk = self.final_base_atk
            
            # 计算技能期间的普攻次数
            hits_during_skill = duration / skill_actual_atk_interval
            
            # 计算单次强化普攻的伤害 (这里只有攻速提升，攻击力不变)
            single_hit_damage = calculate_arts_damage(buffed_atk, enemy.current_res)
            
            total_damage = hits_during_skill * single_hit_damage
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (无畏者协议)：攻击力+30%，持续60秒
            duration = 60
            atk_multiplier = 1.30 # 1 + 30%
            
            # 技能期间的强化攻击力
            buffed_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的普攻次数
            hits_during_skill = duration / actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_damage = calculate_arts_damage(buffed_atk, enemy.current_res)
            
            total_damage = hits_during_skill * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)