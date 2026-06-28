from backend.function.logic.professions import Merchant
from backend.function.logic.formulas import calculate_physical_damage

class Lm22琳琅诗怀雅(Merchant):
    """
    干员：琳琅诗怀雅
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：大买家
        # "开启技能时获得1枚金币（可用于技能消耗），技能期间每次特性消耗费用时获得1枚金币，并提升自身4%的攻击力（最多叠加8次）"
        # 对于伤害计算，我们假设技能期间能达到最大叠加层数。
        # 最大叠加层数：8次
        # 每次提升：4%攻击力
        # 总计提升：8 * 4% = 32%攻击力
        # 这个加成只在技能期间生效，因此在技能计算时应用，这里存储乘数。
        self.talent_1_skill_atk_multiplier = 1 + (0.04 * 8)
        
        # 天赋 2：破财消灾
        # "受到致命伤害时，若费用足够则消耗5点部署费用使生命恢复到70%，每次触发该天赋时消耗的费用翻倍"
        # 这是生存天赋，不影响伤害计算，因此无需在apply_talents中修改属性。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 琳琅诗怀雅的普攻是标准的物理伤害，没有特殊机制（如无视防御、法术伤害等）。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 技能期间的攻击力基数，考虑天赋1的加成。
        # 根据规则，增益是先触发的，所以爆发伤害和技能期间的普攻都应使用强化后的攻击力。
        enhanced_atk_for_skill = self.final_base_atk * self.talent_1_skill_atk_multiplier
        
        if skill_index == 0:
            # 技能 1 (仗义疏财)：
            # "消耗一枚金币，下一次攻击会为周围八格内血量不足70%的一名友方单位恢复相当于攻击力80%的生命；携带此技能时金币上限为3"
            # 这是治疗技能，不造成伤害。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (“见面礼”)：
            # "消耗一枚金币在范围内一个可放置且可通行的地面放置香槟炸弹，
            # 香槟炸弹会对触碰到的首个敌人造成相当于攻击力200%的物理伤害，并使目标停顿2秒；
            # 香槟炸弹在场3秒后可额外造成一次伤害；携带此技能时金币上限为5"
            # 总计造成 200% + 200% = 400% 攻击力的物理伤害。
            
            burst_atk_multiplier = 4.0 # 200% (首次) + 200% (额外)
            atk_val = enhanced_atk_for_skill * burst_atk_multiplier
            
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发伤害技能的DPS计算方式：total_damage / actual_atk_interval。
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (千金一掷)：
            # "攻击变为二连击，击倒敌人时获得一枚金币；
            # 主动关闭技能时消耗所有金币对前方范围内敌人随机攻击，每消耗一枚金币造成一次相当于攻击力150%的物理伤害，并将目标中等力度地向前推开；
            # 持续时间无限，可随时主动关闭技能；携带此技能时金币上限为10"
            
            # 这是永续技能，根据规则，total_damage为0，主要计算DPS。
            total_damage = 0.0
            
            # 技能期间攻击变为二连击。
            single_hit_damage = calculate_physical_damage(enhanced_atk_for_skill, enemy.current_def)
            damage_per_attack_cycle = single_hit_damage * 2 # 二连击
            
            dps = damage_per_attack_cycle / actual_atk_interval
            
            # 主动关闭技能时的爆发伤害不计入永续技能的持续DPS或total_damage。
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)