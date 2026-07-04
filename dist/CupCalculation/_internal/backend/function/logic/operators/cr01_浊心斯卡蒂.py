from backend.function.logic.professions import Bard
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Cr01浊心斯卡蒂(Bard):
    """
    干员：浊心斯卡蒂
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：远古血亲
        # "可以使用一个持续25秒的海嗣，海嗣的攻击范围视为自身攻击范围的延伸"
        # 此天赋不直接影响浊心斯卡蒂自身的攻击力或伤害输出，因此在伤害计算中不体现。
        
        # 天赋 2：捕食习性
        # "自身或海嗣攻击范围内存在其他我方干员时，自身攻击力+6%；
        # 存在【深海猎人】干员时改为攻击力+15%"
        # 根据规则，天赋对提高伤害有帮助的均纳入考虑，且可叠加层数按最大层数叠加。
        # 因此，假设存在【深海猎人】干员，取最大攻击力加成15%。
        self.final_base_atk *= (1 + 0.15)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 浊心斯卡蒂的特性是“不攻击”，因此其普攻不造成任何伤害。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 浊心斯卡蒂不进行普攻，因此实际攻击间隔对于计算DPS（除了S3的真伤）没有直接意义，
        # 但为了遵循模板，我们仍定义它。
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (同归殊途之吟)
            # "立即回复自身所有生命值且生命上限+170%，特性效果提高至80%，
            # 攻击范围内我方所有单位受到伤害的50%直接转移给浊心斯卡蒂承担（同类效果取最高）"
            # 该技能主要提供治疗、生命上限提升和伤害转移，不直接造成伤害，
            # 也不提供攻击力加成以供计算伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (同葬无光之愿)
            # "攻击范围内所有其他友方单位获得相当于浊心斯卡蒂60%攻击力与防御力的鼓舞效果，
            # 自身特性效果提高至20%"
            # 该技能为永续技能 (duration: null)，主要提供鼓舞效果，不直接造成伤害，
            # 也不提供攻击力加成以供计算伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 ("潮涌，潮枯")
            # "特性变为自身每秒流失5%生命，使范围内所有敌人每秒受到70%攻击力的真实伤害
            # （自身与海嗣造成的伤害可叠加），范围内所有友方单位获得相当于浊心斯卡蒂110%攻击力的鼓舞效果"
            # 这是浊心斯卡蒂唯一直接造成伤害的技能，且为真实伤害。
            
            skill_duration = 20 # 技能持续时间为20秒
            
            # 每秒真实伤害 = 自身攻击力 * 70%
            # 真实伤害无视敌方防御和法术抗性，因此无需调用伤害公式。
            damage_per_second = self.final_base_atk * 0.70
            
            # 技能期间的总伤害 = 每秒伤害 * 持续时间
            total_damage = damage_per_second * skill_duration
            
            # 技能期间的DPS即为每秒伤害
            dps = damage_per_second
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果传入了未知的技能索引，则调用基类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)
