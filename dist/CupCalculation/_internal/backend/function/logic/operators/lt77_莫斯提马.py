from backend.function.logic.professions import SplashCaster
from backend.function.logic.formulas import calculate_arts_damage

class Lt77莫斯提马(SplashCaster):
    """
    干员：莫斯提马
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：技力光环·术师 (技力自然回复速度+0.4/秒)
        # 此天赋为光环效果，影响其他术师干员，不直接影响莫斯提马自身的伤害计算。
        
        # 天赋 2：主观缓时 (攻击范围内的敌人移动速度-15%)
        # 此天赋为控制效果，不直接影响莫斯提马自身的伤害计算。
        # 技能3会提升第二天赋效果，但仍是控制效果，不影响伤害数值。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 莫斯提马是扩散术师，攻击造成群体法术伤害。
        # 父类 SplashCaster 默认不覆写 calculate_normal_hit，会继承 Operator 的物理伤害计算。
        # 因此，莫斯提马需要明确覆写以确保造成法术伤害。
        # 计算单次普攻命中时的期望法术伤害。
        # 严禁在代码中乘以任何目标数。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (攻击力强化·γ型): 攻击力+100%，持续30秒
            duration = 30
            atk_multiplier = 1 + 1.00 # 攻击力+100%
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算强化后的单次普攻伤害
            damage_per_hit = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 技能期间能打出的普攻次数
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (荒时之锁): 持续7秒，每秒受到攻击力140%的法术伤害
            # 敌人晕眩效果不影响伤害计算。
            duration = 7
            damage_per_second_ratio = 1.40 # 每秒受到攻击力140%的伤害
            
            # 计算每秒的基础伤害值
            base_damage_per_second = self.final_base_atk * damage_per_second_ratio
            # 计算每秒实际造成的法术伤害
            actual_damage_per_second = calculate_arts_damage(base_damage_per_second, enemy.current_res)
            
            total_damage = actual_damage_per_second * duration
            # 对于持续伤害技能，dps即为每秒造成的伤害
            dps = actual_damage_per_second
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (序时之匙): 攻击力+170%，持续27秒
            # 攻击范围扩大、攻击变为波纹、击退、第二天赋效果提升均不影响伤害数值计算。
            duration = 27
            atk_multiplier = 1 + 1.70 # 攻击力+170%
            
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 计算强化后的单次普攻伤害
            damage_per_hit = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 技能期间能打出的普攻次数
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
