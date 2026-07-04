from backend.function.logic.professions import DecelBinder
from backend.function.logic.formulas import calculate_arts_damage

class Sr02安洁莉娜(DecelBinder):
    """
    干员：安洁莉娜
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # trust_atk 和 final_base_atk 的计算应由基类 Operator 处理，此处无需重复
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：加速力场 (在场时全场友方单位攻速+7)
        # 此天赋对安洁莉娜自身攻速有加成，因此纳入计算。
        self.attack_speed += 7
        
        # 天赋 2：兼职工作 (技能未开启时，全场友方单位每秒回复20点生命)
        # 此天赋为生命回复效果，不直接影响安洁莉娜的伤害输出，因此不在此处进行数值修改。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 安洁莉娜作为凝滞师，其攻击造成法术伤害。
        # DecelBinder 基类特性为“攻击造成法术伤害”，此覆写符合并实现了该特性。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算受攻速影响后的基础攻击间隔
        # 注意：self.attack_speed 已经包含了天赋1“加速力场”的加成
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (秘杖·速充模式)：攻击力+110%，持续35秒
            skill_duration = 35
            atk_multiplier = 1 + 1.10 # 攻击力+110%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能持续期间的普攻次数
            hits_during_skill = skill_duration / base_actual_atk_interval
            
            # 计算单次强化普攻的法术伤害
            damage_per_hit = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 计算总伤害和DPS
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (秘杖·微粒模式)：攻击间隔极大幅度缩短(*0.15)，但每次攻击只能造成相当于攻击力45%的法术伤害，持续30秒
            skill_duration = 30
            atk_multiplier = 0.45 # 每次攻击造成攻击力45%的伤害
            atk_interval_multiplier = 0.15 # 攻击间隔缩短为0.15倍
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能期间的实际攻击间隔 (在基础实际间隔上再乘以技能的间隔缩短系数)
            skill_actual_atk_interval = base_actual_atk_interval * atk_interval_multiplier
            
            # 计算技能持续期间的普攻次数
            hits_during_skill = skill_duration / skill_actual_atk_interval
            
            # 计算单次强化普攻的法术伤害
            damage_per_hit = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 计算总伤害和DPS
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (秘杖·反重力模式)：攻击力+150%，持续25秒
            # "可以攻击5个敌人" 不影响单目标总伤和DPS计算，因此忽略。
            skill_duration = 25
            atk_multiplier = 1 + 1.50 # 攻击力+150%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算技能持续期间的普攻次数
            hits_during_skill = skill_duration / base_actual_atk_interval
            
            # 计算单次强化普攻的法术伤害
            damage_per_hit = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 计算总伤害和DPS
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
