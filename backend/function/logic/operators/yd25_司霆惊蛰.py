from backend.function.logic.professions import Liberator
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Yd25司霆惊蛰(Liberator):
    """
    干员：司霆惊蛰
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：明断
        # "攻击范围内每个地块每秒有10%的概率落雷对所有敌人造成相当于攻击力100%的法术伤害。"
        # "未开启技能时起飞；技能期间攻击时攻击力提升至107%"
        self.talent1_lightning_prob_per_sec = 0.1  # 每秒落雷概率
        self.talent1_lightning_atk_ratio = 1.0     # 落雷伤害倍率
        self.talent1_skill_atk_boost = 1.07        # 技能期间物理攻击力提升倍率

        # 天赋 2：追责
        # "开启技能时，使攻击范围内所有地面地块落雷，对所有敌人造成相当于攻击力100%的法术伤害和2秒战栗"
        self.talent2_skill_activate_lightning_atk_ratio = 1.0 # 技能开启时瞬发落雷伤害倍率

        # 解放者特性 (Liberator Trait):
        # "通常不攻击且阻挡数为0，技能未开启时40秒内攻击力逐渐提升至最高+200%且技能结束时重置攻击力"
        # -> "通常不攻击"意味着 calculate_normal_hit 返回0。
        # -> 技能期间，攻击力加成重置，使用基础攻击力（受天赋1的107%影响）。

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 司霆惊蛰作为解放者，通常不进行普攻。因此普攻伤害为0。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        # 天赋 2：追责 - 技能开启时瞬发法术伤害
        # 此伤害使用干员的最终基础攻击力（不受技能期间攻击力加成影响）
        talent2_burst_damage = calculate_arts_damage(
            self.final_base_atk * self.talent2_skill_activate_lightning_atk_ratio,
            enemy.current_res
        )
        total_damage += talent2_burst_damage

        if skill_index == 0:
            # 技能 1 (浩气长存)：
            # duration = 0.5
            # "对三个方向的地面敌人各造成相当于攻击力355%的物理伤害"
            # (根据规则，严禁乘以目标数，只计算对单个目标的伤害)
            
            skill_duration = 0.5
            
            # 物理攻击力计算：基础攻击力 * 天赋1技能期间攻击力提升 * 技能倍率
            skill_atk_val = self.final_base_atk * self.talent1_skill_atk_boost * 3.55
            physical_hit_damage = calculate_physical_damage(skill_atk_val, enemy.current_def)
            
            total_damage += physical_hit_damage
            
            # 天赋 1：明断 - 技能期间持续落雷伤害
            # 落雷伤害也受益于天赋1的技能期间攻击力提升
            lightning_atk_val = self.final_base_atk * self.talent1_skill_atk_boost * self.talent1_lightning_atk_ratio
            lightning_dps_per_tile = self.talent1_lightning_prob_per_sec * calculate_arts_damage(lightning_atk_val, enemy.current_res)
            total_damage += lightning_dps_per_tile * skill_duration # 将持续伤害计入总伤

            # 对于瞬发或极短持续时间的技能，DPS通常按总伤除以一个标准攻击间隔来衡量
            dps = total_damage / actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (正霆摄威)：
            # duration = 36
            # "攻击对4个目标造成相当于攻击力150%的物理伤害。"
            # "技能期间每次落雷使攻击力+10%（最多可叠加25次）"
            
            skill_duration = 36
            
            # 计算技能2的最大攻击力加成 (25次 * 10% = 250%)
            skill2_atk_stack_multiplier = 1 + (25 * 0.10) # 1 + 2.5 = 3.5
            
            # 技能期间的最终攻击力：基础攻击力 * 天赋1技能期间攻击力提升 * 技能2叠加攻击力倍率
            enhanced_atk_for_skill = self.final_base_atk * self.talent1_skill_atk_boost * skill2_atk_stack_multiplier
            
            # 物理攻击伤害
            physical_hit_damage = calculate_physical_damage(enhanced_atk_for_skill * 1.50, enemy.current_def)
            
            # 技能期间的普攻次数
            num_physical_attacks = skill_duration / actual_atk_interval
            total_damage += num_physical_attacks * physical_hit_damage
            
            # 天赋 1：明断 - 技能期间持续落雷伤害
            # 落雷伤害也受益于技能2的攻击力叠加
            lightning_atk_val = self.final_base_atk * self.talent1_skill_atk_boost * skill2_atk_stack_multiplier * self.talent1_lightning_atk_ratio
            lightning_dps_per_tile = self.talent1_lightning_prob_per_sec * calculate_arts_damage(lightning_atk_val, enemy.current_res)
            total_damage += lightning_dps_per_tile * skill_duration
            
            dps = total_damage / skill_duration
            
        elif skill_index == 2:
            # 技能 3 (天地通明)：
            # duration = 24
            # "攻击间隔大幅延长(+1.7)，攻击造成攻击力300%的范围物理伤害"
            # "目标位置产生朝四周流动三格的电流。电流碰到自身或高台时反弹，
            # 电流所在地块上所有敌人每0.6秒受到司霆惊蛰攻击力70%的法术伤害"
            
            skill_duration = 24
            skill_atk_interval_modifier = 1.7 # 攻击间隔延长值
            
            # 计算技能3的实际攻击间隔
            skill3_actual_atk_interval = (self.attack_interval + skill_atk_interval_modifier) * 100 / self.attack_speed
            
            # 技能期间的最终攻击力：基础攻击力 * 天赋1技能期间攻击力提升
            enhanced_atk_for_skill = self.final_base_atk * self.talent1_skill_atk_boost
            
            # 物理攻击伤害
            physical_hit_damage = calculate_physical_damage(enhanced_atk_for_skill * 3.00, enemy.current_def)
            
            # 技能期间的普攻次数
            num_physical_attacks = skill_duration / skill3_actual_atk_interval
            total_damage += num_physical_attacks * physical_hit_damage
            
            # 天赋 1：明断 - 技能期间持续落雷伤害
            # 落雷伤害受益于天赋1的技能期间攻击力提升
            lightning_atk_val = self.final_base_atk * self.talent1_skill_atk_boost * self.talent1_lightning_atk_ratio
            lightning_dps_per_tile = self.talent1_lightning_prob_per_sec * calculate_arts_damage(lightning_atk_val, enemy.current_res)
            total_damage += lightning_dps_per_tile * skill_duration
            
            # 技能 3 额外电流伤害
            current_damage_interval = 0.6
            current_atk_ratio = 0.7
            # 电流伤害使用“司霆惊蛰攻击力”，即 enhanced_atk_for_skill
            current_arts_damage_per_hit = calculate_arts_damage(enhanced_atk_for_skill * current_atk_ratio, enemy.current_res)
            current_dps_per_tile = current_arts_damage_per_hit / current_damage_interval
            total_damage += current_dps_per_tile * skill_duration
            
            dps = total_damage / skill_duration
            
        return {"total_damage": total_damage, "dps": dps}