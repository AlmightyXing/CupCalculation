from backend.function.logic.professions import Lord
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Ii01棘刺(Lord):
    """
    干员：棘刺
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：神经腐蚀
        # 攻击使目标中毒，在3秒内每秒受到125点法术伤害（对会远程攻击的目标伤害加倍）
        self.talent_nerve_corrosion_base_dmg_per_sec = 125
        self.talent_nerve_corrosion_duration = 3
        self.talent_nerve_corrosion_ranged_multiplier = 2
        
        # 天赋 2：故土潮声
        # 如果2秒内没有主动攻击过，每秒恢复最大生命3.5%的生命
        # 此天赋不直接影响伤害输出，故不在此处实现。

    def _calc_single_hit_physical_damage(self, atk_val: float, enemy, is_ranged_attack: bool, remove_lord_penalty: bool = False) -> float:
        """
        计算单次物理命中时的伤害，考虑领主远程攻击力降低的特性。
        :param atk_val: 当前攻击力
        :param enemy: 敌人对象
        :param is_ranged_attack: 是否为远程攻击
        :param remove_lord_penalty: 是否移除领主远程攻击力降低的惩罚（如S3）
        :return: 单次物理命中伤害
        """
        adjusted_atk_val = atk_val
        if is_ranged_attack and not remove_lord_penalty:
            adjusted_atk_val *= 0.8  # 远程攻击力降低至80%
        
        return calculate_physical_damage(adjusted_atk_val, enemy.current_def)

    def _calc_hit_with_dot(self, atk_val: float, enemy, is_ranged_attack: bool, remove_lord_penalty: bool = False) -> float:
        """
        计算单次攻击的期望总伤害（物理伤害 + 神经腐蚀天赋的法术DoT伤害）。
        :param atk_val: 当前攻击力
        :param enemy: 敌人对象
        :param is_ranged_attack: 是否为远程攻击
        :param remove_lord_penalty: 是否移除领主远程攻击力降低的惩罚（如S3）
        :return: 单次攻击的总期望伤害
        """
        # 物理伤害部分
        physical_dmg = self._calc_single_hit_physical_damage(atk_val, enemy, is_ranged_attack, remove_lord_penalty)
        
        # 神经腐蚀天赋的法术DoT部分
        dot_total_damage_raw = self.talent_nerve_corrosion_base_dmg_per_sec * self.talent_nerve_corrosion_duration
        
        # 假设enemy对象有is_ranged属性来判断是否为远程敌人
        if hasattr(enemy, 'is_ranged') and enemy.is_ranged:
            dot_total_damage_raw *= self.talent_nerve_corrosion_ranged_multiplier
            
        arts_dmg_from_dot = calculate_arts_damage(dot_total_damage_raw, enemy.current_res)
        
        return physical_dmg + arts_dmg_from_dot

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 棘刺作为领主，普攻通常是远程攻击，因此默认考虑远程攻击的80%攻击力惩罚。
        # 并且会触发神经腐蚀天赋。
        return self._calc_hit_with_dot(self.final_base_atk, enemy, is_ranged_attack=True, remove_lord_penalty=False)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (攻击力强化·γ型)：攻击力+100%，持续30秒
            skill_duration = 30
            atk_buff_ratio = 1.00
            
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 技能期间的普攻次数
            hits_during_skill = skill_duration / actual_atk_interval
            
            # 每次普攻的伤害（考虑远程惩罚和天赋）
            # S1期间仍是远程攻击，且没有移除领主远程攻击惩罚
            single_hit_damage = self._calc_hit_with_dot(enhanced_atk, enemy, is_ranged_attack=True, remove_lord_penalty=False)
            
            total_damage = hits_during_skill * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (护身尖刺)：停止攻击，攻击力+60%，防御力+110%，
            # 受到敌人普通攻击时释放尖刺对前方最多4名敌人进行一次远程攻击（每0.6秒最多触发一次）
            # 持续40秒
            skill_duration = 40
            atk_buff_ratio = 0.60
            counter_attack_interval = 0.6 # 每0.6秒最多触发一次
            
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 技能期间的触发次数
            triggers_during_skill = skill_duration / counter_attack_interval
            
            # 每次触发的伤害（假设为100%攻击力，考虑远程惩罚和天赋）
            # 护身尖刺的攻击是远程攻击，且没有移除领主远程攻击惩罚
            single_trigger_damage = self._calc_hit_with_dot(enhanced_atk, enemy, is_ranged_attack=True, remove_lord_penalty=False)
            
            total_damage = triggers_during_skill * single_trigger_damage
            dps = single_trigger_damage / counter_attack_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (至高之术)：攻击范围扩大，攻击力+60%，攻击速度+25，远程攻击不再降低攻击力，
            # 第二次及以后使用时能力加成变为最初的两倍，且持续时间无限
            # 永续技能，total_damage为0，重点计算dps
            
            # 假设为第二次及以后使用，能力加成翻倍
            atk_buff_ratio = 0.60 * 2 # 攻击力+120%
            atk_spd_buff = 25 * 2    # 攻击速度+50
            
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            enhanced_attack_speed = self.attack_speed + atk_spd_buff
            
            # 远程攻击不再降低攻击力，所以 remove_lord_penalty=True
            single_hit_damage = self._calc_hit_with_dot(enhanced_atk, enemy, is_ranged_attack=True, remove_lord_penalty=True)
            
            # 计算实际攻击间隔
            actual_atk_interval_s3 = self.attack_interval * 100 / enhanced_attack_speed
            
            total_damage = 0 # 永续技能总伤为0
            dps = single_hit_damage / actual_atk_interval_s3
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)