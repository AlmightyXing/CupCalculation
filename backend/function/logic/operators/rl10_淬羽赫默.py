from backend.function.logic.professions import Abjurer
from backend.function.logic.formulas import calculate_arts_damage

class Rl10淬羽赫默(Abjurer):
    """
    干员：淬羽赫默
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1: 无声砥柱 (防御/治疗天赋，不直接提升自身伤害)
        # 天赋 2: 丰润羽翼 (治疗天赋，不直接提升自身伤害)
        # 淬羽赫默的天赋均不直接提升自身伤害，因此此处无需修改攻击力、攻击速度等属性。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 淬羽赫默的攻击造成法术伤害
        # Abjurer特性：攻击造成法术伤害。此覆写符合特性。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # Abjurer特性：技能开启后改为治疗友方单位。
        # 因此，在DPS模拟中，淬羽赫默在技能期间不造成伤害，而是进行治疗。
        # 如果需要模拟治疗量，则需要扩展模拟器功能。
        
        # 技能1 (进取之心): 攻击力+80%，持续25秒
        # 技能2 (俯瞰视界): 攻击速度+60，持续12秒
        # 技能3 (无畏者协议): 攻击力+30%，持续60秒
        # 无论哪个技能，淬羽赫默（作为Abjurer）在技能期间都转为治疗模式，不造成伤害。
        
        # 返回0伤害和0 DPS
        return {"total_damage": 0.0, "dps": 0.0}
