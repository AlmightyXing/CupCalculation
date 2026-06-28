from backend.function.logic.professions import Hunter # 莱伊的职业类型为“猎手”
from backend.function.logic.formulas import calculate_physical_damage

class Rb15莱伊(Hunter):
    """
    干员：莱伊
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 干员特性：攻击时需要消耗子弹且攻击力提升至120%
        # 这是一个常驻的攻击力乘区，应用于所有攻击
        self.character_trait_atk_multiplier = 1.2
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：巡哨伙伴 (自身优先攻击该区域内的目标且对其造成的物理伤害提高15%)
        # 这是最终伤害乘区
        self.talent_1_final_dmg_boost_ratio = 0.15
        
        # 天赋 2：入神 (攻击相同目标时每次攻击提高自身攻击力8%，最多3层)
        # 根据规则，直接按最大层数叠加到属性中
        self.talent_2_atk_boost_ratio = 0.08 * 3 # 24% 攻击力提升
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑天赋1的最终伤害加成）
        atk_val 应已包含基础攻击力、信赖、干员特性、天赋2及技能的攻击力加成。
        """
        raw_physical_damage = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 应用天赋 1：巡哨伙伴 (物理伤害提高15%)
        final_damage = raw_physical_damage * (1 + self.talent_1_final_dmg_boost_ratio)
        return final_damage

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 计算普攻时的有效攻击力：
        # 1. final_base_atk (基础攻击力 + 信赖攻击力)
        # 2. character_trait_atk_multiplier (干员特性：攻击力提升至120%)
        # 3. talent_2_atk_boost_ratio (天赋2：入神，最多3层24%攻击力提升)
        
        effective_atk = self.final_base_atk \
                       * self.character_trait_atk_multiplier \
                       * (1 + self.talent_2_atk_boost_ratio)
                       
        return self._calc_hit(effective_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算实际攻击间隔，用于DPS计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 计算技能生效前的基础攻击力，包含干员特性和天赋2的加成
        base_atk_for_skill_calc = self.final_base_atk \
                                 * self.character_trait_atk_multiplier \
                                 * (1 + self.talent_2_atk_boost_ratio)
        
        if skill_index == 0:
            # 技能 1 (脱身矢): 立即用额外特殊子弹攻击目标，造成相当于攻击力450%的物理伤害
            # 这是一个瞬发伤害技能。
            skill_atk_multiplier = 4.5
            
            # 爆发伤害使用当前已强化的攻击力
            atk_val = base_atk_for_skill_calc * skill_atk_multiplier
            total_damage = self._calc_hit(atk_val, enemy)
            
            # 瞬发伤害技能的DPS计算方式：总伤 / 普攻实际攻击间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (广域警觉): 自动开启：攻击范围扩大，攻击力+120%，持续时间无限
            # 这是一个永续技能，总伤为0，重点计算DPS。
            skill_atk_boost_ratio = 1.2 # +120%攻击力意味着攻击力变为 (1 + 1.2) 倍
            
            # 技能期间的有效攻击力
            effective_atk_during_skill = base_atk_for_skill_calc * (1 + skill_atk_boost_ratio)
            
            single_hit_damage = self._calc_hit(effective_atk_during_skill, enemy)
            
            # 永续技能的DPS计算方式：强化后的单次普攻伤害 / 普攻实际攻击间隔
            return {"total_damage": 0, "dps": single_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (“得见光芒”): 持续时间: 16秒
            # 攻击造成相当于攻击力330%的物理伤害
            # 装填间隔大幅缩短(-1.2)
            
            skill_duration = 16
            skill_atk_multiplier = 3.3
            skill_attack_interval_reduction = 1.2 # 减少基础攻击间隔
            
            # 计算技能期间修改后的基础攻击间隔
            modified_base_attack_interval = self.attack_interval - skill_attack_interval_reduction
            
            # 计算技能期间的实际攻击间隔 (考虑攻速加成)
            skill_actual_atk_interval = modified_base_attack_interval * 100 / self.attack_speed
            
            # 技能期间的有效攻击力
            effective_atk_during_skill = base_atk_for_skill_calc * skill_atk_multiplier
            
            single_hit_damage = self._calc_hit(effective_atk_during_skill, enemy)
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = skill_duration / skill_actual_atk_interval
            
            total_damage = single_hit_damage * num_hits
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)