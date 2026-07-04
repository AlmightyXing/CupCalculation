from backend.function.logic.professions import Reaper
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class R169隐德来希(Reaper):
    """
    干员：隐德来希
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：萃血 (每次攻击敌人时偷取目标75点生命上限（最高1350）并使目标每秒受到200点法术伤害持续5秒)
        # 伤害计算只考虑法术伤害部分
        self.talent_1_dot_duration = 5  # 秒
        self.talent_1_dot_damage_per_sec = 200  # 每秒法术伤害
        # 单次攻击触发的天赋1总法术伤害
        self.talent_1_total_arts_damage_per_hit = self.talent_1_dot_duration * self.talent_1_dot_damage_per_sec
        
        # 天赋 2：重盈 (生命值低于25%时，仅一次立刻回复50%最大生命值，且自身之后受到的物理伤害降低10%)
        # 该天赋为生存向，不影响伤害输出，故不在此处体现。
        
    def _calc_single_hit_damage(self, atk_val: float, enemy, include_talent_1_dot: bool = True) -> float:
        """
        计算单次命中时的期望伤害，包含物理伤害和天赋1的法术持续伤害。
        """
        # 干员自身攻击为物理伤害
        physical_dmg = calculate_physical_damage(atk_val, enemy.current_def)
        
        total_damage = physical_dmg
        
        # 如果需要包含天赋1的法术伤害
        if include_talent_1_dot:
            arts_dmg_from_talent = calculate_arts_damage(self.talent_1_total_arts_damage_per_hit, enemy.current_res)
            total_damage += arts_dmg_from_talent
            
        return total_damage

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻造成群体伤害，但根据规则，严禁在代码中乘以任何目标数。
        # 普攻触发天赋1的法术伤害。
        return self._calc_single_hit_damage(self.final_base_atk, enemy, include_talent_1_dot=True)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (玫影觅迹)：下次攻击的攻击力提升至175%，并连续攻击两次
            # 瞬发技能，替换一次普攻动画，但造成两次伤害。
            
            # 强化后的攻击力
            enhanced_atk_val = self.final_base_atk * 1.75
            
            # 单次强化攻击的伤害 (包含天赋1的法术伤害)
            single_hit_dmg = self._calc_single_hit_damage(enhanced_atk_val, enemy, include_talent_1_dot=True)
            
            # 连续攻击两次
            total_damage = single_hit_dmg * 2
            
            # DPS计算：总伤 / (替换的普攻间隔)
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (绯红壁合)：停止攻击，在自身及1名其他地面单位处召唤血镰，对周围所有敌人进行切割，每0.5秒造成相当于攻击力195%的物理伤害
            # 持续时间：12秒
            # 注意：血镰的攻击不触发干员自身的天赋1 (萃血)，因为是召唤物攻击。
            # 规则：严禁在代码中乘以任何目标数，即使描述为“在自身及1名其他地面单位处召唤血镰”。
            
            duration = 12
            
            # 血镰每次切割的攻击力
            scythe_atk_val = self.final_base_atk * 1.95
            
            # 血镰每次切割的物理伤害
            single_scythe_hit_physical_dmg = calculate_physical_damage(scythe_atk_val, enemy.current_def)
            
            # 每0.5秒切割一次，持续12秒
            num_hits = duration / 0.5
            
            total_damage = single_scythe_hit_physical_dmg * num_hits
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (灵与欲的惜别)：攻击范围扩大，攻击力+135%，攻击速度+100，立刻为攻击范围内最多3名生命值最高的地面敌人召唤对应的心烛，
            # 每次攻击对心烛至少造成35%攻击力的伤害，心烛继承原敌人当前60%的生命值，被攻击时原敌人也会受到一次无视闪避/护盾/屏障/格挡且伤害量不会改变的无来源真实伤害
            # 持续时间：20秒
            
            duration = 20
            
            # 技能期间的攻击力加成
            skill_atk_multiplier = 1 + 1.35  # +135%
            enhanced_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 技能期间的攻击速度加成
            skill_attack_speed_bonus = 100
            enhanced_attack_speed = self.attack_speed + skill_attack_speed_bonus
            
            # 技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 技能期间的攻击次数
            num_attacks = duration / skill_actual_atk_interval
            
            # 单次攻击的伤害构成：
            # 1. 干员自身的物理伤害 + 天赋1的法术伤害 (干员攻击触发天赋1)
            operator_hit_dmg = self._calc_single_hit_damage(enhanced_atk_val, enemy, include_talent_1_dot=True)
            
            # 2. 心烛触发的真实伤害
            # "每次攻击对心烛至少造成35%攻击力的伤害" -> 假设这个是真实伤害的量
            heart_candle_true_damage_per_hit = enhanced_atk_val * 0.35
            
            # 单次攻击的总伤害 (干员自身伤害 + 心烛真实伤害)
            total_damage_per_hit = operator_hit_dmg + heart_candle_true_damage_per_hit
            
            total_damage = total_damage_per_hit * num_attacks
            dps = total_damage_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
