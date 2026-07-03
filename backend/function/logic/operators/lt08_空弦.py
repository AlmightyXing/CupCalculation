from backend.function.logic.professions import Marksman
from backend.function.logic.formulas import calculate_physical_damage

class Lt08空弦(Marksman):
    """
    干员：空弦
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：兰登战术 (技力回复，不影响自身伤害，忽略)
        # 天赋 2：铁弦 (护盾/技力回复，不影响自身伤害，忽略)
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 空弦的普攻没有特殊机制，直接调用基类方法
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (箭矢·散逸)：下次攻击造成相当于攻击力230%的物理伤害
            # 额外选择目标周围最多3名其他敌人造成攻击力180%的物理伤害 (根据规则，不计入单目标总伤)
            atk_val = self.final_base_atk * 2.30
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (箭矢·追猎)：立即发射箭矢对目标进行攻击力140%的5次攻击
            # 可弹射至目标周围的下一个未选择过的敌人（每次弹射减少1次攻击次数）
            # 根据规则，弹射伤害不计入单目标总伤，假设5次攻击均命中主目标
            atk_val_per_hit = self.final_base_atk * 1.40
            num_hits = 5
            damage_per_hit = calculate_physical_damage(atk_val_per_hit, enemy.current_def)
            total_damage = damage_per_hit * num_hits
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (箭矢·暴风)：持续20秒，攻击力+30%，攻击变为3连击，每次可以攻击2个敌人
            # 根据规则，攻击2个敌人不计入单目标总伤
            duration = 20
            atk_multiplier = 1.30
            hits_per_attack_animation = 3 # 3连击
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算单次命中伤害
            damage_per_single_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算每次攻击动画的总伤害 (3连击)
            damage_per_attack_animation = damage_per_single_hit * hits_per_attack_animation
            
            # 计算技能持续期间的攻击次数
            attacks_during_duration = (duration or 0) / actual_atk_interval
            
            # 计算总伤害
            total_damage = damage_per_attack_animation * attacks_during_duration
            
            # 计算DPS
            dps = damage_per_attack_animation / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)