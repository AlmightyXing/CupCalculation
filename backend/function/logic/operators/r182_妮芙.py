from backend.function.logic.professions import PrimalCaster
from backend.function.logic.formulas import calculate_arts_damage

class R182妮芙(PrimalCaster):
    """
    干员：妮芙
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性，确保在 apply_talents 中可以修改
        self.talent1_elemental_dps_ratio = 0.4 # 天赋1“失魂”的基础元素伤害比例
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：失魂
        # "攻击处于凋亡损伤爆发期间的敌人时使其每秒受到相当于攻击力40%的元素伤害，持续至凋亡损伤爆发结束"
        # 这个天赋提供的是持续的元素伤害，其比例已在 __init__ 中初始化为 0.4。
        # 在技能计算中，如果敌人处于爆发期间，会将其作为额外的DPS加入。

        # 天赋 2：窥心钥
        # "每当自身攻击范围内敌人凋亡损伤爆发，攻击力+2%，最多可叠加10层"
        # 根据规则，可叠加层数的天赋按最大层数计算。
        max_layers = 10
        atk_per_layer = 0.02
        self.final_base_atk *= (1 + max_layers * atk_per_layer)
        
    def _calc_elemental_dps_from_talent1(self, atk_val: float, current_talent_ratio: float) -> float:
        """
        计算天赋1“失魂”带来的每秒元素伤害。
        假设敌人处于凋亡损伤爆发期间。
        元素伤害无视防御和法术抗性。
        """
        return atk_val * current_talent_ratio

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 妮芙是本源术师，普攻造成法术伤害。
        # PrimalCaster 父类没有覆写 calculate_normal_hit，因此这里直接实现法术伤害计算。
        # self.final_base_atk 已经包含了信赖和天赋2的攻击力加成。
        # 天赋1是每秒元素伤害，不计入单次普攻命中伤害。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 默认的天赋1元素伤害比例
        current_talent1_elemental_dps_ratio = self.talent1_elemental_dps_ratio

        if skill_index == 0:
            # 技能 1 (笞心击)：
            # "攻击力+110%，攻击附带造成法术伤害15%的凋亡损伤，若目标处于凋亡损伤爆发期间则对其额外造成相当于攻击力50%的元素伤害"
            # 持续时间: 20秒
            
            skill_atk_buff_ratio = 1.10
            skill_atk_val = self.final_base_atk * (1 + skill_atk_buff_ratio)
            
            # 单次普攻的法术伤害
            arts_dmg_per_hit = calculate_arts_damage(skill_atk_val, enemy.current_res)
            
            # 额外元素伤害 (假设目标处于凋亡损伤爆发期间，以计算最大伤害)
            elemental_dmg_per_hit = skill_atk_val * 0.50
            
            # 单次普攻总伤害 (法术 + 元素)
            total_dmg_per_hit = arts_dmg_per_hit + elemental_dmg_per_hit
            
            # 技能期间普攻造成的DPS
            dps_from_hits = total_dmg_per_hit / actual_atk_interval
            
            # 来自天赋1的额外元素DPS (基于强化后的攻击力，假设目标处于爆发期间)
            dps_from_talent1 = self._calc_elemental_dps_from_talent1(skill_atk_val, current_talent1_elemental_dps_ratio)
            
            # 技能期间总DPS
            total_dps = dps_from_hits + dps_from_talent1
            
            # 技能总伤害 = 总DPS * 持续时间
            total_damage = total_dps * self.skills[skill_index]["duration"]
            
            return {"total_damage": total_damage, "dps": total_dps}
            
        elif skill_index == 1:
            # 技能 2 (怵然震爆)：
            # "对敌人造成一次相当于攻击力400%的法术伤害、使其恐惧5秒，并对目标周围造成一次等额法术溅射伤害，均附带造成法术伤害25%的凋亡损伤；
            # 若攻击到的单位处于凋亡损伤爆发期间，使第一天赋造成的伤害效果提高至攻击力的100% 可充能2次"
            # 持续时间: null (瞬发技能)
            
            skill_atk_multiplier = 4.0
            skill_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 瞬发法术伤害 (只计算对主目标的伤害，不计算溅射目标数)
            total_damage = calculate_arts_damage(skill_atk_val, enemy.current_res)
            
            # 瞬发技能的DPS计算方式
            # 对于瞬发技能，DPS通常表示为总伤害除以一个标准攻击间隔，或者不计算DPS只返回总伤害。
            # 这里沿用原代码的计算方式。
            dps = total_damage / actual_atk_interval
            
            # 天赋1的伤害效果提高是后续影响，不计入瞬发技能本身的 total_damage 和 dps。
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (心防溃决)：
            # "攻击范围扩大，攻击力+220%，攻击速度+60，同时攻击2个目标，若目标处于凋亡损伤爆发期间，攻击造成元素伤害"
            # 持续时间: 35秒
            
            skill_atk_buff_ratio = 2.20
            skill_atk_speed_buff = 60
            
            skill_atk_val = self.final_base_atk * (1 + skill_atk_buff_ratio)
            skill_attack_speed = self.attack_speed + skill_atk_speed_buff
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 伤害类型：若目标处于凋亡损伤爆发期间，攻击造成元素伤害。
            # 假设目标处于爆发期间以计算最大伤害。元素伤害无视防御和法术抗性。
            dmg_per_hit = skill_atk_val
            
            # 技能期间普攻造成的DPS (不乘以目标数，因为目标数是特性，这里只算单次命中伤害)
            dps_from_hits = dmg_per_hit / skill_actual_atk_interval
            
            # 来自天赋1的额外元素DPS (基于强化后的攻击力，假设目标处于爆发期间)
            dps_from_talent1 = self._calc_elemental_dps_from_talent1(skill_atk_val, current_talent1_elemental_dps_ratio)
            
            # 技能期间总DPS
            total_dps = dps_from_hits + dps_from_talent1
            
            # 技能总伤害 = 总DPS * 持续时间
            total_damage = total_dps * self.skills[skill_index]["duration"]
            
            return {"total_damage": total_damage, "dps": total_dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
