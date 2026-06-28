from backend.function.logic.professions import IntelligenceOfficer # 假设情报官职业类名为 IntelligenceOfficer
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class B215伊内丝(IntelligenceOfficer):
    """
    干员：伊内丝
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents() # 在 final_base_atk 确定后调用天赋逻辑
        
    def apply_talents(self):
        # 天赋 1：影织 (对每个敌人首次造成伤害后，使目标束缚5秒并偷取其90点攻击力)
        # 根据规则，天赋对提高伤害有帮助的均纳入考虑，可叠加层数的按最大层数叠加。
        # 偷取攻击力视为对自身攻击力的永久提升，按最大值90点计算，直接加到最终基础攻击力上。
        self.final_base_atk += 90
        
        # 天赋 2：影哨 (攻击范围内敌人的隐匿效果失效且移动速度-30%，撤退后留下一个影哨使该效果持续生效)
        # 此天赋不直接影响伊内丝的伤害输出数值，因此无需在apply_talents中修改属性。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 伊内丝作为情报官，普攻造成物理伤害
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (淬影突袭)：下次攻击使目标3秒内每秒受到相当于伊内丝攻击力80%的法术伤害（不叠加）
            # 这是一个“下次攻击”技能，包含一次物理普攻和额外的法术持续伤害。
            
            # 物理普攻部分
            physical_hit_damage = self.calculate_normal_hit(enemy)
            
            # 法术持续伤害部分 (3秒内每秒80%攻击力)
            # 总法术伤害为 (伊内丝攻击力 * 0.8) * 3秒
            total_arts_dot_value = self.final_base_atk * 0.8 * 3 
            
            # 法术伤害需要通过 calculate_arts_damage 计算，考虑敌方抗性
            arts_damage_from_dot = calculate_arts_damage(total_arts_dot_value, enemy.current_res)
            
            total_damage = physical_hit_damage + arts_damage_from_dot
            
            # 瞬发伤害技能的DPS计算规则：total_damage / actual_atk_interval
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (暗夜无明)：持续12秒，攻击力+110%
            duration = 12
            atk_multiplier = 1 + 1.10 # 攻击力+110%
            
            # 强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 强化后的单次普攻伤害
            enhanced_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能期间能打出的普攻次数
            num_attacks = duration / actual_atk_interval
            
            total_damage = num_attacks * enhanced_hit_damage
            dps = enhanced_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (独影归途)：部署后攻击力+160%，立刻收回影哨对穿过的最多6名敌人造成相当于攻击力200%的物理伤害
            # 这是一个瞬发爆发伤害技能。
            
            # 增益先触发，爆发伤害使用强化后的攻击力
            atk_multiplier = 1 + 1.60 # 攻击力+160%
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 爆发伤害倍率
            burst_damage_ratio = 2.00 # 200%攻击力
            
            # 爆发伤害的攻击力数值
            burst_atk_value = enhanced_atk * burst_damage_ratio
            
            # 计算单次爆发的物理伤害
            total_damage = calculate_physical_damage(burst_atk_value, enemy.current_def)
            
            # 瞬发伤害技能的DPS计算规则：total_damage / actual_atk_interval
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)