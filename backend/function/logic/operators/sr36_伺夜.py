from backend.function.logic.professions import Tactician
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Sr36伺夜(Tactician):
    """
    干员：伺夜
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 职业特性：自身攻击援军阻挡的敌人时攻击力提升至150%
        # 为计算最大伤害潜力，我们假设敌人总是被狼群阻挡，因此此特性常驻。
        # 注意：此乘数会在 _calc_hit 方法中应用，确保不会与父类重复计算。
        self.atk_multiplier_on_blocked = 1.5 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：狼群领袖
        # "可以在战术点召唤由初始两只“狼影”构成的狼群协助作战，“狼影”的数量每25秒增加一只（至多3只；每只“狼影”使狼群阻挡数+1且攻击额外造成一次伤害）"
        # 此天赋主要影响狼群的召唤和数量，对伺夜自身伤害计算无直接数值加成。
        # 但其存在是天赋2和职业特性（攻击力提升150%）生效的前提，我们已在__init__中假设敌人被阻挡。

        # 天赋 2：狼群天性
        # "敌人被狼群阻挡时，伺夜和狼群对其的攻击无视其175防御力"
        # 为计算最大伤害潜力，我们假设敌人被狼群阻挡，因此此防御力无视常驻。
        self.def_ignore_flat = 175
        
    def _calc_hit(self, base_atk_for_hit: float, enemy, is_arts: bool = False) -> float:
        """
        计算单次命中时的期望伤害。
        此方法封装了伺夜的职业特性（攻击力提升150%）和天赋2（无视175防御力）。
        假设敌人被狼群阻挡，因此所有相关加成均生效。
        
        Args:
            base_atk_for_hit (float): 用于计算本次伤害的基础攻击力（未包含职业特性加成）。
            enemy: 敌人对象。
            is_arts (bool): 是否为法术伤害。
        
        Returns:
            float: 单次命中造成的期望伤害。
        """
        # 职业特性：自身攻击援军阻挡的敌人时攻击力提升至150%
        # 此处将战术家的150%攻击力提升特性与伺夜的天赋结合计算。
        actual_atk_for_formula = base_atk_for_hit * self.atk_multiplier_on_blocked
        
        if is_arts:
            return calculate_arts_damage(actual_atk_for_formula, enemy.current_res)
        else:
            # 天赋2：无视175防御力
            return calculate_physical_damage(actual_atk_for_formula, enemy.current_def, def_ignore_flat=self.def_ignore_flat)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻为物理伤害。
        # 此处直接调用 _calc_hit 方法，该方法已包含了战术家的150%攻击力提升特性和伺夜的天赋2无视防御。
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (领袖的呼唤)："立即获得7点部署费用，并增加一只“狼影”"
            # 纯辅助技能，不直接造成伺夜自身的伤害或提供伺夜自身的伤害增益。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (领袖的馈赠)："立即获得2点部署费用，并使狼群下次攻击的攻击力提升至200%且狼群恢复20%生命值；若狼群击倒敌人则额外获得1点部署费用"
            # 纯辅助技能，不直接造成伺夜自身的伤害或提供伺夜自身的伤害增益。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (领袖的尊严)：
            # 持续时间15秒
            # "技能持续时间内逐渐获得12点部署费用，攻击变为三连击；狼群与伺夜攻击被狼群阻挡的单位造成伤害时，额外造成相当于伺夜攻击力50%的法术伤害"
            
            duration = 15.0
            
            # 1. 计算单次攻击的物理伤害部分 (三连击)
            # _calc_hit 方法已包含职业特性150%攻击力提升和天赋2的175防御力无视。
            physical_hit_damage = self._calc_hit(self.final_base_atk, enemy)
            
            # 2. 计算单次攻击的法术伤害部分 (额外造成50%攻击力的法术伤害)
            # 法术伤害的攻击力基数是伺夜的攻击力，同样会受到职业特性150%的加成。
            arts_hit_damage = self._calc_hit(self.final_base_atk * 0.5, enemy, is_arts=True)
            
            # 单次完整攻击造成的总伤害 (三连击物理 + 额外法术)
            enhanced_single_attack_damage = (physical_hit_damage * 3) + arts_hit_damage
            
            # 技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval
            
            total_damage = num_attacks * enhanced_single_attack_damage
            dps = enhanced_single_attack_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
