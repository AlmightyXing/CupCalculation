from backend.function.logic.professions import UnknownProfession

class Rl10淬羽赫默(UnknownProfession):
    """
    干员：淬羽赫默
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.apply_talents()
        
    def apply_talents(self):
        # TODO: 根据 self.raw_data 中的天赋实现逻辑
        pass
        
    def calculate_dps(self, enemy, skill_index: int = -1):
        # TODO: 实现具体技能的特殊 DPS 计算逻辑
        return super().calculate_dps(enemy, skill_index)
