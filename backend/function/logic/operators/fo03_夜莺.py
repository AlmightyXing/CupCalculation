from backend.function.logic.professions import UnknownProfession
# 夜莺是群愈师，她的普攻和技能均不造成伤害，因此无需导入伤害计算公式。
# from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Fo03夜莺(UnknownProfession):
    """
    干员：夜莺
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 夜莺的天赋主要提供法术抗性、物理闪避和召唤幻影，
        # 这些天赋不直接影响夜莺自身的伤害输出，因此在伤害计算中无需额外处理。
        # 天赋 1: 白恶魔的庇护 (攻击范围内的友方单位法术抗性+15)
        # 天赋 2: 转瞬即逝的幻影 (可以使用幻影，幻影有法抗、物理闪避等)
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 夜莺是群愈师，她的普攻是治疗友方单位，不造成伤害。
        # 因此，单次普攻的期望伤害为0。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 夜莺的所有技能均为治疗或提供增益（如法术抗性、护盾、法术闪避），不造成伤害。
        # 因此，所有技能的伤害均为0。
        
        # 实际攻击间隔在此处不用于伤害计算，因为夜莺不造成伤害。
        # actual_atk_interval = self.attack_interval * 100 / self.attack_speed 
        
        if skill_index == 0:
            # 技能 1 (治疗强化·γ型): 攻击力+90% (提升治疗量，不造成伤害)
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (法术护盾): 提供法术护盾和法术抗性 (不造成伤害)
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (圣域): 攻击范围扩大，攻击力+80%，友方单位法术抗性+150%并获得25%的法术闪避 
            # (提升治疗量和友方生存，不造成伤害)
            return {"total_damage": 0.0, "dps": 0.0}
            
        # 如果技能索引不匹配，则调用基类的处理方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)