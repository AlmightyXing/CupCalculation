from backend.function.logic.professions import PrimalCaster
from backend.function.logic.formulas import calculate_arts_damage, calculate_element_damage

class Re06真言(PrimalCaster):
    """
    干员：真言
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：噤声限域 (场上敌人触发麻痹效果时立即受到相当于真言攻击力135%的元素伤害)
        # 为最大化伤害，我们假设当技能触发麻痹时，此天赋会触发。
        self.talent_1_paralysis_element_dmg_ratio = 1.35
        # 10%概率不消耗麻痹层数不直接影响伤害计算。
        
        # 天赋 2：全局洞悉 (距离真言最近的一个侵入点出场的敌人出现时立刻获得1层麻痹)
        # 此天赋提供初始麻痹，可能间接影响其他效果（如S2的麻痹层数溢出伤害），
        # 但不直接增加普攻或技能的爆发伤害。在S2计算中，我们会假设敌人已拥有麻痹层数以最大化溢出伤害。

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 真言是本源术师，攻击造成法术伤害
        # PrimalCaster特性：攻击造成法术伤害
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0

        if skill_index == 0:
            # 技能 1 (共鸣溃缩)：下次攻击造成攻击力325%的法术伤害并附带伤害30%的神经损伤，
            # 若目标处于神经损伤爆发期间则额外造成200%攻击力的元素伤害
            
            # 这是“下次攻击”技能，视为一次性爆发伤害。
            # 为最大化伤害，假设条件“目标处于神经损伤爆发期间”已满足。
            
            # 法术伤害部分
            arts_atk_val = self.final_base_atk * 3.25
            arts_dmg = calculate_arts_damage(arts_atk_val, enemy.current_res)
            
            # 额外元素伤害部分
            element_atk_val = self.final_base_atk * 2.00
            element_dmg = calculate_element_damage(element_atk_val) # 元素伤害无视防御和法术抗性
            
            total_damage = arts_dmg + element_dmg
            dps = total_damage / actual_atk_interval # 瞬发伤害，DPS按一个攻击间隔计算
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (意识联协)：持续25秒
            # 攻击间隔缩短(-0.8)，攻击造成攻击力240%的法术伤害并以短暂间隔跳跃至其他3名敌人造成攻击力120%的法术伤害，
            # 均附带伤害18%的神经损伤，爆发期间附带25%攻击力的元素伤害
            
            duration = 25
            
            # 技能期间的攻击间隔
            skill_base_atk_interval = self.attack_interval - 0.8
            # 确保攻击间隔不为负或零，设定一个最小值
            if skill_base_atk_interval <= 0:
                skill_base_atk_interval = 0.1 
            
            # 重新计算技能期间的实际攻击间隔
            skill_actual_atk_interval = skill_base_atk_interval * 100 / self.attack_speed
            
            # 主目标法术伤害
            main_arts_atk_val = self.final_base_atk * 2.40
            main_arts_dmg = calculate_arts_damage(main_arts_atk_val, enemy.current_res)
            
            # 跳跃目标法术伤害 (根据规则，只计算一个跳跃目标)
            jump_arts_atk_val = self.final_base_atk * 1.20
            jump_arts_dmg = calculate_arts_damage(jump_arts_atk_val, enemy.current_res)
            
            # 每次伤害附带的元素伤害 (主目标和跳跃目标各一份)
            element_atk_val_per_hit = self.final_base_atk * 0.25
            element_dmg_per_hit = calculate_element_damage(element_atk_val_per_hit)
            
            # 单次攻击循环的总伤害 (主目标法术+元素 + 一个跳跃目标法术+元素)
            damage_per_attack_cycle = (main_arts_dmg + element_dmg_per_hit) + (jump_arts_dmg + element_dmg_per_hit)
            
            # 技能持续期间的攻击次数
            num_attacks = duration / skill_actual_atk_interval
            
            total_damage = num_attacks * damage_per_attack_cycle
            dps = damage_per_attack_cycle / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (无言为真)：持续40秒
            # 攻击范围扩大，范围内敌人隐匿失效且麻痹层数上限降为2，攻击力+275%同时攻击2个目标，
            # 范围中干员开启技能时（包括自身）使范围内敌人获得2层麻痹（至多3次），
            # 范围内敌人麻痹层数每超过上限1层在目标及1名敌人间跳跃1次185%攻击力的元素伤害，跳跃间存在短暂间隔
            
            duration = 40
            
            # 攻击力加成后的攻击力
            skill_enhanced_atk = self.final_base_atk * (1 + 2.75)
            
            # 技能期间普攻造成的法术伤害 (“同时攻击2个目标”但根据规则只计算单个目标)
            arts_dmg_per_hit = calculate_arts_damage(skill_enhanced_atk, enemy.current_res)
            
            # 技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval
            
            # 技能期间普攻总伤害
            skill_normal_attack_total_damage = num_attacks * arts_dmg_per_hit
            
            # 爆发伤害部分
            burst_damage = 0.0
            
            # 1. 天赋1“噤声限域”触发伤害：
            # “范围中干员开启技能时（包括自身）使范围内敌人获得2层麻痹（至多3次）”
            # 每次麻痹效果触发时，天赋1会生效。最多触发3次。
            talent_1_burst_per_trigger = calculate_element_damage(self.final_base_atk * self.talent_1_paralysis_element_dmg_ratio)
            talent_1_total_burst = talent_1_burst_per_trigger * 3
            burst_damage += talent_1_total_burst
            
            # 2. 麻痹层数溢出伤害：
            # “范围内敌人麻痹层数每超过上限1层在目标及1名敌人间跳跃1次185%攻击力的元素伤害”
            # 为最大化伤害，假设敌人初始已有1层麻痹。
            # 当技能使其“获得2层麻痹”时，敌人麻痹层数从1变为3。
            # 技能将麻痹层数上限降为2，因此敌人麻痹层数超过上限1层 (3 - 2 = 1)。
            # 此溢出伤害在每次麻痹施加时（最多3次）都会触发。
            over_cap_element_atk_val = self.final_base_atk * 1.85
            over_cap_element_dmg_per_trigger = calculate_element_damage(over_cap_element_atk_val)
            over_cap_total_burst = over_cap_element_dmg_per_trigger * 3
            burst_damage += over_cap_total_burst
            
            total_damage = skill_normal_attack_total_damage + burst_damage
            
            # DPS计算：(技能期间普攻DPS) + (总爆发伤害 / 技能持续时间)
            dps = (arts_dmg_per_hit / actual_atk_interval) + (burst_damage / duration)
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
