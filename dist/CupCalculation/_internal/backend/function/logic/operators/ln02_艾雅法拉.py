from backend.function.logic.professions import CoreCaster
from backend.function.logic.formulas import calculate_arts_damage

class Ln02艾雅法拉(CoreCaster):
    """
    干员：艾雅法拉
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 应用天赋，天赋可能修改 final_base_atk
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：炎息 (在场时，所有友方【术师】职业干员的攻击力+14%)
        # 艾雅法拉自身作为术师，也享受此加成
        self.final_base_atk *= (1 + 0.14)
        
        # 天赋 2：乱火 (部署后立即随机获得7~15点技力)
        # 此天赋不影响伤害计算，故无需在apply_talents中体现
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 艾雅法拉是中坚术师，攻击造成法术伤害
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员的基础实际攻击间隔，用于瞬发技能的DPS计算
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (二重咏唱)：攻击速度+60，第二次及以后使用时追加攻击力+60%的效果
            # 持续时间：25秒
            # 计算时假设为第二次及以后使用，取最大收益
            duration = 25
            
            # 技能状态加成
            skill_atk_buff_ratio = 0.60 # 攻击力+60%
            skill_attack_speed_buff = 60 # 攻击速度+60
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + skill_atk_buff_ratio)
            # 计算强化后的攻击速度
            temp_attack_speed = self.attack_speed + skill_attack_speed_buff
            
            # 计算技能期间的实际攻击间隔
            temp_actual_atk_interval = self.attack_interval * 100 / temp_attack_speed
            
            # 计算技能期间的普攻次数
            hits = duration / temp_actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_dmg = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 计算总伤害和DPS
            total_damage = hits * single_hit_dmg
            dps = single_hit_dmg / temp_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (点燃)：下次攻击造成相当于攻击力370%的法术伤害
            # 瞬发伤害技能
            
            skill_atk_multiplier = 3.70 # 造成370%攻击力的伤害
            
            # 计算瞬发伤害的攻击力
            burst_atk_value = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次瞬发伤害
            total_damage = calculate_arts_damage(burst_atk_value, enemy.current_res)
            
            # 瞬发技能的DPS通常按单次伤害除以基础攻击间隔
            dps = total_damage / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (火山)：攻击力+130%，攻击间隔大幅度缩短(-1.1)
            # 持续时间：15秒
            duration = 15
            
            # 技能状态加成
            skill_atk_buff_ratio = 1.30 # 攻击力+130%
            skill_attack_interval_reduction = 1.1 # 攻击间隔缩短1.1秒
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + skill_atk_buff_ratio)
            # 计算强化后的攻击间隔
            # 注意：火山技能只缩短攻击间隔，不改变攻击速度
            temp_attack_interval = self.attack_interval - skill_attack_interval_reduction
            
            # 计算技能期间的实际攻击间隔
            temp_actual_atk_interval = temp_attack_interval * 100 / self.attack_speed
            
            # 计算技能期间的普攻次数
            hits = duration / temp_actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_dmg = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 计算总伤害和DPS
            total_damage = hits * single_hit_dmg
            dps = single_hit_dmg / temp_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)