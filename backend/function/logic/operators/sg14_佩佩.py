from backend.function.logic.professions import Earthshaker
from backend.function.logic.formulas import calculate_physical_damage

class Sg14佩佩(Earthshaker):
    """
    干员：佩佩
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：往昔传承 (不影响伤害，忽略)
        # "技能期间每击倒1名敌人，技能结束时获得1点技力，至多回复14点"
        
        # 天赋 2：弥漫莲香 (在场时，所有【近卫】干员的攻击力+16%)
        # 佩佩是【近卫】干员，此天赋对其自身生效
        self.final_base_atk *= (1 + 0.16)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 撼地者特性：攻击使目标周围的其他敌人受到相当于攻击力50%的群体物理伤害
        # 根据规则，最终的 total_damage 和 dps 必须严格是对单个目标造成的伤害。
        # 因此，只计算对主目标的伤害，不计算溅射伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (盖戳！): 下次攻击造成相当于攻击力290%的物理伤害
            # 瞬发伤害技能
            atk_val = self.final_base_atk * 2.90
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (阻遏混乱锤): 持续18秒
            # 攻击范围扩大，攻击力+90%，攻击速度+80
            # 每次使用时，使后续开启技能的攻击速度额外+40，最多叠加2层 (按最大层数计算)
            
            duration = 18
            atk_multiplier = 1 + 0.90 # 攻击力+90%
            
            # 攻击速度加成：基础+80，叠加2层额外+40，总计 80 + (2 * 40) = 160
            atk_speed_bonus = 80 + (2 * 40) 
            effective_atk_speed = self.attack_speed + atk_speed_bonus
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / effective_atk_speed
            
            # 计算强化后的单次普攻伤害
            enhanced_atk = self.final_base_atk * atk_multiplier
            single_hit_dmg = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的总伤害
            num_hits = duration / skill_actual_atk_interval
            total_damage = num_hits * single_hit_dmg
            
            # DPS为强化后的单次普攻伤害除以技能期间的实际攻击间隔
            return {"total_damage": total_damage, "dps": single_hit_dmg / skill_actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (时光震荡): 持续40秒
            # 攻击间隔略微增大(+0.2)，攻击力+240%
            # 每次攻击后使溅射范围扩大且攻击力额外+25%，最多叠加4层 (按最大层数计算)
            
            duration = 40
            
            # 攻击间隔增大
            effective_base_atk_interval = self.attack_interval + 0.2
            
            # 攻击力加成：基础+240%，叠加4层额外+25%，总计 (1 + 2.40) + (4 * 0.25) = 3.40 + 1.00 = 4.40
            atk_multiplier = (1 + 2.40) + (4 * 0.25) 
            
            # 计算技能期间的实际攻击间隔 (在修改后的基础间隔上应用攻速)
            skill_actual_atk_interval = effective_base_atk_interval * 100 / self.attack_speed
            
            # 计算强化后的单次普攻伤害
            enhanced_atk = self.final_base_atk * atk_multiplier
            single_hit_dmg = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的总伤害
            num_hits = duration / skill_actual_atk_interval
            total_damage = num_hits * single_hit_dmg
            
            # DPS为强化后的单次普攻伤害除以技能期间的实际攻击间隔
            return {"total_damage": total_damage, "dps": single_hit_dmg / skill_actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
