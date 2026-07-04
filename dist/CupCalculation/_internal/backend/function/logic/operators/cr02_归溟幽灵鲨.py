from backend.function.logic.professions import Dollkeeper
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Cr02归溟幽灵鲨(Dollkeeper):
    """
    干员：归溟幽灵鲨
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：拥抱自我 (<替身>使周围敌人移动速度-40%且每秒造成相当于40%攻击力的法术伤害)
        # 这个天赋描述的是替身形态下的效果，且是持续法术伤害，不直接影响本体的普攻或技能物理伤害计算。
        # 因此，不在此处修改本体的攻击力或攻击计算逻辑。
        # 如果需要计算替身伤害，应在单独的逻辑中处理，此处仅关注干员本体的攻击。
        self.substitute_arts_damage_ratio = 0.40 # 存储天赋数值，以备后续扩展
        
        # 天赋 2：阿戈尔的深邃 (编入队伍时，所有【深海猎人】干员的生命值+20%)
        # 这是队伍光环，不影响归溟幽灵鲨自身的攻击伤害计算。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 归溟幽灵鲨的普攻没有特殊机制（如无视防御、连击等），直接调用父类的普攻计算
        # Dollkeeper (傀儡师) 没有覆写 calculate_normal_hit，因此会调用 Operator 的默认物理伤害计算
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS和总伤
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (生存的技巧)：自身攻击力+150%，持续25秒
            duration = 25
            atk_multiplier = 1 + 1.50 # 攻击力+150%
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的单次普攻伤害
            damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (生存的渴望)：攻击力+130%，攻击速度+50，持续20秒
            duration = 20
            atk_multiplier = 1 + 1.30 # 攻击力+130%
            atk_speed_buff = 50
            
            # 计算技能期间的实际攻击速度和攻击间隔
            temp_attack_speed = self.attack_speed + atk_speed_buff
            # 确保攻击速度不会低于1，避免除以零或负数
            if temp_attack_speed <= 0:
                temp_attack_speed = 1 
            temp_actual_atk_interval = self.attack_interval * 100 / temp_attack_speed
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的单次普攻伤害
            damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            hits_during_skill = duration / temp_actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / temp_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (生存的重压)：攻击间隔延长(+1.0)，攻击力+260%，攻击生命比例高于或等于自身的敌人时额外造成一次攻击力70%的物理伤害，持续25秒
            duration = 25
            atk_interval_increase = 1.0
            atk_multiplier = 1 + 2.60 # 攻击力+260%
            extra_hit_ratio = 0.70 # 额外造成一次攻击力70%的物理伤害
            
            # 计算技能期间的实际攻击间隔
            temp_attack_interval = self.attack_interval + atk_interval_increase
            # 攻击速度未变，只变了基础间隔，所以用self.attack_speed
            temp_actual_atk_interval = temp_attack_interval * 100 / self.attack_speed 
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算单次普攻的基础伤害
            base_damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算额外伤害 (假设条件满足，即敌人生命比例高于或等于自身)
            # 额外伤害的攻击力基于强化后的攻击力 (通常技能描述中的"攻击力X%"指当前攻击力)
            extra_hit_atk_val = enhanced_atk * extra_hit_ratio
            extra_damage_per_hit = calculate_physical_damage(extra_hit_atk_val, enemy.current_def)
            
            # 单次攻击循环的总伤害 (基础伤害 + 额外伤害)
            total_damage_per_attack_cycle = base_damage_per_hit + extra_damage_per_hit
            
            # 计算技能期间能打出的普攻次数
            hits_during_skill = duration / temp_actual_atk_interval
            
            total_damage = hits_during_skill * total_damage_per_attack_cycle
            dps = total_damage_per_attack_cycle / temp_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
