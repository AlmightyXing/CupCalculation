from backend.function.logic.professions import Centurion
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Re41煌(Centurion):
    """
    干员：煌
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：紧急除颤 (生存天赋，不影响伤害输出，忽略)
        # 天赋 2：严酷训练 (生存/控制天赋，不影响伤害输出，忽略)
        # 煌的两个天赋均不直接提供攻击力、攻击速度或伤害倍率加成，因此在伤害计算中无需修改任何属性。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 煌作为强攻手，普攻同时攻击阻挡的所有敌人，但伤害计算只针对单个目标。
        # 强攻手父类Centurion没有特殊的普攻伤害倍率，因此直接计算物理伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 攻速计算会使用父类Centurion设定的attack_interval (1.2)
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (强力击·γ型)：下次攻击的攻击力提高至290%
            # 这是一个瞬发伤害技能，只计算一次强化普攻的伤害。
            atk_val = self.final_base_atk * 2.90
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (链锯延伸模块)：攻击力+100%，防御力+35%，攻击距离加长
            # 这是一个永续技能 (duration=null，视为永久增益)。
            # 对于永续技能，total_damage 为 0，重点是返回正确的 dps。
            
            atk_multiplier = 1 + 1.00 # 攻击力+100%
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            return {"total_damage": 0, "dps": single_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (沸腾爆裂)：
            # 技能开启后，攻击力和防御力逐渐增至+80% (计算时按最终值+80%处理)
            # 持续10秒，期间进行普攻。
            # 技能结束时对附近所有敌人造成此时攻击力400%的物理伤害 (爆发伤害)。
            
            duration = 10
            atk_buff_ratio = 0.80 # 攻击力+80%
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能期间普攻造成的总伤害
            single_hit_damage_during_skill = calculate_physical_damage(enhanced_atk, enemy.current_def)
            num_attacks = (duration or 0) / actual_atk_interval
            damage_from_attacks = num_attacks * single_hit_damage_during_skill
            
            # 计算技能结束时的爆发伤害
            # 爆发伤害使用强化后的攻击力
            burst_atk_val = enhanced_atk * 4.00 
            burst_damage = calculate_physical_damage(burst_atk_val, enemy.current_def)
            
            # 总伤害为普攻伤害与爆发伤害之和
            total_damage = damage_from_attacks + burst_damage
            # DPS 为总伤害除以技能持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
