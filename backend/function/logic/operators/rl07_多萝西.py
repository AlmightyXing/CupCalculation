from backend.function.logic.professions import Trapmaster
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Rl07多萝西(Trapmaster):
    """
    干员：多萝西
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：共振装置 (不直接影响自身面板伤害计算)
        # "可以使用8个共振装置（最多拥有10个），踩上去的第一个敌人会触发其效果，部署后立刻在攻击范围内召唤2个共振装置"
        # 此天赋描述的是陷阱机制和部署，不直接修改干员的攻击力、攻速等数值。

        # 天赋 2：梦想家 (陷阱触发后，多萝西获得2%的攻击力，最多叠加10层)
        # 按照规则，只要天赋对提高伤害有帮助，均纳入考虑，且可叠加层数的天赋按最大层数叠加。
        max_stacks = 10
        atk_per_stack_ratio = 0.02 # 2%
        self.final_base_atk *= (1 + max_stacks * atk_per_stack_ratio)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 多萝西的普攻是物理伤害，没有特殊机制（如无视防御、连击等）
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 陷阱师的技能伤害通常是瞬发爆发，其DPS计算沿用框架规则：总伤 / 实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (危险目标清除)
            # "被动效果：陷阱触发时对目标造成相当于攻击力的450%的物理伤害，并使其防御力-35%，持续5秒"
            
            # 技能描述中的“攻击力”应为干员当前攻击力，即 self.final_base_atk
            skill_atk_multiplier = 4.5 # 450%
            
            # 敌人防御力降低35%，此效果在伤害计算前生效
            enemy_def_after_debuff = enemy.current_def * (1 - 0.35)
            
            # 计算单次陷阱触发的物理伤害
            total_damage = calculate_physical_damage(self.final_base_atk * skill_atk_multiplier, enemy_def_after_debuff)
            
            # 瞬发伤害技能的DPS计算
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (流沙区域生成)
            # "被动效果：陷阱触发时对周围所有目标造成相当于攻击力的300%的物理伤害，并使其束缚3.5秒..."
            
            skill_atk_multiplier = 3.0 # 300%
            
            # 物理伤害，无特殊防御穿透或减防
            # 即使描述“对周围所有目标”，也只计算对单个目标的伤害
            total_damage = calculate_physical_damage(self.final_base_atk * skill_atk_multiplier, enemy.current_def)
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (高速共振排障)
            # "被动效果：陷阱触发时对范围内所有目标造成相当于攻击力350%的法术伤害，使其停顿5秒..."
            
            skill_atk_multiplier = 3.5 # 350%
            
            # 法术伤害，无特殊抗性穿透
            # 即使描述“对范围内所有目标”，也只计算对单个目标的伤害
            total_damage = calculate_arts_damage(self.final_base_atk * skill_atk_multiplier, enemy.current_res)
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)