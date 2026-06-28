from backend.function.logic.professions import Operator # 史尔特尔是术战者，但为通用性，继承自Operator基类
from backend.function.logic.formulas import calculate_arts_damage

class R111史尔特尔(Operator):
    """
    干员：史尔特尔
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：熔火 (无视攻击目标20法术抗性)
        # 史尔特尔的攻击造成法术伤害，此天赋直接降低敌方法术抗性
        self.arts_res_ignore = 20
        
        # 天赋 2：余烬 (受到致命伤害时持续使生命值不低于1，8秒后强制退出战场)
        # 此天赋影响生存能力，不直接提高伤害输出，故不纳入伤害计算逻辑。
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑熔火天赋的无视法术抗性）
        """
        # 史尔特尔的攻击造成法术伤害
        # 实际生效的法术抗性 = 敌方法术抗性 - 天赋无视抗性，但不能低于0
        effective_res = max(0, enemy.current_res - self.arts_res_ignore)
        return calculate_arts_damage(atk_val, effective_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 史尔特尔的普攻造成法术伤害，并享受天赋的法术抗性无视
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，考虑攻速加成（史尔特尔天赋无攻速加成，但技能可能影响）
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (烈焰魔剑)：下次攻击的攻击力提升至310%
            # 这是一个单次强化攻击技能，立即造成爆发伤害
            atk_multiplier = 3.10
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            total_damage = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 对于单次爆发伤害技能，DPS = 总伤 / 实际攻击间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (熔核巨影)：
            # 攻击力+120%，攻击距离+1，攻击目标数+1，仅攻击到一个敌人时对其攻击力提升至160%
            # 持续时间：18秒
            
            skill_duration = 18
            
            # 技能描述通常是叠加的，"攻击力+120%"是一个基础加成。
            # "仅攻击到一个敌人时对其攻击力提升至160%"通常意味着在单目标情况下，
            # 攻击力加成从120%变为160%（即额外增加40%）。
            # 所以总攻击力加成是 160%。
            atk_buff_multiplier = 1 + 1.60 # 最终攻击力 = 基础攻击力 * (1 + 160%) = 基础攻击力 * 2.60
            enhanced_atk = self.final_base_atk * atk_buff_multiplier
            
            single_hit_damage = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = skill_duration / actual_atk_interval
            
            total_damage = single_hit_damage * num_hits
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (黄昏)：
            # 立即恢复所有生命；攻击力+330%，攻击距离+2，攻击目标数+3，生命上限+5000，逐渐失去生命...；持续时间无限
            # 这是一个永续技能，总伤害为0，重点计算DPS。
            
            atk_buff_multiplier = 1 + 3.30 # 攻击力+330% -> 乘数 4.30
            enhanced_atk = self.final_base_atk * atk_buff_multiplier
            
            single_hit_damage = self._calc_arts_hit(enhanced_atk, enemy)
            
            total_damage = 0 # 永续技能的总伤害为0
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果没有匹配的技能，调用基类的处理
        return super().calculate_skill_damage(enemy, skill_index, target_count)