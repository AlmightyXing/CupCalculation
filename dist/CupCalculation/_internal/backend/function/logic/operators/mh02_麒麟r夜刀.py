from backend.function.logic.professions import Executor
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Mh02麒麟r夜刀(Executor):
    """
    干员：麒麟R夜刀
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：双雷剑麒麟 (攻击额外造成攻击力20%的法术伤害)
        self.talent1_arts_ratio = 0.20
        
        # 天赋 2：鬼人强化状态 (技能期间及技能结束后的10秒内攻击力+13%)
        # 这个加成是条件性的，在技能计算时应用，不直接加到面板
        self.talent2_atk_buff = 0.13

    def _calc_combined_damage(self, atk_val: float, arts_ratio: float, enemy) -> float:
        """
        计算单次命中时的期望伤害，包含物理和法术部分。
        """
        physical_dmg = calculate_physical_damage(atk_val, enemy.current_def)
        arts_dmg = calculate_arts_damage(atk_val * arts_ratio, enemy.current_res)
        return physical_dmg + arts_dmg

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻包含天赋1的额外法术伤害
        return self._calc_combined_damage(self.final_base_atk, self.talent1_arts_ratio, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 基础攻击间隔，用于计算DPS
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 技能期间的攻击力加成 (天赋2)
        skill_atk_buff_multiplier = 1 + self.talent2_atk_buff
        
        if skill_index == 0:
            # 技能 1 (鬼人化)：
            # 持续20秒，攻击速度+100，攻击变为二连击，且技能期间对同一目标的第三次攻击变为六连击
            skill_duration = 20
            skill_atk_speed_increase = 100
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_buff_multiplier
            
            # 计算强化后的攻击速度和实际攻击间隔
            enhanced_attack_speed = self.attack_speed + skill_atk_speed_increase
            skill_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 计算平均每次攻击的打击次数：(2次 + 2次 + 6次) / 3次攻击 = 10/3 次
            avg_hits_per_attack = (2 + 2 + 6) / 3
            
            # 计算单次打击的伤害（包含天赋1的额外法术伤害）
            damage_per_single_hit_instance = self._calc_combined_damage(enhanced_atk, self.talent1_arts_ratio, enemy)
            
            # 技能期间的总攻击次数
            num_attacks_in_duration = skill_duration / skill_actual_atk_interval
            
            # 总伤害 = 技能期间总攻击次数 * 平均每次攻击的打击次数 * 单次打击伤害
            total_damage = num_attacks_in_duration * avg_hits_per_attack * damage_per_single_hit_instance
            
            # DPS = 平均每次攻击的打击次数 * 单次打击伤害 / 技能实际攻击间隔
            dps = avg_hits_per_attack * damage_per_single_hit_instance / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (乱舞)：
            # 永续技能 (duration: null)
            # 第一天赋效果提升至2.5倍，攻击力提升至150%并对前方一格的所有敌人发动16次斩击
            
            # 天赋1法术伤害比例提升
            talent1_arts_ratio_enhanced = self.talent1_arts_ratio * 2.5
            
            # 技能攻击力乘数
            skill_atk_multiplier = 1.50
            
            # 计算强化后的攻击力 (天赋2加成后，再乘以技能乘数)
            enhanced_atk = self.final_base_atk * skill_atk_buff_multiplier * skill_atk_multiplier
            
            # 计算单次打击的伤害（包含强化后的天赋1额外法术伤害）
            damage_per_single_hit_instance = self._calc_combined_damage(enhanced_atk, talent1_arts_ratio_enhanced, enemy)
            
            # 每次攻击发动16次斩击
            hits_per_attack = 16
            
            # 永续技能，total_damage为0，重点计算DPS
            total_damage = 0
            
            # DPS = 每次攻击的打击次数 * 单次打击伤害 / 基础攻击间隔 (此技能无攻速加成)
            dps = hits_per_attack * damage_per_single_hit_instance / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (空中回旋乱舞)：
            # 瞬发技能 (duration: null)
            # 向前突进2格，每突进一段距离都会对周围所有敌人发动攻击力300%的斩击；
            # 期间每攻击到一个敌人都会使突进距离延长（最多延长至5格）
            
            # 技能攻击力乘数
            skill_atk_multiplier = 3.00
            
            # 假设最大突进距离，即造成5次斩击
            max_dash_hits = 5
            
            # 计算强化后的攻击力 (天赋2加成后，再乘以技能乘数)
            enhanced_atk = self.final_base_atk * skill_atk_buff_multiplier * skill_atk_multiplier
            
            # 计算单次斩击的伤害（包含天赋1的额外法术伤害）
            damage_per_single_hit_instance = self._calc_combined_damage(enhanced_atk, self.talent1_arts_ratio, enemy)
            
            # 总伤害 = 最大斩击次数 * 单次斩击伤害
            total_damage = max_dash_hits * damage_per_single_hit_instance
            
            # 瞬发技能的DPS = 总伤害 / 基础攻击间隔
            dps = total_damage / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)