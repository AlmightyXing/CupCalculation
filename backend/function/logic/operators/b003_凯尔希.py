from backend.function.logic.professions import Medic
from backend.function.logic.formulas import calculate_physical_damage, calculate_true_damage

class B003凯尔希(Medic):
    """
    干员：凯尔希
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # Mon3tr的基础属性 (基于游戏内数据和凯尔希面板)
        # Mon3tr的攻击力通常是凯尔希攻击力的100%
        self.mon3tr_base_atk = self.final_base_atk
        self.mon3tr_atk_interval = 1.2 # Mon3tr的基础攻击间隔
        self.mon3tr_atk_speed = 100 # Mon3tr的基础攻击速度 (默认100)
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：Mon3tr
        # "可以使用并治疗Mon3tr..." - Mon3tr的存在和基础属性已在__init__中定义。
        # "Mon3tr不在凯尔希攻击范围内时防御力降至0" - 此条件不影响Mon3tr的攻击力计算，故不在此处处理。
        
        # 天赋 2：不毁重构
        # "Mon3tr在被击倒后...造成1200点真实伤害" - 这是一个Mon3tr的死亡效果，不属于持续性伤害加成，故不在此处处理。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 凯尔希自身普攻不造成伤害，只进行治疗，因此对敌人造成的伤害为0。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 凯尔希的技能主要影响Mon3tr，因此这里计算的是Mon3tr在技能期间造成的伤害。
        
        # Mon3tr的实际攻击间隔 (技能期间Mon3tr自身攻击速度可能变化，但凯尔希S2的攻速加成是给凯尔希自己的)
        # 默认Mon3tr没有攻速加成，除非技能明确说明。
        mon3tr_actual_atk_interval = self.mon3tr_atk_interval * 100 / self.mon3tr_atk_speed
        
        if skill_index == 0:
            # 技能 1 (指令：结构加固)：自身和Mon3tr的防御力+150%，自身获得50%的物理格挡
            # 这是防御性技能，不直接增加Mon3tr的伤害输出。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (指令：战术协同)：自身的攻击速度+100，Mon3tr的攻击力+90%，Mon3tr可以攻击阻挡的所有敌人
            skill_duration = 20 # 秒
            
            # Mon3tr攻击力加成
            mon3tr_skill_atk_multiplier = 1 + 0.90 # +90%攻击力
            mon3tr_current_atk = self.mon3tr_base_atk * mon3tr_skill_atk_multiplier
            
            # Mon3tr的攻击速度没有变化，凯尔希的攻速加成不影响Mon3tr的伤害。
            
            # 计算技能期间Mon3tr的普攻次数
            num_hits = skill_duration / mon3tr_actual_atk_interval
            
            # 计算单次普攻伤害 (物理伤害)
            dmg_per_hit = calculate_physical_damage(mon3tr_current_atk, enemy.current_def)
            
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / mon3tr_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (指令：熔毁)：Mon3tr的防御力+200%，技能期间攻击力从+260%逐渐降低至+0%且伤害类型变为真实
            skill_duration = 20 # 秒
            
            # 攻击力从+260%逐渐降低至+0%。取平均值作为技能期间的攻击力加成。
            # (260% + 0%) / 2 = 130%
            mon3tr_skill_atk_multiplier = 1 + (2.60 + 0.0) / 2 # 平均攻击力加成
            mon3tr_current_atk = self.mon3tr_base_atk * mon3tr_skill_atk_multiplier
            
            # 伤害类型变为真实伤害
            
            # Mon3tr的攻击速度没有变化。
            
            # 计算技能期间Mon3tr的普攻次数
            num_hits = skill_duration / mon3tr_actual_atk_interval
            
            # 计算单次普攻伤害 (真实伤害)
            dmg_per_hit = calculate_true_damage(mon3tr_current_atk)
            
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / mon3tr_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)