from backend.function.logic.professions import Pioneer
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Sr40忍冬(Pioneer):
    """
    干员：忍冬
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：追凶 (对每个敌人造成首次伤害后，10秒内忍冬对该敌人造成伤害时额外造成攻击力30%的法术伤害)
        # 假设条件满足，每次伤害都附带额外法术伤害
        self.additional_talent_arts_ratio = 0.3
        
        # 天赋 2：蓄势 (在场时，部署费用的自然回复速度+10%，若4秒内自身未受到伤害，则每秒恢复4%的最大生命值)
        # 该天赋不直接影响伤害计算，无需在apply_talents中修改属性
        
    def _calc_combined_hit(self, atk_val: float, enemy, skill_additional_arts_ratio: float = 0.0) -> float:
        """
        计算单次命中时的期望伤害，包含物理伤害和天赋附带的法术伤害。
        skill_additional_arts_ratio 用于技能额外法术伤害，与天赋的additional_talent_arts_ratio叠加。
        """
        # 物理伤害部分
        physical_dmg = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 天赋附带的法术伤害部分
        talent_arts_dmg = calculate_arts_damage(atk_val * self.additional_talent_arts_ratio, enemy.current_res)
        
        # 技能额外附带的法术伤害部分 (如果存在)
        skill_arts_dmg = 0.0
        if skill_additional_arts_ratio > 0:
            skill_arts_dmg = calculate_arts_damage(atk_val * skill_additional_arts_ratio, enemy.current_res)
            
        return physical_dmg + talent_arts_dmg + skill_arts_dmg

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻包含物理伤害和天赋1附带的法术伤害
        return self._calc_combined_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 基础攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (小施惩戒)：下次攻击额外造成攻击力290%的法术伤害
            # 这是一个强化普攻技能，只计算单次强化攻击的伤害
            
            # _calc_combined_hit 已经处理了天赋法术伤害，这里只需要传入技能额外法术伤害的倍率
            total_damage = self._calc_combined_hit(self.final_base_atk, enemy, skill_additional_arts_ratio=2.9)
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (坠刃拷问)：立即获得7点部署费用，对周围最多6名敌人造成相当于攻击力300%的法术伤害
            # 这是一个瞬发爆发技能，只造成法术伤害
            
            skill_atk_val = self.final_base_atk * 3.0
            total_damage = calculate_arts_damage(skill_atk_val, enemy.current_res)
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (隐狐之艺)：持续10秒，攻击力+110%，攻击速度从+180逐渐衰减至+0
            duration = 10
            
            # 攻击力增益
            atk_multiplier = 1 + 1.10 # +110%攻击力
            skill_atk_val = self.final_base_atk * atk_multiplier
            
            # 攻击速度增益：从+180衰减至+0，取平均值 (180+0)/2 = 90
            avg_attack_speed_bonus = 90
            skill_attack_speed = self.attack_speed + avg_attack_speed_bonus
            
            # 技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 技能期间的单次普攻伤害 (强化后的攻击力，并包含天赋法术伤害)
            single_hit_damage = self._calc_combined_hit(skill_atk_val, enemy)
            
            # 技能期间能打出的普攻次数
            hits_during_skill = duration / skill_actual_atk_interval
            
            total_damage = hits_during_skill * single_hit_damage
            
            return {"total_damage": total_damage, "dps": single_hit_damage / skill_actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
