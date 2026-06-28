from backend.function.logic.professions import Medic # 假设Medic是治疗职业的基类
# 如果Medic类不存在，请根据实际情况修改为 Operator 或 UnknownProfession

class Ii09流明(Medic):
    """
    干员：流明
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：凡人之愿 (治疗的目标获得抵抗)
        # 此天赋提供控制抵抗，不直接影响治疗量或攻击速度，因此不在此处进行数值修改。
        
        # 天赋 2：应急处理 (攻击范围内的友方受到异常状态时，立刻治疗目标相当于流明攻击力80%的生命)
        # 此天赋为触发式治疗，且有冷却时间，不属于常驻的攻击力或攻击速度加成，
        # 也不直接影响普攻或技能的期望治疗量，因此不在此处进行数值修改。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 流明是疗养师，普攻造成治疗。
        # 疗养师特性：拥有较大治疗范围，但在治疗较远目标时治疗量变为80%。
        # 在计算单次普攻期望时，我们通常假设为最佳情况（即治疗近距离目标，治疗量为100%攻击力）。
        # 这里的“伤害”对于治疗干员来说，实际指“治疗量”。
        return self.final_base_atk

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 对于治疗型干员，"total_damage" 实际指 "总治疗量"，"dps" 实际指 "每秒治疗量" (HPS)。
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (沐雨)：下次攻击使目标和周围的友军每秒受到相当于55%流明攻击力的治疗效果，持续5秒
            # 这是一个持续治疗（HoT）效果，由下次普攻触发。
            # 总治疗量为 HoT_per_sec * duration。
            healing_per_sec = self.final_base_atk * 0.55
            duration = 5.0
            total_healing = healing_per_sec * duration
            
            # 对于瞬发或一次性效果的技能，DPS按总效果除以干员的攻击间隔来标准化。
            return {"total_damage": total_healing, "dps": total_healing / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (沛霖)：立刻恢复攻击范围内最多3名友方单位相当于攻击力260%的生命
            # 这是一个瞬发爆发治疗技能。
            total_healing = self.final_base_atk * 2.60
            
            # 对于瞬发技能，DPS按总效果除以干员的攻击间隔来标准化。
            return {"total_damage": total_healing, "dps": total_healing / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (灯火不灭)：攻击力+55%，攻击速度+30，优先治疗处于异常状态中的单位；
            # 只在治疗异常状态中的单位时会消耗子弹，使该次治疗量提升至攻击力的200%并解除目标所受的异常状态；
            # 攻击装有8发子弹，打完后技能结束。
            
            # 1. 计算技能期间的强化属性
            atk_buff_ratio = 0.55
            atk_spd_buff = 30
            bullet_count = 8
            bullet_heal_multiplier = 2.00 # 治疗量提升至攻击力的200%
            
            buffed_atk = self.final_base_atk * (1 + atk_buff_ratio)
            buffed_atk_speed = self.attack_speed + atk_spd_buff
            
            # 技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / buffed_atk_speed
            
            # 2. 计算总治疗量
            # 假设所有8发子弹都用于治疗处于异常状态的单位，以达到最大治疗效益。
            # 每次消耗子弹的治疗量 = 强化后的攻击力 * 200%
            healing_per_bullet_hit = buffed_atk * bullet_heal_multiplier
            total_healing = bullet_count * healing_per_bullet_hit
            
            # 3. 计算DPS
            # 根据规则，对于增益类技能，DPS = 强化后的单次普攻伤害 / 技能期间的实际攻击间隔。
            # 这里“强化后的单次普攻伤害”即为每次消耗子弹的治疗量。
            dps = healing_per_bullet_hit / skill_actual_atk_interval
            
            return {"total_damage": total_healing, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)