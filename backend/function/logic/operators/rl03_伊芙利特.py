from backend.function.logic.professions import BlastCaster
from backend.function.logic.formulas import calculate_arts_damage

class Rl03伊芙利特(BlastCaster):
    """
    干员：伊芙利特
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：精神融解 (攻击范围内的敌军法术抗性-40%)
        # 这是一个对敌人的法术抗性削减，在计算伤害时应用
        self.talent_res_debuff_ratio = 0.40
        
        # 天赋 2：莱茵回路 (每6秒额外回复2点技力)
        # 此天赋影响技力回复，不直接影响单次攻击或技能期间的伤害计算，故不在此处修改属性。
        
    def _calc_arts_hit(self, atk_val: float, enemy, additional_res_debuff_flat: int = 0) -> float:
        """
        计算单次命中时的期望法术伤害，考虑精神融解天赋和技能可能带来的额外法抗削减。
        """
        # 应用天赋 1: 精神融解 (法术抗性-40%)
        effective_res = enemy.current_res * (1 - self.talent_res_debuff_ratio)
        
        # 应用技能可能带来的额外固定法抗削减
        effective_res -= additional_res_debuff_flat
        
        # 法术抗性不能低于0
        effective_res = max(0, effective_res)
        
        return calculate_arts_damage(atk_val, effective_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 伊芙利特造成法术伤害，并应用其天赋1
        # BlastCaster特性是群体法术伤害，但单次命中伤害计算逻辑与普通法术伤害一致，
        # 仅影响目标数量，不影响单次伤害倍率。
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (狂热): 攻击力+20%，攻击速度+80，持续20秒
            duration = 20
            
            # 计算强化后的属性
            buffed_atk = self.final_base_atk * (1 + 0.20)
            buffed_attack_speed = self.attack_speed + 80
            buffed_actual_atk_interval = self.attack_interval * 100 / buffed_attack_speed
            
            # 计算强化后的单次普攻伤害
            dmg_per_hit = self._calc_arts_hit(buffed_atk, enemy)
            
            # 计算技能持续期间的普攻次数
            hits_during_skill = duration / buffed_actual_atk_interval
            
            total_damage = dmg_per_hit * hits_during_skill
            dps = dmg_per_hit / buffed_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (炎爆): 下次攻击造成相当于攻击力250%的法术伤害
            # 注意：防御力削减和灼烧伤害是次要效果，不计入伊芙利特直接造成的总伤害。
            
            atk_val = self.final_base_atk * 2.50
            total_damage = self._calc_arts_hit(atk_val, enemy)
            
            # 对于瞬发技能，DPS为总伤害除以常规攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (灼地): 对攻击范围内的地面敌人造成每秒相当于攻击力140%的法术伤害，命中目标的法术抗性-20，持续20秒
            # 注意：自身生命流失不计入对敌人的伤害输出。
            duration = 20
            
            # 技能3有额外的固定法抗削减
            skill_res_debuff_flat = 20
            
            # 技能描述为“每秒相当于攻击力140%的法术伤害”，因此将此作为每秒的攻击力值
            dmg_per_second_atk_val = self.final_base_atk * 1.40
            
            # 计算实际每秒伤害，应用所有法抗削减
            dps = self._calc_arts_hit(dmg_per_second_atk_val, enemy, additional_res_debuff_flat=skill_res_debuff_flat)
            
            total_damage = dps * duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
