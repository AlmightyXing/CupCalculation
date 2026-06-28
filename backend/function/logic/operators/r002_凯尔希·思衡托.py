from backend.function.logic.professions import Watcher
from backend.function.logic.formulas import calculate_physical_damage, calculate_true_damage

class R002凯尔希_思衡托(Watcher):
    """
    干员：凯尔希·思衡托
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        # super().__init__ 已经初始化了 self.final_base_atk = self.base_atk
        # 这里将信赖攻击力加到其上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk += self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：遗尘守望 (生命上限和防御力+25%，阻挡数+1，阻挡范围扩大(0.23倍)，部署后生命修复单元升空，自身起飞)
        # 此天赋主要影响干员的生存能力和部署机制，不直接影响凯尔希自身的伤害输出，故在伤害计算中不体现。
        # 如果需要体现，会修改 self.base_hp 和 self.base_def，但与伤害计算无关。

        # 天赋 2：医者丰碑 (其他友方干员进入自身攻击范围时立刻获得1层护盾并额外获得一次每秒回复50点生命值的增益治疗，持续30秒（不可叠加），增益治疗对【罗德岛】干员的效果翻倍)
        # 此天赋为辅助治疗效果，不影响凯尔希自身的伤害输出，故在伤害计算中不体现。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 凯尔希作为医疗干员，普攻为治疗，不造成伤害。
        # 在DPS模拟中，普攻伤害计为0。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        # Watcher 职业的 attack_interval 默认为 2.85
        
        if skill_index == 0:
            # 技能 1 (应急肃正防线)：攻击力+90%，攻击速度+50，持续35秒
            duration = 35
            atk_buff_ratio = 0.90 # 攻击力+90%
            aspd_bonus = 50 # 攻击速度+50
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            # 计算强化后的攻击速度
            enhanced_aspd = self.attack_speed + aspd_bonus
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / enhanced_aspd
            
            # 计算单次普攻伤害（物理伤害）
            # 假设此技能使凯尔希的攻击变为物理伤害
            single_hit_dmg = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的攻击次数
            num_hits = duration / skill_actual_atk_interval
            
            # 总伤害为攻击次数乘以单次伤害
            total_damage = num_hits * single_hit_dmg
            # DPS为单次伤害除以实际攻击间隔
            dps = single_hit_dmg / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (保护性拒止)：攻击力+150%，攻击变为射出医疗单元，对目标周围所有敌人造成相当于攻击力380%的真实伤害，攻击装有10发弹药，持续35秒
            duration = 35
            atk_buff_ratio = 1.50 # 攻击力+150%
            damage_ratio_per_hit = 3.80 # 380%攻击力的真实伤害
            num_shots = 10 # 攻击装有10发弹药
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算单次射击的真实伤害
            # 真实伤害不考虑防御力
            single_shot_damage = calculate_true_damage(enhanced_atk * damage_ratio_per_hit)
            
            # 总伤害为10次射击的总和
            total_damage = single_shot_damage * num_shots
            
            # DPS为总伤害除以技能持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (破梏重生)：攻击力+150%，攻击间隔大幅缩小(-1.55)，持续35秒
            duration = 35
            atk_buff_ratio = 1.50 # 攻击力+150%
            attack_interval_reduction = 1.55 # 攻击间隔减少1.55秒
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能期间的实际攻击间隔
            # 攻击间隔缩小意味着新的攻击间隔 = 原始攻击间隔 - 减少量
            skill_attack_interval = self.attack_interval - attack_interval_reduction
            # 确保攻击间隔不为负或过小，设定一个最小值以避免除以零或负数
            if skill_attack_interval <= 0:
                skill_attack_interval = 0.1 # 设定一个合理的最小值
            
            # 实际攻击间隔 = (新的攻击间隔) * 100 / 攻击速度
            skill_actual_atk_interval = skill_attack_interval * 100 / self.attack_speed
            
            # 计算单次普攻伤害（物理伤害）
            # 假设此技能使凯尔希的攻击变为物理伤害
            single_hit_dmg = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的攻击次数
            num_hits = duration / skill_actual_atk_interval
            
            # 总伤害为攻击次数乘以单次伤害
            total_damage = num_hits * single_hit_dmg
            # DPS为单次伤害除以实际攻击间隔
            dps = single_hit_dmg / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
