from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class R159泥岩(UnknownProfession):
    """
    干员：泥岩
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：沃土予身 (护盾和生命回复，不直接影响伤害输出，故不在此处修改攻击属性)
        # 天赋 2：手足相惜 (受萨卡兹伤害降低，不直接影响伤害输出，故不在此处修改攻击属性)
        # 根据规则，只考虑对提高伤害有帮助的天赋。泥岩的两个天赋均不直接提高伤害。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 泥岩的普攻为物理伤害，且没有特殊机制（如无视防御、连击等）
        # 直接使用基础攻击力计算物理伤害
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        # self.attack_interval 是干员的基础攻击间隔时间 (atk_time)
        # self.attack_speed 是干员的攻击速度百分比 (默认为100)
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (防御力强化·γ型): 防御力+100%，持续40秒
            # 这是防御性技能，不提供伤害加成。
            # 根据规则，只计算对伤害有帮助的技能效果。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (岩崩锤): 下次攻击时回复自身6%的最大生命，对周围所有地面敌人造成相当于攻击力270%的物理伤害
            # 这是一个瞬发伤害技能，只计算单次爆发伤害。
            
            skill_atk_multiplier = 2.70 # 攻击力270%
            atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次爆发的物理伤害
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发伤害的DPS计算方式：总伤害 / 普攻实际攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (秽壤的血脉):
            # 技能开启后无法行动且不受到伤害10秒
            # 该状态结束后晕眩周围地面敌人5秒，攻击间隔缩短(-30%)，攻击力+140%，防御力+80%，攻击阻挡的所有敌人
            
            skill_duration = 30 # 技能总持续时间
            invincible_duration = 10 # 无法行动的持续时间
            
            # 实际造成伤害的持续时间
            damage_duration = skill_duration - invincible_duration
            
            # 如果没有伤害持续时间，则不造成伤害
            if damage_duration <= 0:
                return {"total_damage": 0.0, "dps": 0.0}
            
            # 攻击力加成：攻击力+140%
            skill_atk_multiplier = 1 + 1.40 
            boosted_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 攻击间隔缩短(-30%)
            # 新的实际攻击间隔 = 原始实际攻击间隔 * (1 - 0.3)
            skill3_actual_atk_interval = actual_atk_interval * (1 - 0.3)
            
            # 计算强化后的单次普攻伤害
            single_hit_damage_skill3 = calculate_physical_damage(boosted_atk_val, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            hits_during_skill = damage_duration / skill3_actual_atk_interval
            
            # 总伤害 = 普攻次数 * 单次强化普攻伤害
            total_damage = hits_during_skill * single_hit_damage_skill3
            
            # DPS = 单次强化普攻伤害 / 强化后的攻击间隔
            dps = single_hit_damage_skill3 / skill3_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)