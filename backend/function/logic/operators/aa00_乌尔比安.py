from backend.function.logic.professions import Liberator
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Aa00乌尔比安(Liberator):
    """
    干员：乌尔比安
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：本性的坚守 (每次受到伤害时，治疗自身100点生命值；生命值低于50%时，治疗效果提升至160点生命值)
        # 该天赋为生存向天赋，不直接影响DPS计算，故在此处不进行数值修改。

        # 天赋 2：血脉的哺养 (每次击倒一名敌人时，自身的生命上限提高120，攻击力提高30，最多叠加9次，其他【深海猎人】干员生命上限60，攻击力15获得50%的提高效果)
        # 该天赋为击杀叠加型天赋。在伤害计算中，按最大层数叠加。
        self.final_base_atk += 30 * 9 # 攻击力提高 30 * 9
        # 生命上限提高不影响DPS，故不修改。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 乌尔比安的普攻没有特殊机制（如暴击、破甲等），直接使用基类计算。
        # 根据规则，此方法返回单次普攻对一个目标的伤害。
        # Liberator职业特性“同时攻击阻挡的所有敌人”已由基类处理 target_count，但此方法返回的是单目标伤害。
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (必须促成的接触)：向前方扔出船锚，船锚会把目标地点周围的两名敌人中等力度地拖拽至面前，对其造成相当于攻击力270%的物理伤害
            # 瞬发伤害技能
            atk_val = self.final_base_atk * 2.7
            # 规则：无论技能描述对多少目标造成伤害，total_damage和dps必须严格是对单个目标造成的伤害。
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发伤害技能的DPS计算方式
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (必须维系的界限)：第一天赋的效果提升至2倍，阻挡数+1，生命上限+60%，攻击力+160%
            # 永续增益技能 (duration=null)
            
            # 计算强化后的攻击力
            boosted_atk = self.final_base_atk * (1 + 1.60) # 攻击力+160%
            
            # 计算强化后的单次普攻伤害 (对一个目标)
            # 即使Liberator职业特性是多目标，根据规则，这里计算的是对单个目标的伤害
            boosted_normal_hit_damage = calculate_physical_damage(boosted_atk, enemy.current_def)
            
            # 永续技能 total_damage 为 0，dps 为强化后的单次普攻伤害 / 实际攻击间隔
            return {"total_damage": 0.0, "dps": boosted_normal_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (必须开辟的通路)：最大生命值+80%，攻击力+260%，立即朝面前扔出一个船锚，
            # 撞击到目标或达到最远距离时停止，并对周围所有敌人造成攻击力160%的物理伤害和6秒晕眩。
            # 技能持续时间为25秒，包含一个立即爆发伤害和持续期间的攻击力增益。
            duration = 25
            
            # 1. 计算立即爆发伤害 (船锚投掷)
            # 规则：增益先触发！爆发伤害必须使用强化后的攻击力计算。
            # 技能描述：攻击力+260%，立即造成攻击力160%的物理伤害。
            boosted_atk_for_burst = self.final_base_atk * (1 + 2.60) # 先计算攻击力增益
            burst_final_atk_value = boosted_atk_for_burst * 1.6 # 再计算爆发倍率
            
            # 规则：无论描述如何，严禁将最终伤害乘以目标数。
            total_burst_damage = calculate_physical_damage(burst_final_atk_value, enemy.current_def)
            
            # 2. 计算技能持续期间的普攻伤害
            # 技能期间攻击力+260%
            boosted_atk_during_duration = self.final_base_atk * (1 + 2.60)
            
            # 计算技能期间能打出的普攻次数
            num_hits_during_duration = duration / actual_atk_interval
            
            # 计算强化后的单次普攻伤害 (对一个目标)
            boosted_normal_hit_damage_per_target = calculate_physical_damage(boosted_atk_during_duration, enemy.current_def)
            
            # 技能期间普攻总伤害 (规则：目标数始终视为 1)
            total_normal_attack_damage_during_duration = num_hits_during_duration * boosted_normal_hit_damage_per_target
            
            # 技能总伤害 = 爆发伤害 + 持续期间普攻总伤害
            total_damage = total_burst_damage + total_normal_attack_damage_during_duration
            
            # 技能期间DPS
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)