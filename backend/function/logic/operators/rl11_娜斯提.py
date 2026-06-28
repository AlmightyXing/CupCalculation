from backend.function.logic.professions import Artificer
from backend.function.logic.formulas import calculate_physical_damage

class Rl11娜斯提(Artificer):
    """
    干员：娜斯提
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # trust_atk 和 final_base_atk 的计算已在基类 Operator 的 __init__ 方法中处理，
        # Artificer 继承 Operator，并调用了 super().__init__(data)，因此此处无需重复计算。
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 0: 前方施工 (影响装置数量和效果，不直接影响娜斯提自身伤害)
        # 天赋 1: 注意安全 (提供庇护和技力回复，不直接影响娜斯提自身伤害)
        # 娜斯提的天赋不直接提供攻击力、攻击速度或特殊伤害机制的加成，
        # 因此此方法中没有直接修改娜斯提自身伤害计算的逻辑。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 娜斯提的天赋不影响普攻伤害计算方式（无特殊破甲、连击等），
        # Artificer 类本身没有覆写 calculate_normal_hit，因此会调用 Operator 的默认物理伤害计算。
        # 确保父类的特性（如 Artificer 的攻击间隔）已通过 super().__init__ 继承。
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # Artificer 的 attack_interval 为 1.5，已通过 super().__init__ 继承。
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (拱卫):
            # 描述中 "装置使前方干员防御力提升攻击力+80%，防御力+80%，同时攻击阻挡的所有敌人"
            # 考虑到计算娜斯提自身伤害，我们假设 "攻击力+80%" 作用于娜斯提自身，且她持续攻击。
            # 持续时间: 40秒
            duration = 40
            atk_buff_ratio = 0.80
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算单次强化普攻伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的普攻次数
            num_hits = duration / actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (执行):
            # 描述中明确提到 "停止攻击"
            # 因此，娜斯提自身在此技能期间不造成伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (栖脚地):
            # 描述中 "攻击力+160%，防御力+160%" 是对高台装置或其上干员的增益，不作用于娜斯提自身。
            # 娜斯提自身在此技能期间不获得伤害增益，且技能本身无爆发伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        # 如果技能索引不匹配，调用基类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)
