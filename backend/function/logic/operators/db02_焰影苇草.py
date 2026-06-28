from backend.function.logic.professions import CurseHealer
from backend.function.logic.formulas import calculate_arts_damage

class Db02焰影苇草(CurseHealer):
    """
    干员：焰影苇草
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：灼痕 (造成伤害时有30%概率对敌人施加灼痕效果：30%的【法术脆弱】)
        # 【法术脆弱】意味着敌人受到法术伤害时，最终伤害会乘以 (1 + 脆弱比例)。
        # 这里我们只考虑对伤害计算有直接影响的“30%的【法术脆弱】”。
        self.talent_1_prob = 0.3  # 触发灼痕的概率
        self.talent_1_res_fragility = 0.3 # 30%法术脆弱，即最终伤害 * 1.3
        
        # 天赋 2：映耀 (治疗其他友方单位时，焰影苇草同时享受50%的治疗量)
        # 此天赋影响自身治疗量，不影响对敌人的伤害输出，因此在此处不进行数值修改。
        
    def _calc_arts_hit(self, atk_val: float, enemy, prob_override: float = None, res_fragility_override: float = None) -> float:
        """
        计算单次命中时的期望法术伤害（考虑灼痕天赋的法术脆弱概率）
        """
        current_prob = prob_override if prob_override is not None else self.talent_1_prob
        current_res_fragility = res_fragility_override if res_fragility_override is not None else self.talent_1_res_fragility
        
        # 计算未触发脆弱时的基础法术伤害
        dmg_normal = calculate_arts_damage(atk_val, enemy.current_res)
        
        # 计算触发脆弱时的法术伤害 (脆弱效果通常是最终伤害乘区)
        dmg_fragile = dmg_normal * (1 + current_res_fragility)
        
        # 返回期望伤害
        return current_prob * dmg_fragile + (1 - current_prob) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 焰影苇草的普攻造成法术伤害，并考虑天赋“灼痕”的概率触发法术脆弱
        # CurseHealer特性为“攻击造成法术伤害”，因此这里直接计算法术伤害是正确的。
        # CurseHealer本身没有对普攻伤害进行额外乘算或多段攻击的特性，所以无需super().calculate_normal_hit()
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算技能期间的普攻次数和DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (迅捷打击·γ型)：攻击力+45%，攻击速度+45，持续35秒
            duration = 35
            atk_multiplier = 1.45 # 攻击力+45%
            as_bonus = 45       # 攻击速度+45
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            # 计算技能期间的强化攻击速度
            enhanced_attack_speed = self.attack_speed + as_bonus
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = duration / skill_actual_atk_interval
            
            # 计算单次强化普攻的期望伤害（考虑天赋“灼痕”的概率）
            dmg_per_hit = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 计算总伤害和DPS
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (枯荣共息)：优先使两名部署在地面的干员获得三颗火球，效果如下：
            # 每1.5秒对一名敌人造成相当于焰影苇草240%攻击力的法术伤害并仅对该干员触发焰影苇草特性
            # 此技能描述的是其他干员获得火球并造成伤害，并非焰影苇草自身直接造成伤害。
            # 因此，焰影苇草在此技能期间的直接伤害输出为0。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (生命火种)：同时攻击两名敌人，攻击力+60%，第一天赋触发几率提升至100%，
            # 技能期间附带灼痕效果的敌人每秒受到60%焰影苇草攻击力的法术伤害、
            # 被击倒时对周围敌人造成140%焰影苇草攻击力的法术伤害并施加灼痕效果，灼痕效果持续至技能结束
            duration = 30
            atk_multiplier = 1.60 # 攻击力+60%
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 技能期间，第一天赋“灼痕”触发几率提升至100%
            skill_talent_1_prob = 1.0
            
            # 1. 计算技能期间普攻造成的伤害
            # 由于天赋100%触发，每次普攻都将享受30%法术脆弱效果
            dmg_per_hit = self._calc_arts_hit(
                enhanced_atk, 
                enemy, 
                prob_override=skill_talent_1_prob, 
                res_fragility_override=self.talent_1_res_fragility
            )
            num_hits = duration / actual_atk_interval
            normal_attack_total_dmg = num_hits * dmg_per_hit
            
            # 2. 计算技能期间附带的灼痕DoT伤害
            # "每秒受到60%焰影苇草攻击力的法术伤害"
            dot_atk_val = enhanced_atk * 0.60
            # DoT伤害同样享受100%触发的30%法术脆弱效果
            dot_dmg_per_sec = self._calc_arts_hit(
                dot_atk_val, 
                enemy, 
                prob_override=skill_talent_1_prob, 
                res_fragility_override=self.talent_1_res_fragility
            )
            total_dot_dmg = dot_dmg_per_sec * duration
            
            # "被击倒时对周围敌人造成140%焰影苇草攻击力的法术伤害" 属于击杀触发伤害，
            # 通常不计入常规的总伤和DPS计算，因为它依赖于敌人被击倒这一特定条件。
            
            # 计算总伤害和DPS
            total_damage = normal_attack_total_dmg + total_dot_dmg
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
