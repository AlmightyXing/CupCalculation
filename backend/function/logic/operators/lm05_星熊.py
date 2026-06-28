from backend.function.logic.professions import Protector
from backend.function.logic.formulas import calculate_physical_damage

class Lm05星熊(Protector):
    """
    干员：星熊
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 星熊的天赋 "战术装甲" (25%概率伤害抵挡) 和 "特种作战策略" (友方重装防御+6%)
        # 均不直接提升星熊自身的攻击力或伤害输出，因此在计算星熊自身伤害时无需额外处理。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 星熊普攻无特殊机制，直接计算物理伤害。
        # Protector父类没有覆写calculate_normal_hit，因此直接计算物理伤害是符合预期的。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (战意): 防御力+80%，攻击力+40%，持续30秒
            duration = 30
            atk_multiplier = 1.40 # 攻击力+40%
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的普攻次数
            num_hits = duration / actual_atk_interval
            
            # 计算单次强化普攻伤害
            dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (荆棘): 防御力+30%，每次受到攻击时对目标造成相当于星熊攻击力100%的物理伤害 (永续)
            # 这是一个永续技能，且其伤害为反击伤害，不属于星熊主动攻击造成的伤害。
            # 根据规则，永续技能 total_damage = 0，dps 为强化后的单次普攻伤害 / actual_atk_interval。
            # 此技能不提升星熊的攻击力或攻击速度，因此dps与普攻相同。
            total_damage = 0.0
            dps = calculate_physical_damage(self.final_base_atk, enemy.current_def) / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (力之锯): 攻击力+140%，防御力+90%，对前方一格的所有敌人使用盾牌进行切割，持续25秒
            duration = 25
            atk_multiplier = 1 + 1.40 # 攻击力+140%
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的普攻次数
            num_hits = duration / actual_atk_interval
            
            # 计算单次强化普攻伤害 (即使是范围攻击，也只计算对单个目标的伤害)
            dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果没有匹配的技能，调用父类的默认处理
        return super().calculate_skill_damage(enemy, skill_index, target_count)
