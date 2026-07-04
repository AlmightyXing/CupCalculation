from backend.function.logic.professions import SplashCaster
from backend.function.logic.formulas import calculate_arts_damage

class Nm02夕(SplashCaster):
    """
    干员：夕
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：化境
        # "夕与\"小自在\"击杀一名敌人时，夕获得2%攻击力，最多可叠加15层"
        # 按照最大层数计算，即 15 层 * 2% = 30% 攻击力提升
        self.final_base_atk *= (1 + 0.30)
        
        # 天赋 2：点睛
        # "部署后首次攻击敌人时，在目标位置（可部署地面）召唤一个\"小自在\"（持续25秒）"
        # 此天赋涉及召唤物，不直接影响夕自身的单次伤害计算，因此在此处不进行数值修改。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 夕是扩散术师，造成法术伤害。
        # 普攻无特殊机制，直接计算法术伤害。
        # SplashCaster父类没有覆写calculate_normal_hit，因此这里直接计算法术伤害是正确的。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1：工笔入化
            # "下一次攻击溅射范围扩大，造成相当于攻击力250%的法术伤害，可充能3次"
            # 这是一个瞬发型、单次高倍率的法术伤害。
            
            # 计算技能强化后的攻击力
            atk_val = self.final_base_atk * 2.50
            
            # 计算单次技能命中造成的总伤害
            total_damage = calculate_arts_damage(atk_val, enemy.current_res)
            
            # 瞬发技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2：泼墨淋漓
            # "攻击范围扩大，攻击力+55%，攻击速度+55，攻击范围内的所有敌人且对生命值低于一半的敌人造成的法术伤害提升至130%"
            # 持续时间：20秒
            
            duration = 20
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + 0.55)
            
            # 计算技能期间的强化攻击速度
            enhanced_attack_speed = self.attack_speed + 55
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 计算单次普攻伤害，考虑对生命值低于一半的敌人伤害提升130%
            # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑”，此处假设敌人生命值低于一半。
            single_hit_dmg = calculate_arts_damage(enhanced_atk, enemy.current_res) * 1.30
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = duration / skill_actual_atk_interval
            
            # 计算技能期间的总伤害
            total_damage = num_hits * single_hit_dmg
            
            # 计算技能期间的DPS
            dps = single_hit_dmg / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3：写意胜形
            # "攻击间隔增大(+40%)，优先攻击未阻挡的敌人，攻击范围与溅射范围扩大，攻击力+120%，每次攻击时在目标位置（可部署地面）召唤/刷新一个\"小自在\"（持续25秒）"
            # 持续时间：60秒
            
            duration = 60
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + 1.20)
            
            # 攻击间隔增大(+40%)，直接修改基础攻击间隔
            modified_base_attack_interval = self.attack_interval * (1 + 0.40)
            
            # 计算技能期间的实际攻击间隔（注意此技能不修改攻击速度，只修改攻击间隔）
            skill_actual_atk_interval = modified_base_attack_interval * 100 / self.attack_speed
            
            # 计算单次普攻伤害
            single_hit_dmg = calculate_arts_damage(enhanced_atk, enemy.current_res)
            
            # 召唤/刷新"小自在"不直接影响夕自身的单次伤害，此处忽略。
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = duration / skill_actual_atk_interval
            
            # 计算技能期间的总伤害
            total_damage = num_hits * single_hit_dmg
            
            # 计算技能期间的DPS
            dps = single_hit_dmg / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
