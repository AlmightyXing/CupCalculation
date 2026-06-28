from backend.function.logic.professions import Abjurer # 遥的职业是“护佑者”，已替换为对应基类
from backend.function.logic.formulas import calculate_arts_damage

class Hk15遥(Abjurer):
    """
    干员：遥
    职业：护佑者 (攻击造成法术伤害，技能开启后改为治疗友方单位（治疗量相当于75%攻击力）)
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # final_base_atk 等基础属性应由 Operator 基类处理，此处无需重复计算
        # self.trust_atk = self.raw_data.get("confidence_atk", 0)
        # self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：浮光泡影 (每过一个攻击间隔，使范围内一名友方单位获得30%庇护的浮泡，浮泡在受到敌方伤害的短暂延迟后破碎)
        # 此天赋主要提供庇护和浮泡机制，不直接影响遥的伤害输出，故不在此处进行数值修改。

        # 天赋 2：扶摇花火 (浮泡破碎时，为所在的单位治疗相当于遥攻击力25%的生命值)
        # 此天赋是治疗效果，且是浮泡破碎时触发，不属于遥主动攻击或技能造成的伤害，故不计入遥的直接伤害输出。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 遥的普攻造成法术伤害，这与 Abjurer 的特性一致
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算技能期间的攻击次数
        # 注意：此处的 actual_atk_interval 是基于干员自身未受技能影响的攻速
        # 技能中若有攻速或攻击间隔变化，需重新计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (夜啼彩羽)：攻击速度+60，持续20秒
            # 技能期间遥的攻击仍然造成法术伤害
            duration = self.skills[skill_index]["duration"]
            
            skill_atk_speed = self.attack_speed + 60
            skill_actual_atk_interval = self.attack_interval * 100 / skill_atk_speed
            
            # 计算技能期间的普攻次数
            hits = duration / skill_actual_atk_interval
            
            # 单次普攻伤害
            damage_per_hit = calculate_arts_damage(self.final_base_atk, enemy.current_res)
            
            total_damage = hits * damage_per_hit
            dps = damage_per_hit / skill_actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (幽隙栖萤)：持续26秒 (第一次使用)
            # 职业特性：“技能开启后改为治疗友方单位（治疗量相当于75%攻击力）”
            # 技能描述：“友方单位受到遥的治疗效果时，对周围3名敌人造成相当于治疗量200%的法术伤害”
            # 因此，技能期间遥的每次“攻击”都变为治疗，并触发伤害。
            
            duration = self.skills[skill_index]["duration"]
            
            # 第一次使用，无攻击力加成 (第二次及以后使用时攻击力+40%，且持续时间无限，此处按第一次计算)
            skill_atk_val = self.final_base_atk
            
            # 每次攻击（治疗）的治疗量为 75% 攻击力
            healing_amount_per_attack = skill_atk_val * 0.75
            
            # 每次治疗触发的伤害为治疗量的 200%
            # 注意：这里是“治疗量200%的法术伤害”，不是攻击力200%
            damage_multiplier_from_healing = 2.0
            damage_base_per_hit = healing_amount_per_attack * damage_multiplier_from_healing
            
            damage_per_hit = calculate_arts_damage(damage_base_per_hit, enemy.current_res)
            
            # 攻击间隔不变，使用干员基础实际攻击间隔
            hits = duration / actual_atk_interval
            
            total_damage = hits * damage_per_hit
            dps = damage_per_hit / actual_atk_interval
            
        elif skill_index == 2:
            # 技能 3 (夏末游鳞)：攻击力+55%，攻击间隔缩短(-0.6)，持续40秒
            # 技能期间遥的攻击仍然造成法术伤害
            # 额外伤害："攻击我方浮泡的敌人将浮空4秒，在此浮空期间每秒受到相当于遥攻击力80%的法术伤害"
            
            duration = self.skills[skill_index]["duration"]
            
            # 攻击力加成
            atk_buff_ratio = 0.55
            skill_atk_val = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 攻击间隔缩短
            atk_interval_reduction = 0.6
            current_attack_interval = self.attack_interval - atk_interval_reduction
            # 确保攻击间隔不为负或0，避免除以零或负数
            if current_attack_interval <= 0:
                current_attack_interval = 0.1 
            
            skill_actual_atk_interval = current_attack_interval * 100 / self.attack_speed
            
            # --- 主动攻击伤害计算 ---
            damage_per_main_hit = calculate_arts_damage(skill_atk_val, enemy.current_res)
            hits = duration / skill_actual_atk_interval
            total_damage_main = hits * damage_per_main_hit
            
            # --- 浮空期间额外伤害计算 ---
            # 假设敌人全程处于浮空状态以最大化伤害计算
            # "每秒受到相当于遥攻击力80%的法术伤害"
            floating_damage_per_second_base = skill_atk_val * 0.80
            floating_damage_per_second = calculate_arts_damage(floating_damage_per_second_base, enemy.current_res)
            
            total_floating_damage = floating_damage_per_second * duration
            
            total_damage = total_damage_main + total_floating_damage
            dps = total_damage / duration
            
        return {"total_damage": total_damage, "dps": dps}
