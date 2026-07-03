from backend.function.logic.professions import Lord
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Yd20仇白(Lord):
    """
    干员：仇白
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：入隙 (攻击处于停顿、束缚的敌人时，额外造成相当于攻击力40%的法术伤害)
        self.talent_rift_bonus_ratio = 0.4
        
        # 天赋 2：落英 (攻击时有20%的几率使目标束缚1.5秒)
        # 假设此束缚可以触发天赋1，因此在计算期望伤害时，有20%概率触发天赋1的额外法术伤害
        self.talent_falling_petals_prob = 0.2
        
    def _calculate_chubai_hit_damage(self, 
                                      base_atk_val: float, 
                                      enemy, 
                                      is_ranged: bool = True, 
                                      is_enemy_cced: bool = False, 
                                      talent_rift_multiplier: float = 1.0,
                                      force_arts_damage: bool = False) -> float:
        """
        仇白单次攻击的期望伤害计算。
        考虑领主特性、天赋1、天赋2以及技能对伤害类型和天赋1的修改。
        
        Args:
            base_atk_val: 此次攻击的基础攻击力（已包含技能ATK加成，未包含领主远程惩罚）
            enemy: 敌人对象
            is_ranged: 是否为远程攻击，影响领主特性 (True表示受80%惩罚，False表示不受)
            is_enemy_cced: 敌人是否确定处于停顿/束缚状态 (例如被技能强制停顿)。
                           如果为True，天赋1 100%触发；否则，按天赋2概率触发。
            talent_rift_multiplier: 天赋1的伤害倍率修正 (S3会翻倍)
            force_arts_damage: 是否强制将普攻类型变为法术伤害 (S3)
        """
        
        # 领主特性：远程攻击力降低至80%
        effective_atk = base_atk_val
        if is_ranged:
            effective_atk *= 0.8
            
        # 基础伤害部分
        base_damage = 0.0
        if force_arts_damage:
            base_damage = calculate_arts_damage(effective_atk, enemy.current_res)
        else:
            base_damage = calculate_physical_damage(effective_atk, enemy.current_def)
            
        # 天赋1：入隙 (额外法术伤害)
        # 触发条件：敌人处于停顿/束缚
        # 触发概率：
        #   1. 如果 is_enemy_cced 为 True，则100%触发
        #   2. 否则，有 self.talent_falling_petals_prob 概率触发 (天赋2的束缚)
        
        talent_rift_damage = 0.0
        rift_trigger_prob = 0.0
        
        if is_enemy_cced:
            rift_trigger_prob = 1.0
        else:
            rift_trigger_prob = self.talent_falling_petals_prob
            
        if rift_trigger_prob > 0:
            rift_atk_val = effective_atk * self.talent_rift_bonus_ratio * talent_rift_multiplier
            talent_rift_damage = calculate_arts_damage(rift_atk_val, enemy.current_res)
            
        # 期望总伤害 = 基础伤害 + 期望天赋1伤害
        return base_damage + rift_trigger_prob * talent_rift_damage

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻默认是远程攻击，且没有技能加成，天赋1触发概率由天赋2决定
        return self._calculate_chubai_hit_damage(
            base_atk_val=self.final_base_atk,
            enemy=enemy,
            is_ranged=True, # 普攻默认远程，受80%惩罚
            is_enemy_cced=getattr(enemy, 'is_cced', False), # 普攻时敌人不默认被CC，天赋1触发概率由天赋2决定
            talent_rift_multiplier=1.0,
            force_arts_damage=False
        )

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS和攻击次数
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (留羽)：
            # "下次攻击使目标束缚3秒，该次束缚结束时对目标和附近的所有敌人造成相当于攻击力300%的法术伤害"
            # 这是一个瞬发爆发伤害，发生在束缚结束后。
            # 爆发伤害通常不享受领主远程惩罚，也不触发天赋1 (因为束缚已结束)。
            
            burst_atk_val = self.final_base_atk * 3.0
            total_damage = calculate_arts_damage(burst_atk_val, enemy.current_res)
            dps = total_damage / actual_atk_interval # 视为替换一次普攻的周期
            
        elif skill_index == 1:
            # 技能 2 (承影)：
            # "对前方范围内的地面敌人造成攻击力300%的法术伤害；
            # 攻击范围改变，攻击力+140%，攻击范围内的地面敌人停顿；
            # 技能结束时对范围内的地面敌人造成攻击力300%的物理伤害"
            # Duration: 5秒
            
            duration = 5.0
            
            # 1. 技能开始时的瞬发法术伤害
            # 瞬发伤害不享受领主远程惩罚，不触发天赋1
            initial_burst_atk_val = self.final_base_atk * 3.0
            initial_burst_damage = calculate_arts_damage(initial_burst_atk_val, enemy.current_res)
            total_damage += initial_burst_damage
            
            # 2. 技能持续期间的普攻伤害
            # 攻击力+140%
            # 攻击范围内的地面敌人停顿 -> 100%触发天赋1
            # 远程攻击惩罚依然存在 (技能描述未移除)
            
            skill_atk_buff_ratio = 1.4
            enhanced_base_atk = self.final_base_atk * (1 + skill_atk_buff_ratio)
            
            # 计算单次强化普攻伤害
            single_hit_damage_during_skill = self._calculate_chubai_hit_damage(
                base_atk_val=enhanced_base_atk,
                enemy=enemy,
                is_ranged=True, # 假设仍是远程攻击，受80%惩罚
                is_enemy_cced=True, # 敌人被停顿，天赋1 100%触发
                talent_rift_multiplier=1.0,
                force_arts_damage=False # 伤害类型未改变
            )
            
            num_hits = (duration or 0) / actual_atk_interval
            total_damage += num_hits * single_hit_damage_during_skill
            
            # 3. 技能结束时的瞬发物理伤害
            # 瞬发伤害不享受领主远程惩罚，不触发天赋1 (停顿已结束)
            final_burst_atk_val = self.final_base_atk * 3.0
            final_burst_damage = calculate_physical_damage(final_burst_atk_val, enemy.current_def)
            total_damage += final_burst_damage
            
            dps = total_damage / duration
            
        elif skill_index == 2:
            # 技能 3 (问雪)：
            # "攻击范围扩大，攻击力+55%，伤害类型变为法术，额外攻击2个目标，
            # 第一天赋的伤害提升至2倍，远程攻击不再降低伤害，
            # 每次攻击使自身攻击速度+13（最多叠加8次）"
            # Duration: 30秒
            
            duration = 30.0
            
            # 攻击力+55%
            skill_atk_buff_ratio = 0.55
            enhanced_base_atk = self.final_base_atk * (1 + skill_atk_buff_ratio)
            
            # 攻击速度加成：+13 * 8次 = +104 (最大叠加)
            temp_attack_speed = self.attack_speed + (13 * 8)
            temp_actual_atk_interval = self.attack_interval * 100 / temp_attack_speed
            
            # 计算单次强化普攻伤害
            single_hit_damage_during_skill = self._calculate_chubai_hit_damage(
                base_atk_val=enhanced_base_atk,
                enemy=enemy,
                is_ranged=False, # 远程攻击不再降低伤害
                is_enemy_cced=getattr(enemy, 'is_cced', False), # 技能本身不提供CC，天赋1触发概率由天赋2决定
                talent_rift_multiplier=2.0, # 天赋1伤害提升至2倍
                force_arts_damage=True # 伤害类型变为法术
            )
            
            num_hits = duration / temp_actual_atk_interval
            total_damage = num_hits * single_hit_damage_during_skill
            dps = total_damage / duration
            
        return {"total_damage": total_damage, "dps": dps}