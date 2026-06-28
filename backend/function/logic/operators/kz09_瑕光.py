from backend.function.logic.professions import Defender # 假设“守护者”对应 Defender 职业
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Kz09瑕光(Defender):
    """
    干员：瑕光
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：剑盾骑士 (在场时所有受击回复的技能在干员攻击时也回复1点技力)
        # 此天赋影响SP回复，不直接影响伤害数值，故不在此处实现。

        # 天赋 2：仁慈 (自身可以攻击并优先攻击沉睡的目标且攻击力提升至140%)
        # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑！”，假设此攻击力提升常驻于伤害计算中。
        self.talent_atk_boost_sleep = 1.40 # 攻击力提升至140%
        
    def _get_current_atk_base(self, skill_atk_add_ratio: float = 0.0, apply_talent_sleep_boost: bool = True) -> float:
        """
        计算考虑了技能攻击力加成和天赋“仁慈”加成后的基础攻击力。
        这个值再乘以技能的伤害倍率。
        
        :param skill_atk_add_ratio: 技能提供的攻击力额外百分比，例如攻击力+110%则为1.10。
        :param apply_talent_sleep_boost: 是否应用天赋“仁慈”的攻击力提升。
        :return: 计算后的基础攻击力。
        """
        base_atk = self.final_base_atk
        
        # 技能攻击力加成 (例如攻击力+110% -> skill_atk_add_ratio = 1.10)
        modified_atk = base_atk * (1 + skill_atk_add_ratio)
        
        # 天赋“仁慈”的攻击力提升
        if apply_talent_sleep_boost:
            modified_atk *= self.talent_atk_boost_sleep
            
        return modified_atk

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻时，仁慈天赋的攻击力提升生效
        atk_val = self._get_current_atk_base(apply_talent_sleep_boost=True)
        return calculate_physical_damage(atk_val, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (光芒涌动)：下次攻击造成相当于攻击力260%的物理伤害
            # 瞬发伤害，且仁慈天赋的攻击力提升生效
            
            # 计算强化后的基础攻击力，然后乘以技能倍率
            base_atk_for_skill = self._get_current_atk_base(apply_talent_sleep_boost=True)
            atk_val = base_atk_for_skill * 2.60
            
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (慑敌辉光)：持续10秒，攻击力+110%，立即使自身这格内的所有地面敌人陷入沉睡
            # 增益类技能，攻击力加成 (1+1.10)，且敌人陷入沉睡，仁慈天赋的攻击力提升生效
            duration = 10
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self._get_current_atk_base(skill_atk_add_ratio=1.10, apply_talent_sleep_boost=True)
            
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            num_attacks = duration / actual_atk_interval
            total_damage = single_hit_damage * num_attacks
            
            return {"total_damage": total_damage, "dps": single_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (先贤化身)：持续30秒，攻击力+110%，防御力+60%，每次攻击额外造成相当于攻击力100%的法术伤害
            # 增益类技能，攻击力加成 (1+1.10)。
            # 假设仁慈天赋的攻击力提升生效 (根据规则“只要天赋对提高伤害有帮助，均纳入考虑！”)
            duration = 30
            
            # 计算技能期间的强化攻击力
            enhanced_atk_for_damage = self._get_current_atk_base(skill_atk_add_ratio=1.10, apply_talent_sleep_boost=True)
            
            # 物理伤害部分
            physical_dmg_per_hit = calculate_physical_damage(enhanced_atk_for_damage, enemy.current_def)
            
            # 额外法术伤害部分 (攻击力100%的法术伤害，使用强化后的攻击力)
            arts_dmg_per_hit = calculate_arts_damage(enhanced_atk_for_damage * 1.0, enemy.current_res)
            
            single_hit_total_damage = physical_dmg_per_hit + arts_dmg_per_hit
            
            num_attacks = duration / actual_atk_interval
            total_damage = single_hit_total_damage * num_attacks
            
            return {"total_damage": total_damage, "dps": single_hit_total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)