from backend.function.logic.professions import Flinger
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class B00w维什戴尔(Flinger):
    """
    干员：维什戴尔
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 维什戴尔的职业特性：攻击对小范围的地面敌人造成两次物理伤害
        # (第一次为主攻击，第二次为余震，伤害降低至攻击力的一半)
        # Flinger父类已实现此特性，但维什戴尔有天赋加成，因此在calculate_normal_hit中重新实现并考虑天赋
        self.main_hit_multiplier = 1.0
        self.aftershock_multiplier = 0.5
        
        # 天赋默认值，将在apply_talents中修改
        self.talent1_main_target_atk_multiplier = 1.0 # 天赋1：对主目标的攻击力提升比例
        self.talent1_explosion_prob = 0.0 # 天赋1：残影爆炸概率
        self.talent1_explosion_multiplier = 0.0 # 天赋1：残影爆炸伤害倍率
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：好礼
        # 攻击时对主目标的攻击力提升至115%
        self.talent1_main_target_atk_multiplier = 1.15
        # 残影受到维什戴尔的余震影响时有15%概率爆炸，对周围所有敌人造成150%攻击力的物理伤害
        self.talent1_explosion_prob = 0.15
        self.talent1_explosion_multiplier = 1.5
        
        # 天赋 2：死魂灵的余息
        # 部署完成后立刻在攻击范围内召唤一个魂灵之影，在魂灵之影周围时获得迷彩
        # 此天赋不直接影响伤害计算，故不在此处体现数值修改
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害
        维什戴尔没有特殊的无视防御或法术伤害机制，直接使用物理伤害公式
        """
        return calculate_physical_damage(atk_val, enemy.current_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 维什戴尔对主目标的有效攻击力 (考虑天赋1的115%加成)
        # 任何基于“攻击力”的伤害倍率都应基于此有效攻击力
        effective_atk_for_main_target = self.final_base_atk * self.talent1_main_target_atk_multiplier
        
        # 普攻基础伤害 (主攻击 + 余震)
        # Flinger父类特性：攻击对小范围的地面敌人造成两次物理伤害（第二次为余震，伤害降低至攻击力的一半）
        main_hit_damage = self._calc_hit(effective_atk_for_main_target * self.main_hit_multiplier, enemy)
        aftershock_damage = self._calc_hit(effective_atk_for_main_target * self.aftershock_multiplier, enemy)
        
        total_damage = main_hit_damage + aftershock_damage
        
        # 天赋1：残影爆炸伤害 (15%概率，150%攻击力)
        # 爆炸伤害也应基于对主目标的有效攻击力
        explosion_atk_val = effective_atk_for_main_target * self.talent1_explosion_multiplier
        expected_explosion_damage = self.talent1_explosion_prob * self._calc_hit(explosion_atk_val, enemy)
        
        total_damage += expected_explosion_damage
        
        return total_damage

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔，考虑干员自身攻速加成 (如天赋)
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (定点清算)：下次攻击额外造成2次余震并使所有目标晕眩1.5秒，
            # 此次攻击的溅射范围略微扩大且余震伤害变为攻击力的120%
            # 这是一个单次攻击的强化技能，总伤即为这次强化攻击的伤害
            
            # 维什戴尔对主目标的有效攻击力 (考虑天赋1的115%加成)
            effective_atk_for_main_target = self.final_base_atk * self.talent1_main_target_atk_multiplier
            
            # 主攻击伤害 (倍率不变，继承Flinger的1.0倍)
            main_hit_damage = self._calc_hit(effective_atk_for_main_target * self.main_hit_multiplier, enemy)
            
            # 余震伤害：1 (基础) + 2 (额外) = 3次余震，每次120%攻击力
            aftershock_multiplier_skill1 = 1.2
            aftershock_damage_per_hit = self._calc_hit(effective_atk_for_main_target * aftershock_multiplier_skill1, enemy)
            total_aftershock_damage = aftershock_damage_per_hit * 3
            
            # 天赋1：残影爆炸伤害 (15%概率，150%攻击力)
            # 假设一次攻击只触发一次爆炸判定
            explosion_atk_val = effective_atk_for_main_target * self.talent1_explosion_multiplier
            expected_explosion_damage = self.talent1_explosion_prob * self._calc_hit(explosion_atk_val, enemy)
            
            total_damage = main_hit_damage + total_aftershock_damage + expected_explosion_damage
            
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (饱和复仇)：攻击力+35%，攻击间隔缩短(-0.7)，可同时攻击3名敌人；
            # 过载：攻击改为攻击力80%的4连发，随机攻击范围内的目标；该技能可随时主动关闭
            # 持续时间：25秒
            duration = 25
            
            # 攻击力加成
            skill_atk_multiplier = 1.0 + 0.35
            
            # 攻击间隔缩短
            modified_attack_interval_base = self.attack_interval - 0.7
            # 确保攻击间隔不为负或过小，实际游戏中会有下限，这里简单设为0.1
            if modified_attack_interval_base <= 0.1:
                modified_attack_interval_base = 0.1
            
            # 计算技能期间的实际攻击间隔
            # self.attack_speed 已经包含了天赋等带来的攻速加成
            actual_atk_interval_skill2 = modified_attack_interval_base * 100 / self.attack_speed
            
            # 技能期间对主目标的有效攻击力
            # (最终基础攻击力 * 技能攻击力加成) * 天赋1对主目标的攻击力提升
            effective_atk_for_skill = self.final_base_atk * skill_atk_multiplier * self.talent1_main_target_atk_multiplier
            
            # 过载模式：4连发，每发80%攻击力
            # 此模式下不产生“余震”，因此不触发天赋1的爆炸
            single_hit_damage = self._calc_hit(effective_atk_for_skill * 0.8, enemy)
            damage_per_attack_cycle = single_hit_damage * 4
            
            # 计算技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval_skill2
            
            total_damage = num_attacks * damage_per_attack_cycle
            dps = damage_per_attack_cycle / actual_atk_interval_skill2
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (爆裂黎明)：立刻在攻击范围内召唤2个魂灵之影（最多存在3个，技能结束后保留），
            # 攻击力+180%，攻击间隔大幅增大(+2.9)，攻击时攻击力提升至220%，
            # 溅射范围大幅扩大且第一天赋的发动概率提高至100%；攻击装有6发弹药，打完后结束
            # 弹药技能，总伤为6发弹药的总和
            
            ammo_count = 6
            
            # 攻击力加成 (1+180% = 2.8倍)
            skill_atk_multiplier = 1.0 + 1.80
            
            # 攻击时攻击力提升至220% (额外乘区)
            attack_time_multiplier = 2.20
            
            # 攻击间隔增大
            modified_attack_interval_base = self.attack_interval + 2.9
            actual_atk_interval_skill3 = modified_attack_interval_base * 100 / self.attack_speed
            
            # 天赋1的发动概率提高至100%
            skill3_explosion_prob = 1.0
            
            # 技能期间对主目标的有效攻击力
            # (最终基础攻击力 * 技能攻击力加成 * 攻击时攻击力提升) * 天赋1对主目标的攻击力提升
            effective_atk_for_skill = (self.final_base_atk * skill_atk_multiplier * attack_time_multiplier) * self.talent1_main_target_atk_multiplier
            
            # 主攻击伤害 (继承Flinger的1.0倍)
            main_hit_damage_per_shot = self._calc_hit(effective_atk_for_skill * self.main_hit_multiplier, enemy)
            
            # 余震伤害 (继承Flinger的0.5倍)
            aftershock_damage_per_shot = self._calc_hit(effective_atk_for_skill * self.aftershock_multiplier, enemy)
            
            # 天赋1：残影爆炸伤害 (100%概率，150%攻击力)
            # 爆炸伤害也应基于技能期间的有效攻击力
            explosion_damage_per_shot = skill3_explosion_prob * self._calc_hit(effective_atk_for_skill * self.talent1_explosion_multiplier, enemy)
            
            # 单发弹药的总伤害
            damage_per_shot = main_hit_damage_per_shot + aftershock_damage_per_shot + explosion_damage_per_shot
            
            # 6发弹药的总伤害
            total_damage = damage_per_shot * ammo_count
            # 技能期间的DPS
            dps = damage_per_shot / actual_atk_interval_skill3
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
