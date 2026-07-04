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
        艾丽妮的普攻需要考虑其天赋的破甲计算，同时要保留剑豪职业的普攻两连击特性。
        """
        # 先计算单次攻击的伤害（包含艾丽妮的天赋效果）
        single_hit_damage = self._calc_hit(self.final_base_atk, enemy)
        # 剑豪特性：普通攻击连续造成两次伤害
        return single_hit_damage * 2.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (起风)：2次200%攻击力的物理伤害
            atk_val = self.final_base_atk * 2.0
            total_damage = self._calc_hit(atk_val, enemy) * 2
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (裂潮)：1次400%攻击力的物理伤害
            atk_val = self.final_base_atk * 4.0
            total_damage = self._calc_hit(atk_val, enemy)
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (判决)：1次300%攻击力 + 12次250%攻击力
            hit1_atk = self.final_base_atk * 3.0
            hit2_atk = self.final_base_atk * 2.5
            
            dmg1 = self._calc_hit(hit1_atk, enemy)
            dmg2 = self._calc_hit(hit2_atk, enemy) * 12
            
            total_damage = dmg1 + dmg2
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
