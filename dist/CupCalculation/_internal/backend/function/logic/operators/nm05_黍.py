from backend.function.logic.professions import Guardian
from backend.function.logic.formulas import calculate_physical_damage

class Nm05黍(Guardian):
    """
    干员：黍
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：百谷长青
        # "治疗干员时对其与周围四格地块进行播种施加如下效果：每秒恢复70生命、获得10%庇护"
        # 此天赋主要提供治疗和生存辅助，不直接增加黍自身的伤害输出，因此不在此处修改攻击力、攻速等属性。
        
        # 天赋 2：天有四时
        # "在场时，场上有三名不同职业干员时所有干员生命上限+12%、三名相同职业干员时所有干员攻击速度+12，
        # 编入队伍且编队中有四名【岁】干员时所有干员攻击力+12%且4秒获得1点技力"
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，并按最大层数叠加。
        # 假设条件满足以获得最大伤害增益：
        
        # 攻击速度+12
        self.attack_speed += 12
        
        # 攻击力+12%
        self.final_base_atk *= (1 + 0.12)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 黍的普攻是物理伤害，天赋中没有特殊破甲或连击效果直接影响自身普攻伤害。
        # 直接使用最终基础攻击力计算物理伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (化被草木)：
            # "下一次攻击会为周围血量小于等于一半的一名友方单位恢复相当于攻击力180%的生命，可充能3次"
            # 此技能为纯治疗技能，不造成伤害。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (嘉禾盈仓)：
            # "停止攻击专注治疗范围内至多两名我方单位，攻击力+120%，阻挡数+1，第一天赋效果提升至1.5倍，治疗拥有特殊间隔"
            # 技能描述明确指出“停止攻击”，因此在此技能期间黍不造成伤害。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (离离枯荣)：
            # "治疗范围扩大，攻击同时可治疗我方干员，攻击力+50%，有地面敌人处于播种地块时技能范围内的我方单位攻击力+25%、攻击速度+25，敌人经过播种地块时获得如下效果：当远离该地块达到2格时被传送回该地块"
            # 这是一个增益类技能，持续30秒，期间黍会进行攻击。
            # "攻击力+50%"：直接提升黍的攻击力。
            # "有地面敌人处于播种地块时技能范围内的我方单位攻击力+25%、攻击速度+25"：此效果是给其他我方单位的，不影响黍自身的伤害计算。
            # 其他效果为控制或辅助，不直接影响伤害。
            
            skill_duration = 30 # 技能持续时间
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + 0.50) # 攻击力+50%
            
            # 计算单次强化普攻的伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的攻击次数
            # 假设技能期间的攻击间隔与普攻间隔相同，只是攻击力提升。
            num_attacks = skill_duration / actual_atk_interval
            
            total_damage = single_hit_damage * num_attacks
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
