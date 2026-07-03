from backend.function.logic.professions import Tactician
from backend.function.logic.formulas import calculate_physical_damage

class R00a可露希尔(Tactician):
    """
    干员：可露希尔
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 战术家职业特性：攻击援军阻挡的敌人时攻击力提升至150%
        # 此特性已在父类 Tactician 的 calculate_normal_hit 方法中体现。
        # 对于技能伤害，需要手动将此1.5倍率乘入计算。
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：精准投放
        # 该天赋描述召唤物机制，不直接影响可露希尔自身的伤害数值。
        
        # 天赋 2：极限调度
        # 降低部署费用和为【罗德岛】干员提供攻击力加成，不影响可露希尔自身的伤害数值。
        pass
        
    # calculate_normal_hit 方法已由父类 Tactician 提供，并包含了1.5倍率。
    # 因此，此处无需覆写。

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员的基础实际攻击间隔
        # attack_speed 是百分比，所以需要除以100
        actual_atk_interval = self.attack_interval * (100 / self.attack_speed)
        
        # 战术家职业特性：攻击援军阻挡的敌人时攻击力提升至150%
        # 此倍率需要应用于技能期间的每次攻击。
        profession_atk_multiplier = 1.5

        if skill_index == 0:
            # 技能 1 (递归策略)：
            # 持续时间8秒。该技能提供护盾和部署费用，不直接提供伤害加成。
            # 因此，技能期间的伤害为0，DPS为0。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (模型扩展)：
            # 持续时间30秒。自身攻击力+80%，同时攻击2个目标。
            # 这是一个增益类技能，计算技能持续期间的普攻伤害。
            duration = 30
            
            # 攻击力加成：基础攻击力 * (1 + 80%)
            skill_atk_buff_multiplier = 1.0 + 0.80
            
            # 计算强化后的单次普攻伤害
            # 技能攻击力 = 最终基础攻击力 * 技能倍率 * 职业特性倍率
            enhanced_atk_for_damage = self.final_base_atk * skill_atk_buff_multiplier * profession_atk_multiplier
            single_hit_damage = calculate_physical_damage(enhanced_atk_for_damage, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            num_hits = (duration or 0) / actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (Q.E.D.)：
            # 持续时间30秒。攻击间隔缩短(-0.5)，造成250%攻击力的物理伤害。
            duration = 30
            
            # 攻击间隔缩短
            # 技能直接修改攻击间隔，而不是攻击速度
            skill_attack_interval = self.attack_interval - 0.5
            # 确保攻击间隔不为负或过小，避免潜在的除以零错误
            if skill_attack_interval <= 0:
                skill_attack_interval = 0.1 # 设置一个最小值
            
            # 重新计算技能期间的实际攻击间隔
            actual_atk_interval_skill = skill_attack_interval * (100 / self.attack_speed)
            
            # 攻击力倍率：基础攻击力 * 250%
            skill_atk_multiplier = 2.5
            
            # 计算强化后的单次普攻伤害
            # 技能攻击力 = 最终基础攻击力 * 技能倍率 * 职业特性倍率
            enhanced_atk_for_damage = self.final_base_atk * skill_atk_multiplier * profession_atk_multiplier
            single_hit_damage = calculate_physical_damage(enhanced_atk_for_damage, enemy.current_def)
            
            # 计算技能期间能打出的普攻次数
            num_hits = (duration or 0) / actual_atk_interval_skill
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval_skill
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
