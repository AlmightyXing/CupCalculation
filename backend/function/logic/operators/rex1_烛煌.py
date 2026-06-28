from backend.function.logic.professions import PrimalCaster
from backend.function.logic.formulas import calculate_arts_damage

class Rex1烛煌(PrimalCaster):
    """
    干员：烛煌
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：熔点引爆
        # 这是一个触发式天赋，提供爆发伤害和临时抗性降低。
        # 根据规则，apply_talents用于修改干员的常驻属性。
        # 爆发伤害和临时抗性降低不属于常驻属性，因此不在此处直接应用。
        # 如果需要计算其贡献，应在技能或更复杂的模拟中考虑。
        
        # 天赋 2：绝处重燃
        # 这是一个生存天赋，不影响伤害输出，因此不在此处应用。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望伤害（法术伤害）
        烛煌作为本源术师，普攻造成法术伤害。
        """
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        # 注意：技能可能会修改攻击间隔，因此这里先获取基础值，技能内部再根据情况调整
        # self.attack_interval 是基础攻击间隔 (atk_time)，self.attack_speed 是攻速百分比 (默认为100)
        # PrimalCaster的attack_interval为1.6
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (炙手之援)：
            # "立即选择攻击范围内生命上限最高的一名干员，每秒对其周围所有敌人造成相当于攻击力70%的法术伤害和相当于法术伤害30%的灼燃损伤，持续20秒"
            # 这是一个持续伤害技能，伤害来源于友方干员周围，但伤害值由烛煌攻击力决定。
            # 灼燃损伤是元素损伤积累，不计入直接伤害。
            
            duration = 20 # 秒
            atk_multiplier = 0.70
            
            # 每秒造成的法术伤害
            damage_per_second = calculate_arts_damage(self.final_base_atk * atk_multiplier, enemy.current_res)
            
            total_damage = damage_per_second * duration
            dps = damage_per_second
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (沸血燎原)：
            # "攻击范围改变，攻击间隔增大(+0.9)，攻击力+150%，同时攻击3名敌人；
            # 攻击时流失5%的生命并在目标所在位置留下灼烧地段：
            # 经过的敌人移动速度-50%，每秒受到烛煌攻击力35%的法术伤害和相当于法术伤害30%的灼燃损伤"
            
            duration = 35 # 秒
            
            # 技能期间攻击力加成
            skill_atk_val = self.final_base_atk * (1 + 1.50)
            
            # 技能期间攻击间隔变化
            # 攻击间隔增大(+0.9)，所以是 self.attack_interval + 0.9
            skill_attack_interval_modifier = 0.9
            modified_attack_interval = (self.attack_interval + skill_attack_interval_modifier) * 100 / self.attack_speed
            
            # 计算普攻部分伤害
            single_hit_damage = calculate_arts_damage(skill_atk_val, enemy.current_res)
            num_hits = duration / modified_attack_interval
            direct_attack_total_damage = num_hits * single_hit_damage
            
            # 计算灼烧地段的持续伤害（DoT）
            # "每秒受到烛煌攻击力35%的法术伤害"
            dot_atk_multiplier = 0.35
            dot_damage_per_second = calculate_arts_damage(self.final_base_atk * dot_atk_multiplier, enemy.current_res)
            dot_total_damage = dot_damage_per_second * duration
            
            total_damage = direct_attack_total_damage + dot_total_damage
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (众恶的焚场)：
            # "攻击范围改变，攻击力+115%，攻击间隔大幅缩短(-1.3)，攻击变为群体攻击；
            # 若目标处于灼燃损伤爆发期间则额外造成攻击力80%的元素伤害。
            # 自身每秒流失最大生命的3%，攻击装有25发弹药，全场有敌人进入灼燃损伤爆发时获得2颗额外弹药，弹药打完后结束（可随时停止技能）"
            
            # 永续技能 (duration=null)，total_damage为0，重点计算dps
            total_damage = 0
            
            # 技能期间攻击力加成
            skill_atk_val = self.final_base_atk * (1 + 1.15)
            
            # 技能期间攻击间隔变化
            # 攻击间隔大幅缩短(-1.3)，所以是 self.attack_interval - 1.3
            skill_attack_interval_modifier = -1.3
            modified_attack_interval = (self.attack_interval + skill_attack_interval_modifier) * 100 / self.attack_speed
            
            # 计算普攻部分的法术伤害
            arts_hit_damage = calculate_arts_damage(skill_atk_val, enemy.current_res)
            
            # 计算额外元素伤害
            # "若目标处于灼燃损伤爆发期间则额外造成攻击力80%的元素伤害"
            # 假设条件满足，元素伤害通常无视抗性，直接按攻击力倍率计算
            elemental_bonus_damage = self.final_base_atk * 0.80
            
            # 单次攻击的总伤害 (法术伤害 + 元素伤害)
            single_hit_total_damage = arts_hit_damage + elemental_bonus_damage
            
            # 计算DPS
            dps = single_hit_total_damage / modified_attack_interval
            
            # 弹药系统和生命流失不影响单次攻击的期望伤害和DPS计算，
            # 它们更多影响技能的实际持续时间和生存能力，超出当前计算范围。
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
