from backend.function.logic.professions import Defender
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Lm23斩业星熊(Defender):
    """
    干员：斩业星熊
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：业火 (生存天赋，不影响伤害计算)
        # 天赋 2：鬼之架势 (防御天赋，不影响伤害计算)
        # 根据规则，只有对提高伤害有帮助的天赋才纳入考虑。此干员的两个天赋均不直接提高伤害。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 斩业星熊的职业特性是“技能开启时普通攻击会造成法术伤害”，
        # 因此在技能未开启时，普攻为物理伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (恶业苦果)：永续技能 (duration: null)
            # 描述: 攻击力+70%，防御力+70%，每次受到攻击时对目标造成相当于斩业星熊攻击力175%的法术伤害
            # 职业特性: 技能开启时普通攻击会造成法术伤害
            
            atk_buff_ratio = 0.70
            skill_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 普攻变为法术伤害
            single_hit_damage = calculate_arts_damage(skill_atk, enemy.current_res)
            
            # 永续技能 total_damage 为 0
            # DPS 为强化后的普攻伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            # "每次受到攻击时对目标造成相当于斩业星熊攻击力175%的法术伤害" 是反击伤害，
            # 不计入干员主动输出的 total_damage 或 dps。
            
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (无始无明)：永续技能 (duration: null)
            # 描述: 投出盾牌并以攻击力90%的三连击攻击所有阻挡的敌人，盾牌会环绕斩业星熊飞行一圈；
            #       盾牌碰到敌人时使目标停顿，每0.5秒对其造成攻击力130%的法术伤害，自身回复盾牌造成伤害15%的生命
            # 职业特性: 技能开启时普通攻击会造成法术伤害
            
            # 主动攻击部分：攻击力90%的三连击
            skill_atk_multiplier_main = 0.90
            hits_per_attack_main = 3
            skill_atk_main = self.final_base_atk * skill_atk_multiplier_main
            
            single_hit_damage_main = calculate_arts_damage(skill_atk_main, enemy.current_res)
            damage_per_attack_cycle_main = single_hit_damage_main * hits_per_attack_main
            
            dps_main_attack = damage_per_attack_cycle_main / actual_atk_interval
            
            # 盾牌DoT部分：每0.5秒造成攻击力130%的法术伤害
            # 假设此DoT在技能持续期间持续生效
            skill_atk_multiplier_dot = 1.30
            dot_interval = 0.5 # seconds
            skill_atk_dot = self.final_base_atk * skill_atk_multiplier_dot
            
            dot_damage_per_tick = calculate_arts_damage(skill_atk_dot, enemy.current_res)
            dps_dot = dot_damage_per_tick / dot_interval
            
            total_dps = dps_main_attack + dps_dot
            
            return {"total_damage": 0, "dps": total_dps}
            
        elif skill_index == 2:
            # 技能 3 (地狱变相)：持续32秒 (duration: 32)
            # 描述: 攻击范围扩大，生命上限+100%，攻击力+230%，以二连击攻击最多3名敌人；
            #       主动关闭技能后11秒内保留技能加成且不会被击倒，攻击变为四连击，承担攻击范围内我方干员受到的致命伤害，11秒后强制退出战场
            # 职业特性: 技能开启时普通攻击会造成法术伤害
            
            duration = 32
            atk_buff_ratio = 2.30 # 攻击力+230%
            
            # 技能增益先触发，爆发伤害使用强化后的攻击力
            skill_atk = self.final_base_atk * (1 + atk_buff_ratio)
            hits_per_attack = 2 # 二连击
            
            # 普攻变为法术伤害
            single_hit_damage = calculate_arts_damage(skill_atk, enemy.current_res)
            
            damage_per_attack_cycle = single_hit_damage * hits_per_attack
            
            # 计算技能持续期间的攻击次数
            attacks_during_skill = duration / actual_atk_interval
            
            total_damage = damage_per_attack_cycle * attacks_during_skill
            dps = damage_per_attack_cycle / actual_atk_interval
            
            # "主动关闭技能后11秒内保留技能加成且不会被击倒，攻击变为四连击"
            # 这部分是技能结束后的特殊状态，不计入技能持续期间的 total_damage 和 dps。
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)