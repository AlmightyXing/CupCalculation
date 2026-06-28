from backend.function.logic.professions import Ritualist
from backend.function.logic.formulas import calculate_arts_damage

class Db01死芒(Ritualist):
    """
    干员：死芒
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：复燃
        # "攻击范围内敌人被击倒时生成一个悲叹的仆役，最多召唤3个，若无法再次召唤则使一个悲叹的仆役升级"
        # "升级后：生命值+100%，攻击力+100%，防御力+40%，阻挡数+1"
        # 此天赋主要影响召唤物，不直接修改死芒自身面板。
        # 但技能会触发仆役生成/升级，间接影响伤害计算。
        self.max_servants = 3 # 最多召唤3个悲叹的仆役
        # 技能3被动：最多1名悲叹的仆役变为特殊形态，此形态下只能通过技能升级，最多升级6次
        self.max_special_servant_upgrades = 6 
        
        # 天赋 2：回光黯淡
        # "自身和召唤物攻击生命低于50%的敌人时攻击力提升至140%"
        # 假设条件满足，直接应用攻击力加成
        self.atk_buff_low_hp_ratio = 1.4
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑回光黯淡天赋的攻击力加成）
        """
        # 假设敌人生命低于50%，应用天赋加成
        effective_atk = atk_val * self.atk_buff_low_hp_ratio
        return calculate_arts_damage(effective_atk, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 死芒是塑灵术师，攻击造成法术伤害
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (噩愿)
            # 被动：每个悲叹的仆役生成和升级时对周围所有敌人造成相当于死芒攻击力450%的法术伤害
            # 开启：立刻重新召唤所有悲叹的仆役，若场上没有悲叹的仆役存在则召唤1个
            
            # 技能开启时，假设重新召唤了最大数量的仆役 (3个)。
            # 每个仆役的生成都触发一次被动伤害。
            # 技能描述中没有提到升级，只提到重新召唤。
            
            atk_multiplier = 4.5 # 450%攻击力
            num_triggers = self.max_servants # 假设重新召唤3个仆役，触发3次伤害
            
            # 瞬发伤害
            total_damage = self._calc_hit(self.final_base_atk * atk_multiplier, enemy) * num_triggers
            
            # 瞬发伤害技能的DPS计算规则
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (折朽)
            # 持续12秒，每0.5秒对目标造成相当于攻击力160%的法术伤害
            # "额外召唤2个悲叹的仆役"是副作用，不计入死芒的直接伤害
            
            duration = 12 # 技能持续时间
            hit_interval = 0.5 # 每次伤害间隔
            atk_multiplier = 1.6 # 160%攻击力
            
            # 技能期间的伤害次数
            num_hits = duration / hit_interval
            
            # 单次伤害值
            single_hit_damage = self._calc_hit(self.final_base_atk * atk_multiplier, enemy)
            
            total_damage = single_hit_damage * num_hits
            dps = single_hit_damage / hit_interval # 技能期间的DPS
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (冠死以冕)
            # 持续16秒
            # 开启：立刻对范围内所有敌人造成攻击力800%的法术伤害
            # 之后消耗一个悲叹的仆役使特殊仆役升级并回复20%生命（若悲叹的仆役已升级则翻倍），重复3次
            
            # 只有瞬发伤害，仆役升级和回复不计入死芒的直接伤害
            
            atk_multiplier = 8.0 # 800%攻击力
            
            # 瞬发伤害
            total_damage = self._calc_hit(self.final_base_atk * atk_multiplier, enemy)
            
            # 瞬发伤害技能的DPS计算规则
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
