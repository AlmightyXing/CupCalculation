from backend.function.logic.professions import Crusher
from backend.function.logic.formulas import calculate_physical_damage

class B216赫德雷(Crusher):
    """
    干员：赫德雷
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：及锋而试 (攻击敌人时攻击力提升至110%，若目标处于晕眩、束缚则改为提升至140%)
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，且按最大层数/效果叠加。
        # 因此，我们定义两种乘数，并在计算时根据情况选择或取期望。
        self.talent_1_normal_multiplier = 1.10
        self.talent_1_stun_multiplier = 1.40
        
        # 天赋 2：余火之氅 (使自身与身后一格的友军获得18%的庇护)
        # 该天赋提供庇护（防御性效果），不直接提高伤害输出，因此在伤害计算中忽略。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 根据规则，对于有条件触发的伤害提升天赋，在普攻计算中应考虑其最大伤害潜力。
        # 因此，假设目标处于晕眩/束缚状态，触发天赋1的140%攻击力提升。
        # 重剑手父类没有覆写 calculate_normal_hit，因此直接计算即可，无需 super()。
        atk_val = self.final_base_atk * self.talent_1_stun_multiplier
        return calculate_physical_damage(atk_val, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (重锋不熄)：下次攻击造成相当于攻击力260%的物理伤害，并回复自身25%的生命
            # 这是一个单次爆发伤害技能。
            # 伤害计算时，考虑天赋1的最大伤害潜力（140%攻击力）。
            # 重剑手父类没有覆写 calculate_skill_damage，因此直接计算即可，无需 super()。
            atk_val = self.final_base_atk * self.talent_1_stun_multiplier * 2.60
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 对于瞬发伤害技能，DPS = 总伤 / 实际攻击间隔 (假设其替代一次普攻)
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (余烬重荷)：
            # 被动效果：攻击力+40%；
            # 主动触发可以在下列状态和初始状态间切换：攻击间隔略微增大(+0.5)，阻挡数+1，攻击使目标晕眩1秒
            
            # 该技能持续时间为 null，属于永续技能。
            # 根据规则，永续技能的 total_damage 为 0，重点计算 DPS。
            
            # 1. 计算被动攻击力加成：
            base_atk_after_passive = self.final_base_atk * (1 + 0.40)
            
            # 2. 计算主动效果下的攻击力：
            # 主动效果使攻击必定晕眩目标，因此天赋1的140%攻击力提升必定触发。
            final_atk_val = base_atk_after_passive * self.talent_1_stun_multiplier
            
            # 3. 计算主动效果下的实际攻击间隔：
            # 攻击间隔略微增大 (+0.5)
            modified_atk_interval = (self.attack_interval + 0.5) * 100 / self.attack_speed
            
            # 4. 计算单次普攻伤害和 DPS：
            single_hit_damage = calculate_physical_damage(final_atk_val, enemy.current_def)
            dps = single_hit_damage / modified_atk_interval
            
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (死境硝烟)：
            # 持续时间 70秒。
            # 每秒流失100点生命 (防御性效果，忽略)。
            # 并使自身攻击过和攻击过自身的敌人每秒受到200点真实伤害。
            # 攻击距离+1 (忽略)。
            # 生命上限+60% (防御性效果，忽略)。
            # 攻击力+120%。
            # 每次攻击回复自身5%的生命 (防御性效果，忽略)。
            # 且有25%概率使目标晕眩5秒。
            
            skill_duration = 70
            
            # 1. 计算技能期间的攻击力：
            # 技能提供攻击力+120%
            base_atk_after_skill_buff = self.final_base_atk * (1 + 1.20)
            
            # 2. 计算天赋1的期望攻击力乘数：
            # 25%概率晕眩 (触发140%乘数)，75%概率不晕眩 (触发110%乘数)
            effective_talent_1_multiplier = (0.25 * self.talent_1_stun_multiplier) + \
                                            (0.75 * self.talent_1_normal_multiplier)
            
            final_atk_val = base_atk_after_skill_buff * effective_talent_1_multiplier
            
            # 3. 计算单次普攻的物理伤害：
            single_hit_physical_damage = calculate_physical_damage(final_atk_val, enemy.current_def)
            
            # 4. 计算技能持续期间的普攻次数：
            num_attacks = skill_duration / actual_atk_interval
            
            # 5. 计算普攻造成的总物理伤害：
            total_physical_damage = single_hit_physical_damage * num_attacks
            
            # 6. 计算技能附加的真实伤害：
            true_damage_per_second = 200
            total_true_damage = true_damage_per_second * skill_duration
            
            # 7. 计算总伤害和 DPS：
            total_damage = total_physical_damage + total_true_damage
            dps = total_damage / skill_duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
