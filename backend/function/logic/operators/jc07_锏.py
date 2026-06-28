from backend.function.logic.professions import Swordmaster
from backend.function.logic.formulas import calculate_physical_damage

class Jc07锏(Swordmaster):
    """
    干员：锏
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：天生的武者 (造成伤害时有10%的几率攻击力提升至160%，并使目标战栗5秒)
        self.talent1_prob = 0.10
        self.talent1_atk_multiplier = 1.60
        
        # 天赋 2：活着的传奇 (攻击被战栗的目标时，无视目标25%的防御力)
        self.talent2_def_ignore_ratio = 0.25
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害，考虑天赋1和天赋2的概率触发。
        天赋1: 10%几率攻击力提升至160%，并使目标战栗。
        天赋2: 攻击被战栗的目标时，无视25%防御力。
        这意味着10%的几率同时触发天赋1的攻击力提升和天赋2的无视防御。
        """
        # 场景1: 天赋1触发 (10% 概率)
        # 攻击力提升至160%，目标“战栗”，因此天赋2的25%无视防御生效
        atk_val_talent_proc = atk_val * self.talent1_atk_multiplier
        dmg_talent_proc = calculate_physical_damage(atk_val_talent_proc, enemy.current_def, def_ignore_ratio=self.talent2_def_ignore_ratio)

        # 场景2: 天赋1未触发 (90% 概率)
        # 攻击力正常，目标未“战栗”，因此天赋2的无视防御不生效
        atk_val_normal = atk_val
        dmg_normal = calculate_physical_damage(atk_val_normal, enemy.current_def, def_ignore_ratio=0.0)

        return self.talent1_prob * dmg_talent_proc + (1 - self.talent1_prob) * dmg_normal

    def _calc_hit_skill_enhanced(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害，天赋1和天赋2以100%概率触发。
        天赋1: 攻击力提升至160%。
        天赋2: 无视25%防御力。
        """
        # 攻击力提升至160%，目标“战栗”，因此天赋2的25%无视防御生效
        atk_val_enhanced = atk_val * self.talent1_atk_multiplier
        return calculate_physical_damage(atk_val_enhanced, enemy.current_def, def_ignore_ratio=self.talent2_def_ignore_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 锏的普通攻击连续造成两次伤害
        return self._calc_hit(self.final_base_atk, enemy) * 2

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (纯粹的武力)：下次攻击对周围最多6名地面敌人造成两次相当于攻击力220%的物理伤害
            # 这是一个“下次攻击”技能，替换一次普攻，天赋按概率触发
            atk_val = self.final_base_atk * 2.20
            total_damage = self._calc_hit(atk_val, enemy) * 2
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (无声的嘲笑)：对前方范围内最多6名地面敌人发动2次斩击，攻击被阻挡的敌人时改为3次斩击，
            # 天赋的发动概率提升至100%，每次斩击造成相当于攻击力310%的物理伤害
            # 按照“对提高伤害有帮助，均纳入考虑”的原则，取3次斩击
            # 天赋100%触发，所以使用 _calc_hit_skill_enhanced
            atk_val_base = self.final_base_atk * 3.10
            num_hits = 3 # 攻击被阻挡的敌人时为3次斩击，取最大值
            
            total_damage = self._calc_hit_skill_enhanced(atk_val_base, enemy) * num_hits
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (归于宁静)：持续发动总计10次斩击，每次斩击对最多6名敌人造成相当于攻击力235%的物理伤害，
            # 天赋的发动概率提升至100%，并持续将敌人中等力度地拖拽至自身中心，
            # 之后将造成一次相当于攻击力330%的物理伤害并将敌人较大力地拖拽至自身中心
            # 技能持续时间30秒
            duration = 30
            
            # 10次初始斩击
            atk_val_initial_base = self.final_base_atk * 2.35
            dmg_per_hit_initial = self._calc_hit_skill_enhanced(atk_val_initial_base, enemy)
            total_damage_initial = dmg_per_hit_initial * 10
            
            # 最终爆发伤害
            atk_val_final_base = self.final_base_atk * 3.30
            dmg_final_burst = self._calc_hit_skill_enhanced(atk_val_final_base, enemy)
            
            total_damage = total_damage_initial + dmg_final_burst
            return {"total_damage": total_damage, "dps": total_damage / duration}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)