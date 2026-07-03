from backend.function.logic.professions import Protector
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Nm01年(Protector):
    """
    干员：年
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：积甲成山 (编入队伍时，所有【重装】职业干员的生命上限+16%)
        # 此天赋为团队生命上限加成，不影响年自身的伤害输出，故不在此处实现。
        
        # 天赋 2：干明可鉴 (部署后立即获得3层护盾，每层护盾可以抵挡一次伤害)
        # 此天赋为防御性天赋，不影响年自身的伤害输出，故不在此处实现。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 年的普攻是物理伤害，没有特殊机制（如无视防御、法术伤害转换等）
        # Protector基类没有覆写calculate_normal_hit，因此直接使用物理伤害计算公式即可。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (锡灼)：防御力+70%，攻击力+45%，普通攻击造成法术伤害
            duration = 30
            atk_multiplier = 1 + 0.45
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 技能期间普攻造成法术伤害
            single_hit_damage = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            num_attacks = (duration or 0) / actual_atk_interval
            total_damage = num_attacks * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (铜印)：停止攻击；防御力+130%，阻挡数+1，每次受到攻击时对目标造成相当于年攻击力90%的法术伤害并使其失去特殊能力5秒
            # 年在此技能期间停止攻击，其自身主动造成的伤害为0。
            # 反击伤害取决于被攻击次数，不计入年自身主动输出的total_damage和dps。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (铁御)：攻击力+120%；周围其他友方干员的防御力+80%，阻挡数+1，并获得抵抗
            duration = 45
            atk_multiplier = 1 + 1.20
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 技能期间普攻仍为物理伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            num_attacks = (duration or 0) / actual_atk_interval
            total_damage = num_attacks * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果没有匹配的技能，则调用父类的默认处理
        return super().calculate_skill_damage(enemy, skill_index, target_count)
