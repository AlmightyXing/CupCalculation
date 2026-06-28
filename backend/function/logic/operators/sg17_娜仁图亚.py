from backend.function.logic.professions import Loopshooter
from backend.function.logic.formulas import calculate_physical_damage

class Sg17娜仁图亚(Loopshooter):
    """
    干员：娜仁图亚
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：“我见，我得”
        # 在场时，每次攻击到敌人偷取其25点攻击力（最高250点）与20点防御力（最高200点）
        # 此天赋对提高伤害有帮助的部分是“偷取敌人防御力”，最高200点防御力降低会提高我方伤害。
        # 攻击力偷取是降低敌方攻击力，不影响自身伤害计算。
        self.talent1_max_enemy_def_reduction = 200
        
        # 天赋 2：婀娜虚影
        # 获得35%的物理与法术闪避，周围8格内敌人的物理与法术命中率-20%
        # 这些是防御/生存向天赋，不直接提高自身伤害，因此不在此处修改面板。
        
    def _get_modified_enemy_def(self, enemy) -> float:
        """
        根据天赋计算敌人实际防御力（考虑天赋1的防御力偷取效果）
        """
        # 天赋1：偷取敌人防御力，按最大层数计算
        modified_def = enemy.current_def - self.talent1_max_enemy_def_reduction
        return max(0, modified_def) # 敌人防御力不能低于0

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望伤害。
        娜仁图亚的父类Loopshooter的calculate_normal_hit方法不增加额外伤害系数，
        因此直接计算物理伤害并应用天赋效果即可。
        """
        modified_enemy_def = self._get_modified_enemy_def(enemy)
        return calculate_physical_damage(self.final_base_atk, modified_enemy_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        modified_enemy_def = self._get_modified_enemy_def(enemy)
        
        if skill_index == 0:
            # 技能 1 (旋刃)：
            # 攻击距离-1，回旋投射物造成相当于攻击力190%的物理伤害，并且可以在敌人间重复弹射（最多弹跳3次）
            # 技能类型为永续技能 (duration: null)，total_damage = 0，重点是返回正确的dps。
            # 根据规则，最终伤害必须严格是对单个目标造成的伤害。
            # 因此，弹跳效果不计入单个目标的伤害，只计算对当前目标造成的190%攻击力伤害。
            skill_atk_multiplier = 1.90
            atk_val = self.final_base_atk * skill_atk_multiplier
            damage_per_hit = calculate_physical_damage(atk_val, modified_enemy_def)
            
            return {"total_damage": 0, "dps": damage_per_hit / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (恶魇)：
            # 每次攻击造成相当于攻击力250%的物理伤害并使目标停顿1秒，
            # 投射物命中目标后会在短暂突进后折返，返回时对穿过的所有敌人造成一次相当于攻击力200%的物理伤害
            # 持续时间：30秒
            # 对单个目标而言，每次攻击造成 (250% + 200%) = 450% 攻击力的物理伤害。
            skill_atk_multiplier = 2.50 + 2.00 # 250% (初次命中) + 200% (折返命中单个目标)
            atk_val = self.final_base_atk * skill_atk_multiplier
            damage_per_hit = calculate_physical_damage(atk_val, modified_enemy_def)
            
            duration = 30
            num_hits = duration / actual_atk_interval
            total_damage = damage_per_hit * num_hits
            
            return {"total_damage": total_damage, "dps": damage_per_hit / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (吞日)：
            # 每次攻击发射3个回旋投射物（每个造成相当于攻击力175%的物理伤害），
            # 投射物全部回收时娜仁图亚对周围8格内至多3名敌人造成一次相当于攻击力160%的物理伤害并使其停顿1秒
            # 持续时间：20秒
            # 对单个目标而言，每次攻击造成 (3 * 175%) + 160% = 525% + 160% = 685% 攻击力的物理伤害。
            # 3个投射物对单个目标造成3次伤害，回收时对单个目标造成1次伤害。
            skill_atk_multiplier = (3 * 1.75) + 1.60 # (3 * 175%) + 160%
            atk_val = self.final_base_atk * skill_atk_multiplier
            damage_per_hit = calculate_physical_damage(atk_val, modified_enemy_def)
            
            duration = 20
            num_hits = duration / actual_atk_interval
            total_damage = damage_per_hit * num_hits
            
            return {"total_damage": total_damage, "dps": damage_per_hit / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
