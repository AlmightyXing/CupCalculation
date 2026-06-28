from backend.function.logic.professions import SentinelDefender
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Bs30涤火杰西卡(SentinelDefender):
    """
    干员：涤火杰西卡
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：灵活应变 (防御力+15%) - 影响自身防御力，不直接影响伤害输出，故不在此处体现
        # 天赋 2：蓄能释放 (技力回复) - 影响技能回转，不直接影响单次伤害或DPS，故不在此处体现
        pass # 涤火杰西卡的天赋不直接提供攻击力、攻速或特殊伤害类型加成
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 涤火杰西卡普攻为物理伤害，无特殊机制（如无视防御、连击等）
        # SentinelDefender 自身没有覆写此方法，因此直接计算物理伤害即可
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算基础实际攻击间隔 (考虑干员自身攻速，包括天赋加成)
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (坚守阵线)：永续技能
            # 描述：攻击力+70%，自身与机动盾牌防御力+70%，机动盾牌持续时间+30秒
            
            atk_multiplier = 1 + 0.70
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算强化后的单次普攻伤害
            enhanced_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 永续技能的总伤害为0，DPS为强化后的单次普攻伤害除以实际攻击间隔
            total_damage = 0.0
            dps = enhanced_hit_damage / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (掩蔽护卫)：持续15秒
            # 描述：攻击范围扩大，攻击力+75%，攻击间隔大幅缩小(-0.9)，获得75%的物理和法术闪避
            
            skill_duration = 15.0
            atk_multiplier = 1 + 0.75
            atk_interval_modifier = -0.9 # 攻击间隔缩小0.9秒
            
            # 计算技能期间的实际攻击间隔
            # 技能期间的 attack_interval = 基础 attack_interval + 技能修正值
            modified_attack_interval_base = self.attack_interval + atk_interval_modifier
            # 实际攻击间隔 = (修正后的 attack_interval) * 100 / self.attack_speed
            actual_atk_interval_s2 = modified_attack_interval_base * 100 / self.attack_speed
            
            # 强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 强化后的单次普攻伤害
            enhanced_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能持续期间能打出的普攻次数
            hits_during_skill = skill_duration / actual_atk_interval_s2
            
            # 总伤害 = 单次强化普攻伤害 * 普攻次数
            total_damage = enhanced_hit_damage * hits_during_skill
            # DPS = 单次强化普攻伤害 / 实际攻击间隔
            dps = enhanced_hit_damage / actual_atk_interval_s2
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (饱和迸射)：持续40秒，攻击装有20发弹药
            # 描述：攻击距离+1，攻击间隔增大(+0.6)，攻击力+310%，防御力+80%，机动盾牌防御力+170%；
            #       机动盾牌存在时，立刻向前发射一枚炮弹，命中或到达终点时对范围内所有敌人造成相当于攻击力250%的物理伤害，并使其晕眩6秒；
            #       攻击装有20发弹药，打完后结束（可随时停止技能）
            
            atk_multiplier = 1 + 3.10
            atk_interval_modifier = +0.6 # 攻击间隔增大0.6秒
            num_auto_attacks = 20 # 20发弹药
            
            # 1. 计算瞬发伤害 (根据规则，增益先触发，瞬发伤害使用强化后的攻击力)
            enhanced_atk_for_burst = self.final_base_atk * atk_multiplier
            # 瞬发伤害的攻击力倍率为250%
            initial_burst_damage = calculate_physical_damage(enhanced_atk_for_burst * 2.50, enemy.current_def)
            
            # 2. 计算后续20次普攻伤害
            # 技能期间的实际攻击间隔
            modified_attack_interval_base = self.attack_interval + atk_interval_modifier
            actual_atk_interval_s3 = modified_attack_interval_base * 100 / self.attack_speed
            
            # 强化后的攻击力 (与瞬发伤害相同)
            enhanced_atk_for_auto = self.final_base_atk * atk_multiplier
            
            # 强化后的单次普攻伤害 (每次攻击造成100%攻击力伤害)
            enhanced_auto_hit_damage = calculate_physical_damage(enhanced_atk_for_auto, enemy.current_def)
            
            # 20次普攻的总伤害
            total_auto_attack_damage = enhanced_auto_hit_damage * num_auto_attacks
            
            # 技能总伤害 = 瞬发伤害 + 20次普攻总伤害
            total_damage = initial_burst_damage + total_auto_attack_damage
            
            # 技能持续时间 = 20次普攻所需时间 (瞬发伤害通常不计入持续时间，因为它在技能开始时立即发生)
            skill_duration_s3 = actual_atk_interval_s3 * num_auto_attacks
            
            # DPS = 总伤害 / 技能持续时间
            dps = total_damage / skill_duration_s3
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
