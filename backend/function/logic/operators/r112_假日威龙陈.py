from backend.function.logic.professions import Spreadshooter # 假日威龙陈的职业是散射手
from backend.function.logic.formulas import calculate_physical_damage

class R112假日威龙陈(Spreadshooter):
    """
    干员：假日威龙陈
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：节约风气 (在场时自身弹药类技能攻击时20%概率不消耗对应弹药)
        # 此天赋影响技能总弹药消耗，但对于单次技能循环的期望伤害计算，我们假设弹药正常消耗，故不在此处直接修改面板属性。
        
        # 天赋 2：假日余韵 (攻击速度+8，当场地中存在水地形时改为攻击速度+12)
        # 默认不考虑水地形，取攻击速度+8。如果需要考虑水地形，需在外部传入环境参数。
        self.attack_speed += 8
        
    def _calc_single_hit_damage(self, atk_val: float, enemy, apply_profession_bonus: bool = False, def_reduction: int = 0) -> float:
        """
        计算单次命中时的期望物理伤害，考虑散射手特性和防御力减免。
        散射手特性：对自己前方一横排的敌人攻击力提升至150%。
        
        :param atk_val: 当前攻击力数值。
        :param enemy: 敌人对象。
        :param apply_profession_bonus: 是否应用散射手前方一横排150%攻击力加成。
        :param def_reduction: 额外防御力减免数值。
        :return: 单次命中造成的期望物理伤害。
        """
        effective_atk = atk_val
        if apply_profession_bonus:
            effective_atk *= 1.5 # 对前方一横排的敌人攻击力提升至150%
            
        effective_def = max(0, enemy.current_def - def_reduction)
            
        return calculate_physical_damage(effective_atk, effective_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻默认目标在前方一横排，享受150%攻击力加成
        return self._calc_single_hit_damage(self.final_base_atk, enemy, apply_profession_bonus=True)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (高压冲击)：攻击力+100%，攻击时对攻击范围内的所有敌人应用特性加成；攻击装有4发弹药
            skill_atk_multiplier = 2.0 # 基础攻击力 * (1 + 100%)
            ammo_count = 4
            
            enhanced_base_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能描述明确“应用特性加成”，故享受前方150%攻击力加成
            single_hit_damage = self._calc_single_hit_damage(enhanced_base_atk, enemy, apply_profession_bonus=True)
            
            total_damage = single_hit_damage * ammo_count
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (“堇青之夜”)：攻击力+80%，每次攻击在范围内生成粘液(防御力-170)；攻击装有8发弹药
            # 注意：此技能描述未提及“应用特性加成”，故不享受前方150%攻击力加成
            skill_atk_multiplier = 1.8 # 基础攻击力 * (1 + 80%)
            ammo_count = 8
            def_reduction = 170 # 粘液效果：防御力-170
            
            enhanced_base_atk = self.final_base_atk * skill_atk_multiplier
            
            # 不应用特性加成
            single_hit_damage = self._calc_single_hit_damage(enhanced_base_atk, enemy, apply_profession_bonus=False, def_reduction=def_reduction)
            
            total_damage = single_hit_damage * ammo_count
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (“假日风暴”)：攻击力+100%，攻击造成两次伤害，对攻击范围内的所有敌人应用特性加成，
            # 每次攻击生成粘液(防御力-220)；攻击装有32发弹药，每次攻击消耗2发
            skill_atk_multiplier = 2.0 # 基础攻击力 * (1 + 100%)
            def_reduction = 220 # 粘液效果：防御力-220
            ammo_per_attack = 2 # 每次攻击消耗2发弹药
            total_ammo = 32
            num_attacks = total_ammo // ammo_per_attack # 技能期间总攻击次数
            
            enhanced_base_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能描述明确“应用特性加成”，故享受前方150%攻击力加成
            single_hit_damage_instance = self._calc_single_hit_damage(enhanced_base_atk, enemy, apply_profession_bonus=True, def_reduction=def_reduction)
            
            # 每次攻击造成两次伤害
            single_attack_total_damage = single_hit_damage_instance * 2
            
            total_damage = single_attack_total_damage * num_attacks
            dps = single_attack_total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)