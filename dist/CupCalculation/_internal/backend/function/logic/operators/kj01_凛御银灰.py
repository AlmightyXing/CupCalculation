from backend.function.logic.professions import Strategist
from backend.function.logic.formulas import calculate_physical_damage

class Kj01凛御银灰(Strategist):
    """
    干员：凛御银灰
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：开放性开局
        # 该天赋主要影响部署费用、技力回复和再部署时间，不直接影响凛御银灰自身的攻击力、攻速或伤害计算。
        pass
        
        # 天赋 2：雪境先驱
        # 该天赋主要影响【谢拉格】干员的防御力和生命回复，以及凛御银灰自身的防御力和生命回复。
        # 不直接影响凛御银灰自身的攻击力、攻速或伤害计算。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 凛御银灰的普攻为物理伤害，且天赋不提供特殊的伤害修正（如无视防御、法术伤害转换等）。
        # 因此直接使用基础物理伤害计算。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (周旋的谋略)：
            # 该技能为纯粹的辅助技能，提供部署费用、降低其他干员费用并提供屏障，不造成任何伤害。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (御敌的锋锐)：
            # 对前方6名敌人造成攻击力380%的物理伤害。
            # 这是一个瞬发爆发伤害技能。
            
            # 计算强化后的攻击力
            atk_val = self.final_base_atk * 3.80
            
            # 计算单次命中伤害
            single_hit_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 总伤害即为单次命中伤害（不乘以目标数）
            total_damage = single_hit_damage
            
            # DPS为总伤害除以实际攻击间隔（瞬发技能的DPS计算方式）
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (变革已至)：
            # 持续48秒，攻击范围扩大，攻击对直线范围造成攻击力200%的物理伤害和30%的脆弱。
            # 这是一个持续增益型技能，改变普攻模式并附加脆弱效果。
            
            duration = 48.0
            
            # 技能期间的攻击力倍率
            atk_multiplier = 2.0
            # 脆弱效果，使敌人受到的伤害提高30%
            vulnerability_ratio = 0.3
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间单次普攻的期望伤害，考虑脆弱效果
            single_hit_damage = calculate_physical_damage(
                enhanced_atk, 
                enemy.current_def)
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = (duration or 0) / actual_atk_interval
            
            # 总伤害为普攻次数乘以单次普攻伤害
            total_damage = single_hit_damage * num_hits
            
            # DPS为单次普攻伤害除以实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)