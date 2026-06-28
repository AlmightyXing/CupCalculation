from backend.function.logic.professions import Executor
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Pl07缄默德克萨斯(Executor):
    """
    干员：缄默德克萨斯
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1: 德克萨斯传统 (被动技能持续时间内攻击力+20%)
        # 此天赋为技能期间的攻击力加成，将在 calculate_skill_damage 中应用。
        # 不在此处直接修改干员面板属性。

        # 天赋 2: 德克萨斯剑术 (每次部署后击倒一名敌人之前，攻击速度+8)
        # 假设此天赋在计算最大伤害时始终处于激活状态。
        self.attack_speed += 8
        # "受到的所有伤害降低25%" 为防御性天赋，不影响伤害计算，故忽略。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 处决者干员的普攻为物理伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 天赋 1: 德克萨斯传统 (被动技能持续时间内攻击力+20%)
        # 此加成适用于所有技能的伤害计算。
        talent_1_atk_multiplier = 1.20 # 1 + 0.20
        
        # 存储敌人原始法术抗性，以便在技能2计算后恢复
        original_enemy_res = enemy.current_res

        if skill_index == 0:
            # 技能 1 (细雨无声)
            # 描述: "部署后攻击力+70%，攻击使命中目标失去特殊能力10秒，期间目标每秒受到400点法术伤害"
            
            # 计算技能期间普攻的强化攻击力
            skill_atk_multiplier = 1.70 # 1 + 0.70
            enhanced_atk = self.final_base_atk * skill_atk_multiplier * talent_1_atk_multiplier
            
            # 技能1期间普攻为物理伤害 (未另行说明)
            normal_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 额外每秒法术伤害
            flat_arts_dps = 400
            
            # 此为永续增益类技能 (duration: null)
            # total_damage = 0 (根据规则)
            # dps = (强化普攻伤害 / 实际攻击间隔) + 额外每秒法术伤害
            
            dps = (normal_hit_damage / actual_atk_interval) + flat_arts_dps
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (阵雨连绵)
            # 描述: "部署后立即对周围所有敌人造成相当于攻击力240%的法术伤害，并使命中目标在10秒内法术抗性-30%；攻击力+55%，攻击变为二连击并造成法术伤害"
            
            # 1. 计算瞬发爆发伤害
            # 爆发伤害使用基础攻击力 + 天赋1加成，再乘以爆发倍率。
            # 技能自身的攻击力+55%是针对后续普攻的，不影响瞬发爆发。
            burst_base_atk_for_calc = self.final_base_atk * talent_1_atk_multiplier
            burst_atk_value = burst_base_atk_for_calc * 2.40
            burst_damage = calculate_arts_damage(burst_atk_value, enemy.current_res)
            
            # 2. 应用法术抗性Debuff，用于后续持续伤害计算
            # 假设Debuff在持续伤害开始前生效，且由于技能永续，Debuff也视为永续。
            enemy.current_res = max(0, enemy.current_res - 30) # 固定值减法抗
            
            # 3. 计算持续DPS
            skill_atk_multiplier = 1.55 # 1 + 0.55
            enhanced_atk_for_continuous = self.final_base_atk * skill_atk_multiplier * talent_1_atk_multiplier
            
            # 攻击变为二连击并造成法术伤害
            single_hit_arts_damage = calculate_arts_damage(enhanced_atk_for_continuous, enemy.current_res)
            continuous_attack_damage = single_hit_arts_damage * 2 # 二连击
            
            # 恢复敌人原始法术抗性
            enemy.current_res = original_enemy_res
            
            # total_damage = 瞬发爆发伤害 (根据规则)
            # dps = 持续攻击伤害 / 实际攻击间隔
            
            dps = continuous_attack_damage / actual_atk_interval
            return {"total_damage": burst_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (剑雨滂沱)
            # 描述: "部署后立即对周围所有敌人造成两次相当于攻击力165%的法术伤害并使目标晕眩2秒，之后每秒释放剑雨攻击范围内最多4个不同的目标，造成攻击力130%的法术伤害和0.2秒晕眩"
            
            # 1. 计算瞬发爆发伤害
            # 爆发伤害使用基础攻击力 + 天赋1加成，再乘以爆发倍率。
            burst_base_atk_for_calc = self.final_base_atk * talent_1_atk_multiplier
            burst_atk_value = burst_base_atk_for_calc * 1.65
            burst_damage = calculate_arts_damage(burst_atk_value, enemy.current_res) * 2 # 两次伤害
            
            # 2. 计算持续DPS (剑雨)
            # 这是独立的每秒伤害，不与干员攻击间隔挂钩。
            # 剑雨伤害使用基础攻击力 + 天赋1加成，再乘以剑雨倍率。
            sword_rain_base_atk_for_calc = self.final_base_atk * talent_1_atk_multiplier
            sword_rain_atk_value = sword_rain_base_atk_for_calc * 1.30
            sword_rain_damage_per_hit = calculate_arts_damage(sword_rain_atk_value, enemy.current_res)
            
            # "每秒释放剑雨" -> 此伤害即为每秒的DPS贡献
            # "最多4个不同的目标" -> 根据规则，只计算单个目标的伤害。
            continuous_dps = sword_rain_damage_per_hit
            
            # total_damage = 瞬发爆发伤害
            # dps = 持续剑雨伤害
            
            return {"total_damage": burst_damage, "dps": continuous_dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)