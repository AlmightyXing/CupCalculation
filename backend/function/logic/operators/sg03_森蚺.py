from backend.function.logic.professions import Duelist # 假设“决战者”对应的职业类为 Duelist
from backend.function.logic.formulas import calculate_physical_damage

class Sg03森蚺(Duelist):
    """
    干员：森蚺
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关的属性
        self.talent_atk_multiplier = 1.0 # 默认天赋攻击力乘数
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：勇冠三军
        # "生命值高于一半时，攻击力造成115%伤害"
        # 对于伤害计算，我们假设处于最有利的条件，即生命值高于一半。
        # "生命值不高于一半时，获得20%的庇护" - 庇护是减伤效果，不影响输出，故不在此处计算。
        self.talent_atk_multiplier = 1.15
        
        # 天赋 2：愈战愈勇
        # "阻挡敌人时技力回复速度+0.2/秒"
        # 此天赋影响技力回复速度，不直接影响单次攻击伤害或技能持续期间的DPS，
        # 因此不在此处修改攻击力或攻击速度等面板属性。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 计算普攻伤害时，应用天赋的攻击力乘数
        atk_val = self.final_base_atk * self.talent_atk_multiplier
        return calculate_physical_damage(atk_val, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算基础实际攻击间隔（不受技能影响时）
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (轻型挂斧)：攻击力+25%，防御力+25%
            # 这是一个永续技能 (duration: null)，总伤害为0，主要关注DPS。
            
            # 计算技能期间的攻击力 (基础攻击力 * (1 + 技能增益) * 天赋增益)
            skill_atk_multiplier = 1.0 + 0.25
            buffed_atk = self.final_base_atk * skill_atk_multiplier * self.talent_atk_multiplier
            
            # 计算单次普攻伤害
            single_hit_damage = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            total_damage = 0.0 # 永续技能的总伤害为0
            dps = single_hit_damage / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (震慑劈砍)：攻击间隔略微增大(+0.4)，攻击力+180%，持续18秒
            duration = 18
            
            # 计算技能期间的实际攻击间隔
            skill_attack_interval = self.attack_interval + 0.4
            skill_actual_atk_interval = skill_attack_interval * 100 / self.attack_speed
            
            # 计算技能期间的攻击力 (基础攻击力 * (1 + 技能增益) * 天赋增益)
            skill_atk_multiplier = 1.0 + 1.80
            buffed_atk = self.final_base_atk * skill_atk_multiplier * self.talent_atk_multiplier
            
            # 计算单次普攻伤害
            single_hit_damage = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            # 计算技能持续期间的攻击次数
            num_hits = duration / skill_actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (钢铁意志)：攻击力+230%，防御力+160%，阻挡数+2，每秒恢复6%生命，持续35秒
            duration = 35
            
            # 计算技能期间的攻击力 (基础攻击力 * (1 + 技能增益) * 天赋增益)
            skill_atk_multiplier = 1.0 + 2.30
            buffed_atk = self.final_base_atk * skill_atk_multiplier * self.talent_atk_multiplier
            
            # 计算单次普攻伤害
            single_hit_damage = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            # 计算技能持续期间的攻击次数 (此技能未改变攻击间隔，使用基础攻击间隔)
            num_hits = duration / base_actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)