from backend.function.logic.professions import Pioneer
from backend.function.logic.formulas import calculate_physical_damage

class Gg01推进之王(Pioneer):
    """
    干员：推进之王
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：万兽之王 (在场时，所有【先锋】职业干员的攻击力和防御力各+8%)
        # 此天赋对推进之王自身也生效，提高其攻击力。防御力提升不直接影响伤害计算，故忽略。
        self.final_base_atk *= (1 + 0.08)
        
        # 天赋 2：粉碎 (周围四格内有敌人倒下时获得1点技力)
        # 此天赋影响技力回复，不直接影响伤害或面板属性，故在伤害计算中忽略。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 推进之王没有特殊的普攻机制（如无视防御、法术伤害等），直接调用父类计算物理伤害
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算实际攻击间隔，用于DPS计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (冲锋号令·γ型)：立即获得12点部署费用
            # 此技能为费用回复技能，不造成任何伤害。
            # 根据规则，无伤害技能 total_damage 和 dps 均为 0。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (跃空锤)：下次攻击对四周所有敌人造成相当于攻击力340%的物理伤害，并获得3点部署费用，可充能3次
            # 这是一个瞬发伤害技能，只计算单次爆发伤害。
            # 攻击力倍率为340%
            atk_val = self.final_base_atk * 3.40
            
            # 计算单次爆发的物理伤害
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发技能的DPS计算方式：总伤 / 实际攻击间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (碎颅击)：持续25秒。攻击间隔1.0增大(+1.0)，攻击时攻击力提高至380%，并且有40%的概率晕眩目标1.5秒
            duration = 25.0
            
            # 技能期间攻击间隔增大1.0，所以新的基础攻击间隔为 self.attack_interval + 1.0
            # 重新计算技能期间的实际攻击间隔
            skill_atk_interval = (self.attack_interval + 1.0) * 100 / self.attack_speed
            
            # 攻击力提高至380%
            enhanced_atk = self.final_base_atk * 3.80
            
            # 计算单次强化普攻的伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = duration / skill_atk_interval
            
            # 技能总伤害为单次强化普攻伤害乘以攻击次数
            total_damage = single_hit_damage * num_hits
            
            # 技能期间的DPS为单次强化普攻伤害除以技能期间的实际攻击间隔
            dps = single_hit_damage / skill_atk_interval
            
            # 眩晕效果不影响伤害计算，故忽略
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
