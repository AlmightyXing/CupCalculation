from backend.function.logic.professions import Physician
from backend.function.logic.formulas import calculate_physical_damage

class Fo01闪灵(Physician):
    """
    干员：闪灵
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：黑恶魔的庇护 (攻击范围内的友方单位防御力+60)
        # 此天赋为友方单位提供防御力加成，不影响闪灵自身的伤害输出，因此在此处无需代码实现。
        
        # 天赋 2：法典 (攻击速度+10)
        self.attack_speed += 10
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望伤害。
        闪灵作为医师，其普攻为治疗，不直接对敌人造成伤害。
        因此，对敌人造成的伤害为0。
        """
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        """
        计算技能期间的总伤害和DPS。
        闪灵的所有技能均为治疗或辅助技能，不直接对敌人造成伤害。
        因此，所有技能的 total_damage 和 dps 均为 0。
        """
        # 闪灵的所有技能均不造成伤害，只提供治疗或防御增益。
        # 根据规则，如果技能不造成伤害，则 total_damage 和 dps 均为 0。
        
        # 技能 1 (信条): 攻击力+80%，攻击速度+20，持续20秒。此技能增加闪灵的治疗量和治疗速度，不造成伤害。
        # 技能 2 (自动掩护): 下次治疗使目标获得屏障和防御力提升。此技能不造成伤害。
        # 技能 3 (教条力场): 攻击力+50%，攻击范围内的所有友方单位防御力+100%，持续60秒。此技能增加闪灵的治疗量和友方防御，不造成伤害。
        
        # 因此，无论激活哪个技能，对敌人造成的总伤害和DPS均为0。
        return {"total_damage": 0.0, "dps": 0.0}
