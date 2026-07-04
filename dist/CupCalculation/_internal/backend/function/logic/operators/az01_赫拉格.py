from backend.function.logic.professions import Fighter
from backend.function.logic.formulas import calculate_physical_damage

class Az01赫拉格(Fighter):
    """
    干员：赫拉格
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：月盈星亏 (在场时，自身获得最高100攻击速度的坚忍（损失70%生命值时达到最大加成）)
        # 根据规则，天赋按最大层数/效果计算，因此直接加满100攻击速度。
        self.attack_speed += 100
        
        # 天赋 2：运筹帷幄 (未阻挡敌人时每秒回复60生命)
        # 此天赋为生命回复，不直接影响伤害输出，因此在伤害计算中忽略。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算赫拉格单次普攻命中时的期望物理伤害。
        赫拉格的普攻为单次物理伤害，无特殊机制。
        """
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (新月)：下次攻击的攻击力提升至175%，并连续攻击两次
            # 这是一个瞬发技能，计算一次强化攻击的伤害。
            atk_val = self.final_base_atk * 1.75
            single_hit_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            total_damage = single_hit_damage * 2  # 连续攻击两次
            
            # 瞬发技能的DPS按总伤除以一次攻击间隔计算
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (弦月)：攻击力+80%，攻击变为二连击，获得75%的物理闪避。持续13秒。
            # 这是一个增益类技能。
            skill_duration = 13
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + 0.80)
            
            # 计算单次普攻（二连击）的伤害
            single_hit_damage = calculate_physical_damage(buffed_atk, enemy.current_def)
            damage_per_attack_cycle = single_hit_damage * 2 # 攻击变为二连击
            
            # 计算技能期间能打出的攻击次数
            num_attacks = skill_duration / actual_atk_interval
            
            total_damage = damage_per_attack_cycle * num_attacks
            dps = damage_per_attack_cycle / actual_atk_interval
            
            # 物理闪避不影响伤害输出，因此忽略
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (满月)：攻击力+100%，攻击范围+2格，最多可以同时攻击3个目标。持续15秒。
            # 这是一个增益类技能。
            skill_duration = 15
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + 1.00)
            
            # 计算单次普攻的伤害
            single_hit_damage = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            # 计算技能期间能打出的攻击次数
            num_attacks = skill_duration / actual_atk_interval
            
            total_damage = single_hit_damage * num_attacks
            dps = single_hit_damage / actual_atk_interval
            
            # 攻击范围和攻击目标数不影响对单个目标的总伤和DPS，因此忽略
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)