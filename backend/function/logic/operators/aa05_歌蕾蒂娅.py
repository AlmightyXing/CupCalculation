from backend.function.logic.professions import Specialist
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Aa05歌蕾蒂娅(Specialist):
    """
    干员：歌蕾蒂娅
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：阿戈尔的波涛 (在场时，所有【深海猎人】干员每秒回复2.5%最大生命值且受到【海怪】敌人的物理与法术伤害降低25%)
        # 此天赋不直接影响歌蕾蒂娅自身的输出伤害，故在此伤害计算模块中不体现。

        # 天赋 2：弱肉强食 (攻击重量小于等于3的敌人时攻击力提升至130%)
        self.talent_atk_boost_weight_3 = 1.3
        self.talent_weight_threshold = 3
        
    def _calc_hit(self, base_atk_val: float, enemy, damage_type: str = "physical") -> float:
        """
        计算单次命中时的期望伤害，考虑弱肉强食天赋。
        """
        effective_atk_val = base_atk_val
        
        # 应用天赋2：弱肉强食
        if hasattr(enemy, 'weight') and enemy.weight <= self.talent_weight_threshold:
            effective_atk_val *= self.talent_atk_boost_weight_3
        
        if damage_type == "physical":
            return calculate_physical_damage(effective_atk_val, enemy.current_def)
        elif damage_type == "arts":
            return calculate_arts_damage(effective_atk_val, enemy.current_res)
        else:
            raise ValueError(f"Unsupported damage type: {damage_type}")

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        return self._calc_hit(self.final_base_atk, enemy, damage_type="physical")

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (缺水的大洋裂断)：下次攻击造成相当于攻击力210%的物理伤害
            # 这是一个瞬发伤害技能，计算单次触发的伤害。
            skill_atk_multiplier = 2.1
            total_damage = self._calc_hit(self.final_base_atk * skill_atk_multiplier, enemy, damage_type="physical")
            
            # 瞬发伤害的DPS按单次伤害 / 普攻间隔计算
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (缺水的掌握怒海)：持续20秒，攻击间隔50%增大，每次攻击造成相当于攻击力180%的物理伤害
            duration = 20
            atk_interval_skill_modifier = 1.5  # 攻击间隔50%增大，即变为原来的1.5倍
            
            # 计算技能期间的实际攻击间隔
            skill_attack_interval_base = self.attack_interval * atk_interval_skill_modifier
            actual_skill_atk_interval = skill_attack_interval_base * 100 / self.attack_speed
            
            # 计算技能持续期间能打出的普攻次数
            hits_during_skill = duration / actual_skill_atk_interval
            
            # 计算单次强化普攻的伤害
            skill_atk_multiplier = 1.8
            damage_per_hit = self._calc_hit(self.final_base_atk * skill_atk_multiplier, enemy, damage_type="physical")
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / actual_skill_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (缺水的碎漩狂舞)：持续8秒，每1.5秒造成130%攻击力的法术伤害
            duration = 8
            damage_interval = 1.5  # 每1.5秒造成一次伤害
            
            # 计算技能持续期间能造成的伤害次数 (按平均值计算)
            hits_during_skill = duration / damage_interval
            
            # 计算单次法术伤害
            skill_atk_multiplier = 1.3
            damage_per_hit = self._calc_hit(self.final_base_atk * skill_atk_multiplier, enemy, damage_type="arts")
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / damage_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)