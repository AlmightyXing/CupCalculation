from backend.function.logic.professions import WanderingMedic
# 纯烬艾雅法拉作为行医，其普攻和技能主要为治疗和提供增益，不对敌方单位造成伤害。
# 因此，无需导入 calculate_physical_damage 或 calculate_arts_damage。

class Ln10纯烬艾雅法拉(WanderingMedic):
    """
    干员：纯烬艾雅法拉
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：氤氲 (普通治疗使目标每秒额外受到一次治疗量和元素损伤回复量为10%的增益治疗，持续6秒（最多叠加3层）)
        # 该天赋主要影响治疗量和元素损伤回复量，不直接影响对敌方单位造成的伤害。
        # 因此，在计算对敌伤害时，此天赋不修改干员的攻击力或攻击速度。
        
        # 天赋 2：火山灰疗愈 (攻击范围内的友方单位生命上限+6%，且受到的元素损伤降低12%)
        # 该天赋为友方单位提供增益，不直接影响对敌方单位造成的伤害。
        # 因此，在计算对敌伤害时，此天赋不修改干员的攻击力或攻击速度。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 纯烬艾雅法拉是行医，其普攻为治疗友方单位，不对敌方单位造成伤害。
        # 根据伤害计算规则，此方法应返回对单个敌方目标造成的期望伤害。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 纯烬艾雅法拉是行医，其技能主要为治疗或提供增益，不对敌方单位造成伤害。
        # 因此，所有技能的对敌总伤害 (total_damage) 和技能期间DPS (dps) 均为0。
        
        # actual_atk_interval = self.attack_interval * 100 / self.attack_speed 
        # 此处无需计算实际攻击间隔，因为不对敌方造成伤害。
        
        if skill_index == 0:
            # 技能 1 (无声润物)：攻击力+40%，每次可额外治疗一名单位，攻击范围内所有友方单位每秒回复纯烬艾雅法拉攻击力8%的元素损伤
            # 永续技能 (duration: null)，但不对敌方造成伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (云霭荫佑)：立即对攻击范围内所有友方单位进行一次治疗，并生成一个持续20秒的范围损伤屏障，为范围内的友方单位吸收相当于攻击力900%的元素损伤
            # 瞬发治疗和元素损伤吸收，不对敌方造成伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (火山回响)：攻击范围扩大至整个战场，治疗变为60%治疗量和元素损伤回复量的5连发，优先治疗不同的目标，第二天赋的效果提升至5倍
            # 持续治疗和元素损伤回复，不对敌方造成伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        # 如果传入了未定义的技能索引，则返回默认的0伤害。
        return {"total_damage": 0.0, "dps": 0.0}
