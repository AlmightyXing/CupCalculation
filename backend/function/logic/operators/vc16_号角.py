from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Vc16号角(UnknownProfession):
    """
    干员：号角
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 应用天赋
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：军事要塞 (在场时所有重装干员的攻击力+20%)
        # 此天赋不直接影响号角自身的伤害，故不在此处体现。

        # 天赋 2：血战 (被击倒时不撤退，恢复所有生命且生命上限-50%，攻击速度+18、防御力+18%（单次部署只触发一次）)
        # 考虑其对伤害的增益部分，按最大收益计算。
        self.attack_speed += 18
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 号角普攻为远程群体物理攻击，但计算时只考虑对单个目标的伤害
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于DPS计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (照明榴弹)：下次攻击时造成280%攻击力的物理伤害
            # 这是一个瞬发伤害技能，替换一次普攻
            skill_atk_val = self.final_base_atk * 2.8
            total_damage = calculate_physical_damage(skill_atk_val, enemy.current_def)
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (暴风号令)：每次攻击造成240%攻击力的物理溅射伤害，过载：每次攻击额外造成60%攻击力的法术溅射伤害
            # 技能拥有10枚弹药，按最大收益（过载）计算
            
            # 单次攻击的物理伤害部分
            phys_atk_val = self.final_base_atk * 2.4
            dmg_phys_per_hit = calculate_physical_damage(phys_atk_val, enemy.current_def)
            
            # 单次攻击的法术伤害部分 (过载)
            arts_atk_val = self.final_base_atk * 0.6
            dmg_arts_per_hit = calculate_arts_damage(arts_atk_val, enemy.current_res)
            
            # 单次攻击的总伤害
            dmg_per_hit = dmg_phys_per_hit + dmg_arts_per_hit
            
            # 技能总伤害 (10枚弹药)
            total_damage = dmg_per_hit * 10
            
            # DPS为单次攻击伤害除以实际攻击间隔
            return {"total_damage": total_damage, "dps": dmg_per_hit / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (终极防线)：攻击力+70%，攻击间隔大幅缩短(-1.8)，过载：攻击力改为+140%，持续24秒
            # 按最大收益（过载）计算
            duration = 24
            
            # 攻击力增益
            skill_atk_multiplier = 1 + 1.40 # 过载状态下攻击力+140%
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 攻击间隔缩短
            # 注意：self.attack_interval 是基础攻击间隔，self.attack_speed 影响最终实际间隔
            base_skill_attack_interval = self.attack_interval - 1.8
            if base_skill_attack_interval <= 0: # 避免攻击间隔为负或零
                base_skill_attack_interval = 0.1 # 设定一个极小值
            
            actual_skill_atk_interval = base_skill_attack_interval * 100 / self.attack_speed
            
            # 单次强化普攻的伤害
            dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能持续期间的攻击次数
            num_hits = duration / actual_skill_atk_interval
            
            # 技能总伤害
            total_damage = dmg_per_hit * num_hits
            
            # 技能期间的DPS
            dps = dmg_per_hit / actual_skill_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)