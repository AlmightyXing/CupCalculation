from backend.function.logic.professions import Artificer
from backend.function.logic.formulas import calculate_physical_damage

class Vc17白铁(Artificer):
    """
    干员：白铁
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：战地工程师 (可以携带3个<支援装置>(最多可部署2个)，效果根据技能改变而改变)
        # 此天赋主要影响装置的部署和效果，不直接修改白铁自身的攻击力、攻速等面板属性。
        # 装置的效果在技能中体现，因此此处无需对白铁自身属性进行修改。
        pass
        
        # 天赋 2：节约经费 (当白铁周围8格的自身装置损毁时，有70%的几率回收使白铁额外获得1个装置)
        # 此天赋为资源管理类天赋，不直接修改白铁自身的攻击力、攻速等面板属性。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 白铁的普攻没有特殊机制，直接计算物理伤害
        # Artificer (工匠) 职业本身没有普攻伤害倍率，因此直接计算即可。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (极致火力)：攻击造成相当于200%的物理伤害
            # 这是一个瞬发爆发伤害技能。
            # 技能描述中的“装置使一名我方干员的攻击力+12%”和“装置效果提升至4倍”
            # 均不影响白铁自身的伤害计算。
            
            atk_val = self.final_base_atk * 2.0
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发技能的DPS计算方式：总伤除以一次普攻的间隔
            dps = total_damage / actual_atk_interval 
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (高效补给)：攻击力+60%，防御力+60%，攻击所有阻挡的敌人
            # 这是一个持续增益技能。
            
            duration = 30 # seconds
            atk_buff_ratio = 0.60
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能期间的单次普攻伤害
            damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            hits_during_skill = duration / actual_atk_interval
            
            # 计算总伤害
            total_damage = hits_during_skill * damage_per_hit
            
            # 计算DPS
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (铁钳号·原型机)：攻击力+55%，攻击速度+55
            # 这是一个持续增益技能，同时提升攻击力和攻击速度。
            
            duration = 30 # seconds
            atk_buff_ratio = 0.55
            atk_speed_buff = 55
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算强化后的攻击速度和实际攻击间隔
            temp_atk_speed = self.attack_speed + atk_speed_buff
            # 避免除以零或负数，虽然游戏数据通常不会出现
            if temp_atk_speed <= 0: 
                temp_atk_speed = 1 # Fallback to a small positive value
            temp_actual_atk_interval = self.attack_interval * 100 / temp_atk_speed
            
            # 计算技能期间的单次普攻伤害
            damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            hits_during_skill = duration / temp_actual_atk_interval
            
            # 计算总伤害
            total_damage = hits_during_skill * damage_per_hit
            
            # 计算DPS
            dps = damage_per_hit / temp_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
