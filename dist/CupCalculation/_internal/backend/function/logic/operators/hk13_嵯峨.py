from backend.function.logic.professions import Pioneer
from backend.function.logic.formulas import calculate_physical_damage

class Hk13嵯峨(Pioneer):
    """
    干员：嵯峨
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：劝善
        # "造成致命伤害时使敌人保留1点生命并使其重伤（击杀者技力+2）；嵯峨不攻击重伤单位"
        # 此天赋主要影响敌方状态和友方技力回复，不直接提升嵯峨自身的伤害输出或修改其攻击属性。
        # 根据规则，只考虑对提高伤害有帮助的天赋。因此，此处不进行数值修改。

        # 天赋 2：清明
        # "生命值低于40%时，仅一次获得70%物理闪避和每秒回复5%的最大生命，持续15秒"
        # 此天赋为防御/生存向天赋，不直接提升嵯峨的伤害输出。
        # 根据规则，只考虑对提高伤害有帮助的天赋。因此，此处不进行数值修改。
        pass
        
    # 嵯峨的普攻为物理伤害，无特殊天赋修改普攻伤害。
    # Pioneer（尖兵）职业本身没有特殊的普攻伤害特性，因此继承Operator的默认物理伤害计算即可。
    # 此处无需覆写 calculate_normal_hit 方法。

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算瞬发技能的DPS或永续技能的DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (冲锋号令·γ型): 立即获得12点部署费用
            # 纯粹的费用回复技能，不造成伤害。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (除恶): 立即获得4点部署费用；对十字范围内最多6名地面敌人造成相当于攻击力400%的物理伤害
            # 瞬发伤害技能。
            # "对十字范围内最多6名地面敌人" - 根据规则，严禁将最终伤害乘以目标数，只计算对单个目标的伤害。
            
            # 计算技能爆发伤害的攻击力
            skill_atk_val = self.final_base_atk * 4.0
            
            # 计算单次爆发对单个敌人的伤害
            total_damage = calculate_physical_damage(skill_atk_val, enemy.current_def)
            
            # 瞬发伤害技能的DPS计算方式
            dps = total_damage / actual_atk_interval
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (怒目): 技能持续时间内逐渐获得20点部署费用，攻击间隔稍微增大(+0.5s)，攻击距离+1，攻击力+130%，同时攻击阻挡的所有敌人，目标生命值低于一半时额外追加一次攻击
            duration = 20 # 技能持续时间
            
            # 技能期间攻击间隔修改: "攻击间隔稍微增大(+0.5s)"
            skill_base_atk_interval = self.attack_interval + 0.5
            skill_actual_atk_interval = skill_base_atk_interval * 100 / self.attack_speed
            
            # 技能期间攻击力增益: "攻击力+130%"
            skill_atk_multiplier = 1 + 1.30
            skill_final_atk = self.final_base_atk * skill_atk_multiplier
            
            # "目标生命值低于一半时额外追加一次攻击"
            # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑”，此处假设额外攻击条件满足，每次攻击视为造成2次伤害。
            hits_per_attack = 2
            
            # 计算技能期间单次普攻（包含额外攻击）对单个敌人的伤害
            single_attack_damage = calculate_physical_damage(skill_final_atk, enemy.current_def) * hits_per_attack
            
            # 计算技能持续期间能打出的普攻次数
            num_attacks = duration / skill_actual_atk_interval
            
            # 计算技能期间的总伤害
            total_damage = num_attacks * single_attack_damage
            
            # 计算技能期间的DPS
            dps = single_attack_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
