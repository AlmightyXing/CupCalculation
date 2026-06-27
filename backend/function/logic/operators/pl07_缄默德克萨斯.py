from backend.function.logic.professions import UnknownProfession

class Pl07缄默德克萨斯(UnknownProfession):
    """
    干员：缄默德克萨斯
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.apply_talents()
        
    def apply_talents(self):
        # TODO: 根据 self.raw_data 中的天赋实现逻辑
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # TODO: 覆写基类普攻期望（处理特殊破甲、连击等）
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> float:
        # TODO: 覆写基类技能总伤计算，返回对应技能单次爆发的总伤害
        return super().calculate_skill_damage(enemy, skill_index, target_count)
