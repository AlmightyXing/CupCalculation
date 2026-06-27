from backend.function.logic.professions import Swordmaster
from backend.function.logic.formulas import calculate_physical_damage

class Ii07艾丽妮(Swordmaster):
    """
    干员：艾丽妮
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：审判之火 (物理伤害有50%概率无视50%防御力)
        self.prob_ignore_def = 0.5
        self.ignore_def_ratio = 0.5
        
        # 天赋 2：净化之剑 (攻击速度+18)
        # TODO: 场上有海怪时效果翻倍，当前未实装敌人种族，按基础+18计算
        self.attack_speed += 18
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑审判之火天赋的无视防御概率）
        """
        dmg_ignore = calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.ignore_def_ratio)
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=0.0)
        return self.prob_ignore_def * dmg_ignore + (1 - self.prob_ignore_def) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        覆写基类普攻期望。
        根据规则，忽略父类特性的连击描述，视为攻击一次。
        引入了艾丽妮特殊的天赋破甲计算。
        """
        return self._calc_hit(self.final_base_atk, enemy) * target_count

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> float:
        """
        覆写基类技能总伤计算，仅需关注技能本身的倍率。
        """
        if skill_index == 0:
            # 技能 1 (起风)：2次200%攻击力的物理伤害
            atk_val = self.final_base_atk * 2.0
            return self._calc_hit(atk_val, enemy) * 2 * target_count
            
        elif skill_index == 1:
            # 技能 2 (裂潮)：1次400%攻击力的物理伤害
            atk_val = self.final_base_atk * 4.0
            return self._calc_hit(atk_val, enemy) * target_count
            
        elif skill_index == 2:
            # 技能 3 (判决)：1次300%攻击力 + 12次250%攻击力
            hit1_atk = self.final_base_atk * 3.0
            hit2_atk = self.final_base_atk * 2.5
            
            dmg1 = self._calc_hit(hit1_atk, enemy)
            dmg2 = self._calc_hit(hit2_atk, enemy) * 12
            
            return (dmg1 + dmg2) * target_count
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
