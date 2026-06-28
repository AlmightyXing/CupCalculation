from backend.function.logic.professions import Defender
from backend.function.logic.formulas import calculate_physical_damage

class Rl02塞雷娅(Defender):
    """
    干员：塞雷娅
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        # 虽然防御力信赖和天赋会影响防御，但由于本模块只计算干员的伤害输出，
        # 且防御力不直接影响伤害输出，因此在此处仅计算攻击力。
        # self.trust_def = self.raw_data.get("confidence_def", 0) 
        
        self.final_base_atk = self.base_atk + self.trust_atk
        # self.final_base_def = self.base_def + self.trust_def # 不影响伤害，故不在此处处理
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：莱茵充能护服
        # "每在场上停留20秒，攻击力+5%，防御力+4%，最多叠加5层"
        # 根据规则，只考虑对提高伤害有帮助的天赋。
        # 攻击力加成对伤害有帮助，按最大层数叠加。
        # 防御力加成不直接影响塞雷娅的伤害输出，因此不在此处计算。
        max_stacks = 5
        atk_talent_multiplier = 1 + (0.05 * max_stacks)
        
        self.final_base_atk *= atk_talent_multiplier
        
        # 天赋 2：精神回复
        # "每次回复友方单位生命值时额外回复该单位1点技力"
        # 此天赋不直接影响塞雷娅的伤害输出，因此不在此处计算。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 塞雷娅的普攻为物理伤害，无特殊机制（如无视防御、连击等）。
        # 使用经过信赖和天赋加成后的最终基础攻击力。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 计算普攻的单次伤害和DPS，作为技能未造成伤害时的参考DPS
        normal_hit_damage = self.calculate_normal_hit(enemy)
        normal_dps = normal_hit_damage / actual_atk_interval
        
        if skill_index == 0:
            # 技能 1 (急救): "下一次攻击会为周围血量小于等于一半的一名友方单位恢复相当于攻击力180%的生命，可充能3次"
            # 该技能将普攻替换为治疗，不造成伤害。
            # 因此，技能期间的总伤害和DPS均为0。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (药物配置): "治疗附近一定范围内的所有友军相当于塞雷娅攻击力140%的生命"
            # 该技能为主动治疗技能，塞雷娅在技能期间仍会进行普攻。
            # 技能本身不造成伤害，且不改变普攻伤害。
            # 因此，技能总伤害为0，DPS为普攻DPS。
            return {"total_damage": 0.0, "dps": normal_dps}
            
        elif skill_index == 2:
            # 技能 3 (钙质化): "附近所有友军每秒回复相当于塞雷娅攻击力35%的生命，附近所有敌军受到的法术伤害+55%，移动速度-60%"
            # 该技能为增益/减益技能，塞雷娅在技能期间仍会进行普攻。
            # 技能本身不造成伤害，且不改变普攻伤害。
            # "附近所有敌军受到的法术伤害+55%" 是对敌方的Debuff，影响其他干员的法术伤害，不计入塞雷娅自身的伤害输出。
            # 因此，技能总伤害为0，DPS为普攻DPS。
            return {"total_damage": 0.0, "dps": normal_dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)