from backend.function.logic.professions import MysticCaster
from backend.function.logic.formulas import calculate_arts_damage

class Ln05黑键(MysticCaster):
    """
    干员：黑键
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：强弱法
        # "储存的攻击能量造成的伤害提升至135%"
        self.talent1_stored_atk_multiplier = 1.35
        # "可额外储存1份只用于攻击精英或领袖敌人的攻击能量"
        # 秘术师基础可储存3份攻击能量，天赋额外增加1份，总计4份。
        self.max_stored_energy = 4 
        
        # 天赋 2：倚音
        # "若攻击目标周围没有其他敌人，攻击对其额外造成相当于攻击力15%的法术伤害"
        # 为计算最大伤害，假设此条件始终满足。
        self.talent2_bonus_ratio = 0.15
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次法术伤害命中时的期望伤害。
        黑键的所有伤害均为法术伤害。
        """
        return calculate_arts_damage(atk_val, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 黑键的普攻是发射所有储存的攻击能量。
        # 每个储存的能量都受到天赋1和天赋2的加成。
        # 最终伤害是所有能量的总和。
        
        # 计算单个储存能量的攻击力：基础攻击力 * 天赋1加成 * (1 + 天赋2额外伤害)
        atk_per_projectile = self.final_base_atk * self.talent1_stored_atk_multiplier * (1 + self.talent2_bonus_ratio)
        
        # 计算一次普攻爆发的总伤害：储存能量数 * 单个能量的伤害
        total_damage_burst = self.max_stored_energy * self._calc_arts_hit(atk_per_projectile, enemy)
        
        return total_damage_burst

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员当前的实际攻击间隔（受攻击速度影响）
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (渐快急板)：
            # 持续时间：5秒
            # 描述："攻击范围改变，攻击间隔0.17超大幅度缩短(*0.17)，每次攻击造成相当于攻击力50%的法术伤害"
            
            skill_duration = 5
            skill_atk_interval_multiplier = 0.17 # 攻击间隔缩短至0.17倍
            skill_atk_multiplier = 0.50 # 每次攻击造成50%攻击力伤害
            
            # 计算技能期间的实际攻击间隔
            # 技能描述为攻击间隔缩短，而非攻击速度增加，因此直接修改基础攻击间隔再计算实际间隔。
            skill_actual_atk_interval = (self.attack_interval * skill_atk_interval_multiplier) * 100 / self.attack_speed
            
            # 计算每次攻击的攻击力（受天赋2加成）
            atk_val_per_hit = self.final_base_atk * skill_atk_multiplier * (1 + self.talent2_bonus_ratio)
            
            # 计算技能持续期间的攻击次数
            num_hits = skill_duration / skill_actual_atk_interval
            
            # 计算总伤害：攻击次数 * 单次攻击伤害
            total_damage = num_hits * self._calc_arts_hit(atk_val_per_hit, enemy)
            
            # 计算技能期间的DPS：单次攻击伤害 / 技能期间实际攻击间隔
            dps = self._calc_arts_hit(atk_val_per_hit, enemy) / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (荒芜回响)：
            # 持续时间：null (瞬发伤害，召唤物造成伤害)
            # 描述："消耗所有攻击能量，在攻击范围内的可放置地块召唤消耗能量数+1个旧日残影（持续30秒），
            # 残影在敌人接近时激活，对周围的敌人造成攻击力245%的法术伤害并以中等力度拖拽敌人至自身中心"
            
            # 召唤的残影数量 = 消耗能量数 + 1 (消耗能量数即为最大储存能量数)
            num_echoes = self.max_stored_energy + 1
            
            # 计算每个残影造成的伤害（受天赋2加成，天赋1的“储存的攻击能量”加成不适用于残影伤害）
            atk_val_per_echo = self.final_base_atk * 2.45 * (1 + self.talent2_bonus_ratio)
            
            # 计算总伤害：残影数量 * 单个残影伤害
            total_damage = num_echoes * self._calc_arts_hit(atk_val_per_echo, enemy)
            
            # 瞬发伤害技能的DPS计算方式：总伤害 / 干员的常规攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (寂静之声)：
            # 持续时间：30秒
            # 描述："攻击速度+80，攻击力+65%，只以精英或领袖敌人为攻击目标，
            # 第一天赋的伤害加成提升至原本的140%可主动关闭技能（期间可随时停止技能）"
            
            skill_duration = 30
            atk_speed_buff = 80 # 攻击速度+80
            atk_buff_ratio = 0.65 # 攻击力+65%
            talent1_override_ratio = 1.40 # 天赋1加成提升至原本的140%
            
            # 计算技能期间的实际攻击速度和攻击间隔
            modified_atk_speed = self.attack_speed + atk_speed_buff
            modified_actual_atk_interval = self.attack_interval * 100 / modified_atk_speed
            
            # 计算强化后的基础攻击力
            enhanced_base_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能期间的天赋1乘数 (原本1.35 * 1.40)
            skill3_talent1_multiplier = self.talent1_stored_atk_multiplier * talent1_override_ratio
            
            # 计算每个储存能量的攻击力（受强化攻击力、技能期间天赋1乘数、天赋2加成）
            atk_per_projectile_skill3 = enhanced_base_atk * skill3_talent1_multiplier * (1 + self.talent2_bonus_ratio)
            
            # 计算单次爆发的总伤害（发射所有储存能量）
            damage_per_burst_skill3 = self.max_stored_energy * self._calc_arts_hit(atk_per_projectile_skill3, enemy)
            
            # 计算技能持续期间的爆发次数
            num_bursts = skill_duration / modified_actual_atk_interval
            
            # 计算总伤害：爆发次数 * 单次爆发伤害
            total_damage = num_bursts * damage_per_burst_skill3
            
            # 计算技能期间的DPS：单次爆发伤害 / 技能期间实际攻击间隔
            dps = damage_per_burst_skill3 / modified_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)