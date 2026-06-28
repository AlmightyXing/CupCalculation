from backend.function.logic.professions import Bard
from backend.function.logic.formulas import calculate_true_damage

class Dwdb魔王(Bard):
    """
    干员：魔王
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：过往尘埃
        # "魔王周围持续围绕3枚“微尘”，“微尘”碰撞友方干员时，消失并使该干员受到魔王特性效果提升至1.5倍，持续6秒，消失的“微尘”在6秒后重生"
        # 此天赋主要影响友方干员受到的治疗量，不直接影响魔王对敌方的伤害输出。
        pass
        
        # 天赋 2：魔王残响
        # "在场时，所有友方单位受到【萨卡兹】敌人的伤害降低10%"
        # 此天赋为友方防御性增益，不直接影响魔王对敌方的伤害输出。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 魔王特性（继承自吟游者）：不攻击，持续恢复范围内所有友军生命。
        # 因此，普攻对敌人不造成伤害。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔用于计算DPS，即使魔王不普攻，其基础攻击间隔仍是计算瞬发技能DPS的基准。
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (往昔萦绕身旁)：
            # "自身特性效果提高至35%，“微尘”的重生速度加快，持续时间无限"
            # 永续技能，主要为辅助和治疗增益，不造成直接伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (明日渺远不及)：
            # 持续35秒。
            # "“微尘”上限+3，立刻获得6枚“微尘”，“微尘”旋转半径扩大，攻击范围内所有其他友方单位获得相当于魔王100%攻击力的鼓舞效果，
            # “微尘”不再碰撞友方干员，“微尘”碰撞敌方单位时造成相当于魔王攻击力275%的真实伤害，并使目标束缚3.5秒"
            
            # 此技能使“微尘”获得对敌方造成真实伤害的能力。
            # 由于技能描述中未明确“微尘”的碰撞频率，根据伤害计算规则，
            # 假设在技能激活时，所有6枚“微尘”对单个敌人造成一次爆发伤害。
            # 这是一种瞬发爆发伤害的计算方式。
            
            # 强化后的攻击力 (技能本身没有攻击力加成，直接使用最终基础攻击力)
            atk_for_dust = self.final_base_atk * 2.75
            
            # 6枚微尘，每枚造成一次真实伤害
            total_damage = calculate_true_damage(atk_for_dust) * 6
            
            # DPS计算：总伤 / 实际攻击间隔 (按照瞬发技能的规则)
            # 这里的actual_atk_interval是魔王自身的，并非微尘的攻击频率。
            # 规则要求瞬发伤害的dps计算方式是 total_damage / actual_atk_interval。
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (编织重构现世)：
            # 持续30秒。
            # "攻击范围扩大，自身特性效果提高至90%，“微尘”不再消失，
            # 攻击范围内所有其它友方单位获得相当于魔王100%的最大生命值的鼓舞效果，
            # 每隔2秒重新分配攻击范围内所有友方单位的生命"
            # 此技能为纯粹的辅助/治疗技能，不造成直接伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
