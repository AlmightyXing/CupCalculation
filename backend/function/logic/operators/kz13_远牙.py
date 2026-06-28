from backend.function.logic.professions import Deadeye
from backend.function.logic.formulas import calculate_physical_damage

class Kz13远牙(Deadeye):
    """
    干员：远牙
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：凝神 (最近10秒内未受伤害时，攻击力+15%)
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，并按最大层数/条件满足计算。
        # 假设条件满足，直接加成到最终基础攻击力。
        self.final_base_atk *= (1 + 0.15)
        
        # 天赋 2：屏息 (技能开启时，嘲讽等级(-1)，且攻击无视目标的物理闪避)
        # 标记此特性。由于 calculate_physical_damage 函数不包含闪避参数，
        # 此天赋意味着我们假设攻击不会被闪避，这通常是默认行为，因此无需额外代码修改 calculate_physical_damage 的调用。
        self.ignore_physical_evasion = True 
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻伤害，self.final_base_atk 已包含凝神天赋加成
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算干员自身面板的实际攻击间隔
        # 注意：这里的 actual_atk_interval 是基于干员自身面板（可能含天赋AS加成，但远牙天赋无常驻AS加成）
        # 技能若有额外AS加成，需在技能内部重新计算 skill_actual_atk_interval
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (迅捷打击·γ型)：攻击力+45%，攻击速度+45，持续35秒
            duration = 35
            
            # 计算技能期间的攻击力
            skill_atk_multiplier = 1 + 0.45
            boosted_atk = self.final_base_atk * skill_atk_multiplier
            
            # 计算技能期间的攻击速度和实际攻击间隔
            boosted_attack_speed = self.attack_speed + 45
            skill_actual_atk_interval = self.attack_interval * 100 / boosted_attack_speed
            
            # 计算技能期间的普攻次数
            hits = duration / skill_actual_atk_interval
            
            # 计算单次普攻伤害
            single_hit_damage = calculate_physical_damage(boosted_atk, enemy.current_def)
            
            # 计算总伤害和DPS
            total_damage = hits * single_hit_damage
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (同盟支援)：可以攻击到范围外被阻挡的敌方单位，攻击速度+110，持续35秒
            duration = 35
            
            # 攻击力无额外加成，使用干员最终基础攻击力 (已含凝神天赋)
            boosted_atk = self.final_base_atk
            
            # 计算技能期间的攻击速度和实际攻击间隔
            boosted_attack_speed = self.attack_speed + 110
            skill_actual_atk_interval = self.attack_interval * 100 / boosted_attack_speed
            
            # 计算技能期间的普攻次数
            hits = duration / skill_actual_atk_interval
            
            # 计算单次普攻伤害
            single_hit_damage = calculate_physical_damage(boosted_atk, enemy.current_def)
            
            # 计算总伤害和DPS
            total_damage = hits * single_hit_damage
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (光羽箭)：攻击范围改为前方无限长的直线，攻击力+140%，
            # 攻击原本范围以外的目标时，造成的伤害提高至140%，持续20秒
            duration = 20
            
            # 计算技能期间的攻击力
            # 攻击力加成：1 + 1.40 = 2.40
            # 攻击原本范围以外的目标时，造成的伤害提高至140% (即最终伤害乘1.4)
            # 根据规则，将所有伤害提升效果都体现在攻击力上，并假设条件满足以计算最大伤害。
            skill_atk_multiplier = (1 + 1.40) * 1.40 # 最终攻击力 = (基础攻击力 * 2.4) * 1.4
            final_hit_atk_value = self.final_base_atk * skill_atk_multiplier
            
            # 攻击速度无额外加成，使用干员自身面板的实际攻击间隔
            # (self.attack_speed 在 apply_talents 中未被修改，所以这里用 actual_atk_interval 即可)
            
            # 计算技能期间的普攻次数
            hits = duration / actual_atk_interval
            
            # 计算单次普攻伤害
            single_hit_damage = calculate_physical_damage(final_hit_atk_value, enemy.current_def)
            
            # 计算总伤害和DPS
            total_damage = hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)