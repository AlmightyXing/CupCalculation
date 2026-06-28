from backend.function.logic.professions import PhalanxCaster
from backend.function.logic.formulas import calculate_arts_damage

class Kj02圣聆初雪(PhalanxCaster):
    """
    干员：圣聆初雪
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：无垠的雪景
        # 攻击范围内的地面每隔5.5秒产生一层积雪，地面敌人经过时立即受到相当于攻击力75%的法术伤害
        # 假设目标敌人始终处于积雪影响范围，且积雪伤害可叠加到总伤/DPS中
        self.talent1_snow_damage_ratio = 0.75
        self.talent1_snow_damage_interval = 5.5 # 秒
        
        # 天赋 2：圣山的祝福
        # 受到伤害时使敌人寒冷1.5秒，若受到致命伤害，仅一次立刻回复所有生命值并使自身冻结4秒，使攻击范围内所有敌方单位冻结8秒
        # 此天赋不直接增加伤害，不纳入伤害计算。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 圣聆初雪的职业特性是“通常时不攻击”，因此普攻伤害为0
        # PhalanxCaster父类已实现此特性，此处保持一致
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 辅助函数：计算天赋1“无垠的雪景”带来的每秒伤害（DPS）
        def get_talent1_snow_dps(atk_val: float) -> float:
            # 积雪伤害为法术伤害，但这里只计算其DPS贡献，不涉及抗性计算，因为是触发式伤害
            # 伤害值 = 攻击力 * 伤害倍率
            # DPS = 伤害值 / 触发间隔
            return (atk_val * self.talent1_snow_damage_ratio) / self.talent1_snow_damage_interval

        if skill_index == 0:
            # 技能 1 (铃音吹雪)：立即对范围内所有敌人造成相当于攻击力520%的法术伤害
            # 瞬发伤害技能
            
            # 瞬发伤害计算
            atk_val = self.final_base_atk * 5.20
            instant_damage = calculate_arts_damage(atk_val, enemy.current_res)
            
            # 积雪扩散等效果不直接计入单次伤害计算
            
            total_damage = instant_damage
            # 对于瞬发技能，DPS通常是总伤除以一个“等效攻击间隔”，这里使用实际攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (霜涛覆岭)：永续技能 (duration: null)
            # 每次攻击造成相当于攻击力380%的法术伤害
            # 处于积雪上的地面敌人每秒受到攻击力20%的法术伤害
            
            # 永续技能 total_damage 为 0，重点计算DPS
            total_damage = 0.0
            
            # 1. 每次攻击造成的伤害
            skill_atk_val = self.final_base_atk * 3.80
            single_hit_damage = calculate_arts_damage(skill_atk_val, enemy.current_res)
            
            # 2. 技能期间积雪的每秒法术伤害 (DoT)
            skill_snow_dot_per_sec = self.final_base_atk * 0.20
            
            # 3. 天赋1的积雪伤害 (使用当前基础攻击力)
            talent1_snow_dps = get_talent1_snow_dps(self.final_base_atk)
            
            # 总DPS = (单次攻击伤害 / 实际攻击间隔) + 技能积雪DoT + 天赋1积雪DPS
            dps = (single_hit_damage / actual_atk_interval) + skill_snow_dot_per_sec + talent1_snow_dps
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (群山俯首)：持续35秒
            # 攻击力+100%，攻击速度+30，攻击无视目标10点法术抗性，每次攻击造成相当于攻击力260%的法术伤害
            # 积雪生成速度加快 (未量化具体数值，假设天赋1积雪间隔不变，但伤害受攻击力加成)
            
            duration = 35.0
            
            # 1. 应用技能增益
            atk_buff_ratio = 1.00 # 攻击力+100%
            atk_speed_buff = 30 # 攻击速度+30
            res_ignore = 10 # 无视目标10点法术抗性
            
            boosted_atk = self.final_base_atk * (1 + atk_buff_ratio)
            boosted_attack_speed = self.attack_speed + atk_speed_buff
            
            # 计算强化后的实际攻击间隔
            boosted_actual_atk_interval = self.attack_interval * 100 / boosted_attack_speed
            
            # 2. 计算单次攻击伤害
            skill_hit_atk_val = boosted_atk * 2.60 # 260%攻击力
            single_hit_damage = calculate_arts_damage(skill_hit_atk_val, enemy.current_res, res_ignore=res_ignore)
            
            # 3. 计算技能期间的攻击次数
            num_attacks = duration / boosted_actual_atk_interval
            
            # 4. 计算天赋1积雪伤害 (使用强化后的攻击力)
            talent1_snow_dps = get_talent1_snow_dps(boosted_atk)
            
            # 总伤 = 技能期间普攻总伤 + 技能期间天赋1积雪总伤
            total_damage = (num_attacks * single_hit_damage) + (talent1_snow_dps * duration)
            
            # DPS = (单次攻击伤害 / 强化后实际攻击间隔) + 天赋1积雪DPS
            dps = (single_hit_damage / boosted_actual_atk_interval) + talent1_snow_dps
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
