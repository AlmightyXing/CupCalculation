from backend.function.logic.professions import Ambusher
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Sw00阿斯卡纶(Ambusher):
    """
    干员：阿斯卡纶
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：死亡拘审
        # 攻击对敌人施加效果：每秒受到10％阿斯卡纶当前攻击力的法术伤害，持续25秒，效果最多叠加三层
        # 根据规则，天赋对提高伤害有帮助的均纳入考虑，可叠加层数的按最大层数计算。
        self.talent1_dot_ratio_per_sec = 0.10  # 每秒伤害比例
        self.talent1_dot_max_stacks = 3      # 最大叠加层数
        self.talent1_dot_duration = 25       # DoT持续时间

        # 天赋 2：噬光残影
        # 攻击速度+8，自身周围四格有高台时，攻击速度额外+6
        # 叠加到属性中，按最大值计算
        self.attack_speed += (8 + 6) # 总计攻击速度+14
        
    def _calc_talent1_dot_damage(self, atk_val: float, enemy) -> float:
        """
        计算天赋1“死亡拘审”单次攻击触发时，最大层数DoT的期望总伤害。
        此DoT为法术伤害。
        """
        # 每秒法术伤害 = 攻击力 * 每秒伤害比例 * 最大层数
        dot_per_sec_val = atk_val * self.talent1_dot_ratio_per_sec * self.talent1_dot_max_stacks
        # 单次触发的DoT总伤害 = 每秒法术伤害 * 持续时间
        total_dot_from_one_application = dot_per_sec_val * self.talent1_dot_duration
        return calculate_arts_damage(total_dot_from_one_application, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻是物理伤害
        physical_dmg = calculate_physical_damage(self.final_base_atk, enemy.current_def)
        
        # 加上天赋1的DoT伤害 (假设每次普攻都能触发并刷新/维持最大层数DoT)
        dot_dmg = self._calc_talent1_dot_damage(self.final_base_atk, enemy)
        
        return physical_dmg + dot_dmg

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (追袭)：下次攻击的攻击力提升至210%，并连续攻击两次，可充能3次
            # 瞬发技能，计算爆发伤害
            atk_multiplier = 2.10
            hits = 2 # 连续攻击两次
            
            # 技能爆发伤害使用强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 物理伤害
            physical_dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            total_physical_damage = physical_dmg_per_hit * hits
            
            # 天赋1 DoT伤害 (假设一次技能触发一次最大层数DoT，即使攻击两次也只算一次完整的DoT效果)
            dot_dmg = self._calc_talent1_dot_damage(enhanced_atk, enemy)
            
            total_damage = total_physical_damage + dot_dmg
            # 瞬发技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (恩赐)：攻击力+130%，持续35秒
            duration = 35
            atk_buff_ratio = 1.30
            
            # 技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 技能期间能打出的普攻次数
            hits_during_skill = duration / actual_atk_interval
            
            # 单次普攻的物理伤害 (强化后)
            physical_dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 单次普攻触发的天赋1 DoT伤害 (强化后)
            # 增益类技能中，每次攻击都会触发天赋，所以DoT伤害计入每次攻击
            dot_dmg_per_hit = self._calc_talent1_dot_damage(enhanced_atk, enemy)
            
            # 每次攻击的总伤害 (物理 + DoT)
            total_dmg_per_attack = physical_dmg_per_hit + dot_dmg_per_hit
            
            total_damage = total_dmg_per_attack * hits_during_skill
            dps = total_dmg_per_attack / actual_atk_interval
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (降临)：攻击范围扩大，攻击力+50%，攻击间隔较大幅度缩短(-1.5)，持续45秒
            duration = 45
            atk_buff_ratio = 0.50
            atk_interval_reduction = 1.5 # 攻击间隔缩短1.5秒
            
            # 技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能期间的实际攻击间隔
            # 原始攻击间隔 self.attack_interval (例如3.5秒)
            # 技能描述是 "攻击间隔较大幅度缩短(-1.5)"，这意味着 attack_interval 减少 1.5
            modified_base_attack_interval = self.attack_interval - atk_interval_reduction
            
            # 结合攻速加成计算最终实际攻击间隔
            actual_atk_interval_skill3 = modified_base_attack_interval * 100 / self.attack_speed
            
            # 技能期间能打出的普攻次数
            hits_during_skill = duration / actual_atk_interval_skill3
            
            # 单次普攻的物理伤害 (强化后)
            physical_dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 单次普攻触发的天赋1 DoT伤害 (强化后)
            dot_dmg_per_hit = self._calc_talent1_dot_damage(enhanced_atk, enemy)
            
            # 每次攻击的总伤害 (物理 + DoT)
            total_dmg_per_attack = physical_dmg_per_hit + dot_dmg_per_hit
            
            total_damage = total_dmg_per_attack * hits_during_skill
            dps = total_dmg_per_attack / actual_atk_interval_skill3
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)