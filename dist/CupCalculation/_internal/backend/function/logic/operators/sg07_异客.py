from backend.function.logic.professions import ChainCaster
from backend.function.logic.formulas import calculate_arts_damage

class Sg07异客(ChainCaster):
    """
    干员：异客
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋属性，确保它们在apply_talents中被正确设置
        self.talent_1_dmg_boost_ratio = 0.0 # 机理分析：伤害提升比例
        self.talent_2_atk_boost_ratio = 0.0 # 孤卒：攻击力提升比例
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：机理分析 (攻击命中生命值在80%以上的敌人时，3秒内异客对其造成的伤害提升20%)
        # 为最大化伤害，假设条件满足
        self.talent_1_dmg_boost_ratio = 0.20
        
        # 天赋 2：孤卒 (当周围4格没有敌人时，攻击力+8%)
        # 为最大化伤害，假设条件满足，直接加到最终基础攻击力上
        self.talent_2_atk_boost_ratio = 0.08
        self.final_base_atk *= (1 + self.talent_2_atk_boost_ratio)
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑机理分析天赋的伤害提升）。
        异客是链术师，攻击造成法术伤害。
        """
        # 计算基础法术伤害
        damage = calculate_arts_damage(atk_val, enemy.current_res)
        
        # 应用天赋 1：机理分析 (伤害提升)
        damage *= (1 + self.talent_1_dmg_boost_ratio)
        
        return damage

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 异客作为链术师，攻击会在多个敌人间跳跃，但伤害计算只针对第一个目标。
        # 后续跳跃的伤害降低不计入单目标DPS。
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，考虑攻速加成
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (电能之触)：下次攻击时攻击力提升至250%
            # 这是一个单次强化攻击的技能。
            
            # 计算强化后的攻击力
            skill_atk_val = self.final_base_atk * 2.50
            
            # 计算单次强化攻击的总伤害
            total_damage = self._calc_arts_hit(skill_atk_val, enemy)
            
            # 瞬发技能的DPS计算为总伤害除以一次普攻的实际攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (聚焦指令)：攻击距离+1，攻击力+30%，攻击间隔较大幅度缩短(-50%)，攻击最大弹跳次数提升至5
            # 这是一个持续增益类技能。
            
            duration = 35 # 技能持续时间
            atk_boost_ratio = 0.30 # 攻击力提升30%
            atk_interval_reduction_ratio = 0.50 # 攻击间隔缩短50% (即变为原先的50%)
            
            # 计算技能期间的攻击力 (在最终基础攻击力上进行加成)
            skill_atk_val = self.final_base_atk * (1 + atk_boost_ratio)
            
            # 计算技能期间的实际攻击间隔
            # 攻击间隔缩短通常是在应用攻速修正后的基础上再次修正
            skill_actual_atk_interval = actual_atk_interval * (1 - atk_interval_reduction_ratio)
            
            # 计算技能期间单次普攻的伤害
            single_hit_damage = self._calc_arts_hit(skill_atk_val, enemy)
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = duration / skill_actual_atk_interval
            
            # 计算技能期间的总伤害
            total_damage = num_hits * single_hit_damage
            
            # DPS为技能期间单次普攻伤害除以技能期间的实际攻击间隔
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (辉煌裂片)：立即寻找大范围内生命值最高的目标，在其位置生成持续4秒的雷暴区域，
            # 期间每0.5秒以150%的攻击力对雷暴区域内的随机敌人进行一次额外攻击；可充能2次
            # 这是一个持续造成额外伤害的技能。
            
            duration = 4 # 雷暴区域持续时间
            hit_interval = 0.5 # 每0.5秒进行一次额外攻击
            atk_multiplier = 1.50 # 额外攻击以150%攻击力造成伤害
            
            # 计算额外攻击的攻击力
            skill_atk_val = self.final_base_atk * atk_multiplier
            
            # 计算单次额外攻击的伤害
            single_hit_damage = self._calc_arts_hit(skill_atk_val, enemy)
            
            # 计算持续期间额外攻击的总次数
            num_hits = duration / hit_interval
            
            # 计算技能期间的总伤害
            total_damage = num_hits * single_hit_damage
            
            # DPS为总伤害除以技能持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)