from backend.function.logic.professions import HeavyShooter
from backend.function.logic.formulas import calculate_physical_damage

class Ss02黑(HeavyShooter):
    """
    干员：黑
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：破甲箭头
        # 攻击时，20%几率当次攻击的攻击力提升至160%，并使命中目标的防御力下降20%
        self.talent1_base_prob = 0.2
        self.talent1_atk_mult = 1.6
        self.talent1_def_reduc = 0.2
        
        # 天赋 2：交叉火力
        # 场上存在黑和另外至少一名【狙击】干员时，所有【狙击】干员的攻击力+8%
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑。
        # 假设条件满足，直接将攻击力加成应用到自身。
        self.final_base_atk *= (1 + 0.08)
        
    def _calc_expected_physical_hit(self, atk_val: float, enemy, talent_prob_override: float = None) -> float:
        """
        计算单次物理命中时的期望伤害，考虑“破甲箭头”天赋的概率触发。
        talent_prob_override: 如果技能修改了天赋触发概率，则传入此值。
        """
        current_talent_prob = talent_prob_override if talent_prob_override is not None else self.talent1_base_prob
        
        # 触发天赋时的伤害计算
        # 攻击力提升至160%，防御力下降20%
        atk_on_proc = atk_val * self.talent1_atk_mult
        def_on_proc = enemy.current_def * (1 - self.talent1_def_reduc)
        dmg_on_proc = calculate_physical_damage(atk_on_proc, def_on_proc)
        
        # 未触发天赋时的伤害计算
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 期望伤害 = 触发概率 * 触发伤害 + (1 - 触发概率) * 未触发伤害
        return current_talent_prob * dmg_on_proc + (1 - current_talent_prob) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻时使用最终基础攻击力和天赋的基础触发概率
        return self._calc_expected_physical_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (强弩)：下一次攻击的攻击力提高至220%，且天赋发动概率提高至80%
            # 这是一个“下一次攻击”的瞬发技能
            skill_atk_multiplier = 2.20
            skill_talent_prob = 0.80
            
            # 强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次强化攻击的期望伤害
            total_damage = self._calc_expected_physical_hit(enhanced_atk, enemy, skill_talent_prob)
            
            # 瞬发技能的DPS为总伤除以一次攻击间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (暮眼锐瞳)：攻击力+130%，天赋的发动概率提高至50%
            # 持续时间：40秒
            skill_duration = 40
            skill_atk_bonus_ratio = 1.30 # +130% 意味着攻击力变为 (1 + 1.30) 倍
            skill_talent_prob = 0.50
            
            # 强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + skill_atk_bonus_ratio)
            
            # 计算单次强化攻击的期望伤害
            single_hit_damage = self._calc_expected_physical_hit(enhanced_atk, enemy, skill_talent_prob)
            
            # 技能持续期间的攻击次数
            hits_during_skill = skill_duration / actual_atk_interval
            
            # 总伤害 = 单次伤害 * 攻击次数
            total_damage = single_hit_damage * hits_during_skill
            
            # DPS = 单次伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (战术的终结)：攻击范围改为前方4格，攻击间隔略微增大(+0.4)，攻击力+180%，天赋的发动概率提高至100%
            # 持续时间：25秒
            skill_duration = 25
            skill_atk_bonus_ratio = 1.80 # +180% 意味着攻击力变为 (1 + 1.80) 倍
            skill_talent_prob = 1.00
            
            # 攻击间隔略微增大(+0.4)
            # 这意味着基础攻击间隔 (self.attack_interval) 增加0.4，然后才计算实际攻击间隔
            modified_base_atk_interval = self.attack_interval + 0.4
            skill_actual_atk_interval = modified_base_atk_interval * 100 / self.attack_speed
            
            # 强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + skill_atk_bonus_ratio)
            
            # 计算单次强化攻击的期望伤害
            single_hit_damage = self._calc_expected_physical_hit(enhanced_atk, enemy, skill_talent_prob)
            
            # 技能持续期间的攻击次数
            hits_during_skill = skill_duration / skill_actual_atk_interval
            
            # 总伤害 = 单次伤害 * 攻击次数
            total_damage = single_hit_damage * hits_during_skill
            
            # DPS = 单次伤害 / 实际攻击间隔
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)