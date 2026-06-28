from backend.function.logic.professions import StandardBearer # 假设存在StandardBearer类对应“执旗手”职业
from backend.function.logic.formulas import calculate_physical_damage

class Vc10琴柳(StandardBearer):
    """
    干员：琴柳
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：不退之旗 (部署时自身持有军旗；军旗周围8格的干员攻击速度+10，敌人的攻击速度-10)
        # 此天赋为辅助型，影响友方和敌方单位，不直接提高琴柳自身的伤害输出，故不修改琴柳自身属性。
        
        # 天赋 2：精神感召 (部署后，下一名部署的干员费用-2)
        # 此天赋为辅助型，不直接影响琴柳自身的伤害输出，故不修改琴柳自身属性。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望物理伤害。
        琴柳的普攻没有特殊机制（如无视防御、连击等），直接计算物理伤害。
        """
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于DPS计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (支援号令·γ型)：停止攻击，持续时间内回复总共18点部署费用
            # 纯DP回复技能，无伤害输出。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (信仰传承)：停止攻击，持续时间内回复总共20点部署费用；将军旗掷向范围内生命比例最低的干员所在位置，使其防御力+50%且每秒恢复相当于琴柳攻击力50%的生命值。技能结束时收回军旗。
            # 纯DP回复、治疗和防御增益技能，无伤害输出。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (光辉旗帜)：停止攻击，立即回复10点部署费用，将军旗掷向地面敌人所在位置，并对周围造成300%的物理伤害和3.5秒晕眩；期间军旗周围8格敌人受到停顿和30%的脆弱效果。技能结束时收回军旗。
            # 技能包含一个瞬发物理伤害。
            # "停止攻击" 指的是在瞬发伤害后，技能持续期间不再进行普攻。
            # "脆弱效果" 的描述是“期间军旗周围8格敌人受到...脆弱效果”，这表明脆弱效果在瞬发伤害发生后才开始生效，因此瞬发伤害不享受脆弱加成。
            
            # 瞬发伤害计算
            burst_atk_value = self.final_base_atk * 3.0
            total_damage = calculate_physical_damage(burst_atk_value, enemy.current_def)
            
            # 根据规则，瞬发伤害技能的DPS计算方式为：总伤 / 实际攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果技能索引不匹配，调用基类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)