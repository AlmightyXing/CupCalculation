from backend.function.logic.professions import Summoner # 麦哲伦的职业是召唤师
from backend.function.logic.formulas import calculate_arts_damage, calculate_physical_damage

class Rl06麦哲伦(Summoner):
    """
    干员：麦哲伦
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：支援无人机·龙腾 (可以使用5个不阻挡敌人的无人机，功能随技能选择而改变)
        # 天赋 2：光学折射配件 (无人机在部署后的20秒内处于隐匿状态)
        # 麦哲伦的天赋主要描述无人机的部署机制和功能，以及无人机的隐匿特性。
        # 这些天赋不直接提供数值上的攻击力、攻速或伤害类型加成，
        # 因此在 apply_talents 中无需进行数值修改。无人机的伤害计算会体现在技能逻辑中。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 麦哲伦的普攻造成法术伤害
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 记录原始攻击速度，以便在技能计算中进行临时修改或作为基准
        # 注意：这里不直接修改 self.attack_speed 或 self.final_base_atk，
        # 而是使用局部变量来计算技能期间的属性，避免影响后续计算或状态。
        original_attack_speed = self.attack_speed
        
        # 计算技能开启前的实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / original_attack_speed
        
        total_damage = 0.0
        dps = 0.0

        if skill_index == 0:
            # 技能 1 (高效制冷模块): 持续15秒，无直接伤害增益，主要为控制。
            # 伤害计算基于技能持续期间的普攻。
            duration = self.raw_data["skills"][skill_index]["duration"]
            
            # 单次普攻伤害 (麦哲伦的普攻为法术伤害)
            single_hit_damage = self.calculate_normal_hit(enemy)
            
            # 技能期间的普攻次数
            num_hits = duration / actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (激光开采模块): 持续15秒，麦哲伦和无人机攻击速度+150，无人机变为群体法术攻击。
            duration = self.raw_data["skills"][skill_index]["duration"]
            
            # 应用攻击速度增益
            skill_attack_speed = original_attack_speed + 150
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 攻击力无额外加成，使用基础攻击力
            skill_atk_val = self.final_base_atk
            
            # 单次命中伤害 (无人机变为群体法术攻击，但计算仍按单目标)
            single_hit_damage = calculate_arts_damage(skill_atk_val, enemy.current_res)
            
            # 技能期间的普攻次数
            num_hits = duration / skill_actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / skill_actual_atk_interval
            
        elif skill_index == 2:
            # 技能 3 (武装打击模块): 持续15秒，麦哲伦和无人机攻击力+150%，无人机变为群体物理攻击。
            duration = self.raw_data["skills"][skill_index]["duration"]
            
            # 应用攻击力增益
            skill_atk_val = self.final_base_atk * (1 + 1.50) # 150%攻击力提升，即变为2.5倍
            
            # 攻击速度无额外加成，使用技能开启前的实际攻击间隔
            
            # 单次命中伤害 (无人机变为群体物理攻击，但计算仍按单目标)
            single_hit_damage = calculate_physical_damage(skill_atk_val, enemy.current_def)
            
            # 技能期间的普攻次数
            num_hits = duration / actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
        return {"total_damage": total_damage, "dps": dps}
        
        # 如果有未处理的技能索引，可以调用父类方法作为回退
        # return super().calculate_skill_damage(enemy, skill_index, target_count)