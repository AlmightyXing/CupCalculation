from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_physical_damage

class Lm20阿(UnknownProfession):
    """
    干员：阿
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：混合药物射击 (每次攻击时有25%概率攻击力提升至150%)
        # 其他效果（回复生命、停顿、晕眩）不影响对敌伤害，故不纳入计算。
        self.prob_atk_boost = 0.25
        self.atk_boost_ratio = 1.5
        
        # 天赋 2：药剂扩散 (自身受到的治疗量+20%)
        # 该天赋不影响对敌伤害，故不纳入计算。
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑混合药物射击天赋的攻击力提升概率）
        """
        # 25% 概率攻击力提升至150%
        dmg_boosted = calculate_physical_damage(atk_val * self.atk_boost_ratio, enemy.current_def)
        # 75% 概率为正常攻击力
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def)
        
        return self.prob_atk_boost * dmg_boosted + (1 - self.prob_atk_boost) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (快速射击)：攻击速度+100，持续30秒
            duration = 30
            
            # 计算技能期间的实际攻击速度和攻击间隔
            enhanced_attack_speed = self.attack_speed + 100
            enhanced_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 计算技能期间的普攻次数
            hits_during_skill = duration / enhanced_actual_atk_interval
            
            # 计算强化后的单次普攻伤害
            enhanced_hit_damage = self._calc_hit(self.final_base_atk, enemy)
            
            total_damage = hits_during_skill * enhanced_hit_damage
            dps = enhanced_hit_damage / enhanced_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (爆发剂·γ型)：
            # 立即对友方单位攻击15次 (此为对友方单位的伤害，不计入对敌总伤)
            # 之后持续时间内使自身和目标防御力和生命上限+80% (此为防御性增益，不影响对敌伤害)
            # 因此，该技能对敌方单位造成的伤害为0。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (爆发剂·榴莲味)：
            # 立即对友方单位攻击15次 (此为对友方单位的伤害，不计入对敌总伤)
            # 之后持续时间内使自身和目标攻击力+50%，攻击速度+50，持续20秒
            duration = 20
            
            # 计算技能期间的攻击力
            enhanced_atk_val = self.final_base_atk * (1 + 0.50)
            
            # 计算技能期间的实际攻击速度和攻击间隔
            enhanced_attack_speed = self.attack_speed + 50
            enhanced_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 计算技能期间的普攻次数
            hits_during_skill = duration / enhanced_actual_atk_interval
            
            # 计算强化后的单次普攻伤害
            enhanced_hit_damage = self._calc_hit(enhanced_atk_val, enemy)
            
            total_damage = hits_during_skill * enhanced_hit_damage
            dps = enhanced_hit_damage / enhanced_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)