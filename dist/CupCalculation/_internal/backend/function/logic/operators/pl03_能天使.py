from backend.function.logic.professions import Marksman
from backend.function.logic.formulas import calculate_physical_damage

class Pl03能天使(Marksman):
    """
    干员：能天使
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：快速弹匣 (攻击速度+12)
        self.attack_speed += 12
        
        # 天赋 2：天使的祝福 (攻击力+6%，生命上限+10%。置入战场后这个效果会同样赋予给一名随机友方单位)
        self.final_base_atk *= (1 + 0.06)
        self.base_hp *= (1 + 0.10) # 虽然不影响伤害计算，但作为天赋效果也一并处理
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 能天使的普攻没有特殊机制，直接使用基类的物理伤害计算
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔 = 基础攻击间隔 * 100 / 攻击速度
        # 注意：这里的 self.attack_interval 是干员的基础攻击间隔，self.attack_speed 包含了天赋加成
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (冲锋模式)：下次攻击变为3连射，每次射击造成相当于攻击力145%的伤害
            # 这是一个瞬发技能，替换一次普攻
            skill_atk_multiplier = 1.45
            hits_per_attack = 3
            
            # 计算单次射击的攻击力
            atk_val_per_shot = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次射击的伤害
            single_shot_damage = calculate_physical_damage(atk_val_per_shot, enemy.current_def)
            
            # 总伤害 = 单次射击伤害 * 连射次数
            total_damage = single_shot_damage * hits_per_attack
            
            # DPS = 总伤害 / 实际攻击间隔 (因为是替换一次普攻的爆发)
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (扫射模式)：攻击变为4连射，每次射击造成相当于攻击力125%的伤害
            # 持续时间：15秒
            skill_duration = 15
            skill_atk_multiplier = 1.25
            hits_per_attack = 4
            
            # 计算技能期间单次射击的攻击力
            atk_val_per_shot = self.final_base_atk * skill_atk_multiplier
            
            # 计算技能期间单次射击的伤害
            single_shot_damage = calculate_physical_damage(atk_val_per_shot, enemy.current_def)
            
            # 计算技能期间每次普攻造成的总伤害 (4连射)
            damage_per_attack_cycle = single_shot_damage * hits_per_attack
            
            # 技能期间的普攻次数
            attacks_during_skill = skill_duration / actual_atk_interval
            
            # 总伤害 = 每次普攻伤害 * 普攻次数
            total_damage = damage_per_attack_cycle * attacks_during_skill
            
            # DPS = 每次普攻伤害 / 实际攻击间隔
            dps = damage_per_attack_cycle / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (过载模式)：攻击变为5连射，攻击间隔一定程度缩短(-0.22)，攻击力提升至110%
            # 持续时间：15秒
            skill_duration = 15
            hits_per_attack = 5
            atk_boost_ratio = 1.10
            atk_interval_reduction = 0.22 # 攻击间隔缩短0.22秒
            
            # 计算技能期间的攻击力 (先提升攻击力)
            skill_enhanced_atk = self.final_base_atk * atk_boost_ratio
            
            # 计算技能期间的实际攻击间隔
            # 基础攻击间隔 (self.attack_interval) 减去缩短值，再结合攻击速度
            temp_base_atk_interval = self.attack_interval - atk_interval_reduction
            temp_actual_atk_interval = temp_base_atk_interval * 100 / self.attack_speed
            
            # 计算技能期间单次射击的伤害
            single_shot_damage = calculate_physical_damage(skill_enhanced_atk, enemy.current_def)
            
            # 计算技能期间每次普攻造成的总伤害 (5连射)
            damage_per_attack_cycle = single_shot_damage * hits_per_attack
            
            # 技能期间的普攻次数
            attacks_during_skill = skill_duration / temp_actual_atk_interval
            
            # 总伤害 = 每次普攻伤害 * 普攻次数
            total_damage = damage_per_attack_cycle * attacks_during_skill
            
            # DPS = 每次普攻伤害 / 技能期间的实际攻击间隔
            dps = damage_per_attack_cycle / temp_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)