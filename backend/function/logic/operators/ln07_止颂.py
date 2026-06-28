from backend.function.logic.professions import Dreadnought
from backend.function.logic.formulas import calculate_physical_damage

class Ln07止颂(Dreadnought):
    """
    干员：止颂
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：苦痛专注 (阻挡时，受到来自非自身阻挡敌人的物理和法术伤害降低35%)
        # 此天赋为防御性天赋，不直接提高干员的输出伤害，故不在此处实现。
        
        # 天赋 2：痛楚砺刃 (受到伤害后，攻击力+12%，持续15秒（不可叠加）)
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑。
        # 假设此天赋在计算最大伤害时常驻触发。
        self.final_base_atk *= (1 + 0.12)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望伤害。
        止颂的普攻没有特殊机制（如无视防御、法术伤害等），直接计算物理伤害。
        """
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (强力击·γ型)：下次攻击的攻击力提高至290%
            # 这是一个瞬发技能，只计算一次强化攻击的伤害
            skill_atk_multiplier = 2.90
            atk_val = self.final_base_atk * skill_atk_multiplier
            
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发技能的DPS计算方式：总伤 / 实际攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (虔修对决)：部署后，第一天赋效果提升至2.2倍，攻击力+60%，攻击变为2连击
            # 持续时间：24秒
            duration = 24
            
            # 第一天赋效果提升不影响输出伤害，故不在此处实现。
            
            # 攻击力+60%
            atk_buff_multiplier = 1 + 0.60
            
            # 攻击变为2连击 (对单个目标造成两次伤害)
            hits_per_attack = 2
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_buff_multiplier
            
            # 单次命中伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 每次攻击的总伤害（考虑连击，仍是对单个目标）
            damage_per_attack = single_hit_damage * hits_per_attack
            
            # 技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval
            
            # 技能总伤害
            total_damage = num_attacks * damage_per_attack
            # 技能期间DPS
            dps = damage_per_attack / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (苦修破誓)：自身免疫异常状态，生命值+110%，攻击被阻挡目标时，造成相当于攻击力220%的物理伤害
            # 持续时间：20秒
            duration = 20
            
            # 攻击被阻挡目标时，造成相当于攻击力220%的物理伤害
            # 这意味着每次攻击的倍率是220%
            skill_atk_multiplier = 2.20
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 单次命中伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval
            
            # 技能总伤害
            total_damage = num_attacks * single_hit_damage
            # 技能期间DPS
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)