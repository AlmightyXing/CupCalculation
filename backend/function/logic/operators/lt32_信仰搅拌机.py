from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_physical_damage

class Lt32信仰搅拌机(UnknownProfession):
    """
    干员：信仰搅拌机
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：扫射迎宾仪礼 (每次造成伤害使自身10秒内防御力+30，攻击速度+3，最多可叠加3层)
        # 根据规则，只考虑对提高伤害有帮助的天赋。
        # 自身防御力+30是生存属性，不直接影响对敌伤害，因此不纳入伤害计算。
        # 攻击速度+3，最多可叠加3层，即攻击速度+9。这会影响DPS，因此需要计算。
        self.attack_speed += 3 * 3 # 最大叠加3层
        
        # 天赋 2：架盾送客仪礼 (若8秒内未主动攻击，获得相当于生命上限15%的屏障，失去屏障后重新计时)
        # 该天赋提供生存能力（屏障），不直接增加伤害，因此不纳入伤害计算。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 信仰搅拌机的普攻是物理伤害，没有特殊机制（如无视防御、法术伤害等）
        # 哨戒铁卫可以进行远程攻击，但伤害计算方式与近战物理伤害相同
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (铳骑主考官)：下次攻击变为三连击，每次造成相当于190%攻击力的物理伤害
            # 这是一个瞬发技能，计算一次性爆发伤害。
            atk_val = self.final_base_atk * 1.90
            single_hit_damage = calculate_physical_damage(atk_val, enemy.current_def)
            total_damage = single_hit_damage * 3 # 三连击
            
            # 瞬发技能的DPS计算方式
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (八臂电锯侠)：攻击力+150%，防御力+130%，攻击装有50发弹药，打完后结束
            # 这是一个增益类技能，持续期间进行普攻。
            # 攻击力增益：1 + 1.50 = 2.50
            # 弹药数：50发，决定了技能期间的攻击次数。
            # 防御力增益和抵挡致命伤害是生存属性，不影响伤害计算。
            
            enhanced_atk = self.final_base_atk * 2.50
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能期间总伤害 = 单次强化普攻伤害 * 攻击次数 (弹药数)
            total_damage = single_hit_damage * 50
            
            # DPS = 单次强化普攻伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (退休前布道)：攻击力+220%，停止主动攻击敌人，受到攻击时立即向攻击范围内最多3个敌人进行1次反击，
            # 反击最小间隔为实际攻击间隔的10%；攻击装有30发弹药，打完后结束
            # 这是一个特殊的反击技能。
            # 攻击力增益：1 + 2.20 = 3.20
            # 弹药数：30发，决定了反击次数。
            # 生命上限、防御力增益、补弹、攻击范围扩大等不影响自身伤害计算。
            # 关键在于“停止主动攻击敌人”和“受到攻击时立即反击”，以及“反击最小间隔为实际攻击间隔的10%”。
            
            enhanced_atk = self.final_base_atk * 3.20
            single_counter_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能期间总伤害 = 单次强化反击伤害 * 反击次数 (弹药数)
            total_damage = single_counter_damage * 30
            
            # DPS = 单次强化反击伤害 / 反击的实际攻击间隔
            # 反击最小间隔为实际攻击间隔的10%
            counter_atk_interval = actual_atk_interval * 0.10
            dps = single_counter_damage / counter_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)