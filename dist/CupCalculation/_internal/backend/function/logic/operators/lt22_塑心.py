from backend.function.logic.professions import IncantationMedic
from backend.function.logic.formulas import calculate_arts_damage

class Lt22塑心(IncantationMedic):
    """
    干员：塑心
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.decay_damage_ratio_talent1 = 0.0  # 天赋1：无词哀歌 - 每秒凋亡损伤比例
        self.decay_damage_boost_talent2 = 0.0  # 天赋2：精神逆构 - 凋亡损伤提高比例
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：无词哀歌 (使攻击范围内敌人每秒受到相当于攻击力10%的凋亡损伤并停顿0.2秒)
        # 存储凋亡损伤的攻击力比例
        self.decay_damage_ratio_talent1 = 0.10
        
        # 天赋 2：精神逆构 (使攻击范围内敌人受到的凋亡损伤提高20%)
        # 存储凋亡损伤的额外提高比例
        self.decay_damage_boost_talent2 = 0.20
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 塑心攻击造成法术伤害
        # 技能1未开启时无法普通攻击，但此处仍需返回普攻的期望伤害
        # 普攻只计算直接法术伤害，不包含每秒的凋亡损伤
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取当前攻击速度，用于计算实际攻击间隔
        current_attack_speed = self.attack_speed
        actual_atk_interval = self.attack_interval * 100 / current_attack_speed
        
        # 计算基础的每秒凋亡损伤（来自天赋1，并受天赋2加成）
        # 这是在技能未修改天赋效果前的基础值
        base_talent_decay_damage_per_sec = self.final_base_atk * self.decay_damage_ratio_talent1 * (1 + self.decay_damage_boost_talent2)

        if skill_index == 0:
            # 技能 1 (黄金的狂喜)：
            # "对一个未处于损伤爆发期间的敌人造成相当于攻击力300%的法术伤害并附带110%攻击力的凋亡损伤，可充能3次，技能未开启时无法普通攻击"
            # 这是一个瞬发爆发技能。
            
            # 法术伤害部分：300%攻击力
            arts_atk_val = self.final_base_atk * 3.0
            direct_arts_damage = calculate_arts_damage(arts_atk_val, enemy.current_res)
            
            # 凋亡损伤部分：110%攻击力，并受天赋2加成
            skill_decay_damage_raw = self.final_base_atk * 1.10
            skill_decay_damage_boosted = skill_decay_damage_raw * (1 + self.decay_damage_boost_talent2)
            
            total_damage = direct_arts_damage + skill_decay_damage_boosted
            
            # 瞬发伤害技能的DPS计算方式：总伤 / 实际攻击间隔
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (安魂的弥撒)：
            # "攻击速度+60，额外攻击1个目标，自身和攻击范围内攻击力最高的另一名友方干员对敌人造成伤害时附带自身25%攻击力的凋亡损伤"
            # 持续时间：20秒
            
            duration = 20
            
            # 攻击速度加成
            skill_attack_speed = current_attack_speed + 60
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 技能持续期间的普攻次数
            num_hits = duration / skill_actual_atk_interval
            
            # 单次普攻的法术伤害
            single_hit_arts_damage = calculate_arts_damage(self.final_base_atk, enemy.current_res)
            
            # 技能附带的额外凋亡损伤 (25%攻击力，受天赋2加成)
            extra_skill_decay_damage_raw_per_hit = self.final_base_atk * 0.25
            extra_skill_decay_damage_boosted_per_hit = extra_skill_decay_damage_raw_per_hit * (1 + self.decay_damage_boost_talent2)
            
            # 单次攻击造成的总伤害 (直接法术伤害 + 技能附带的凋亡损伤)
            damage_per_attack = single_hit_arts_damage + extra_skill_decay_damage_boosted_per_hit
            
            # 技能期间攻击造成的总伤害
            total_attack_damage = num_hits * damage_per_attack
            
            # 技能期间来自天赋1的持续凋亡损伤总和
            total_talent_decay_damage = base_talent_decay_damage_per_sec * duration
            
            # 技能期间的总伤害 = 攻击总伤 + 天赋持续凋亡总伤
            total_damage = total_attack_damage + total_talent_decay_damage
            
            # DPS = (单次攻击总伤 / 技能实际攻击间隔) + 天赋1每秒凋亡损伤
            dps = (damage_per_attack / skill_actual_atk_interval) + base_talent_decay_damage_per_sec
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (自由的探戈)：
            # "停止攻击，攻击范围扩大，攻击力+180%，第二天赋效果提升至2.5倍；技能期间使攻击范围内其他干员生命上限最高的生命上限+30%、攻击力最高的攻击力+30%、防御力最高的防御力+30%"
            # 持续时间：40秒
            
            duration = 40
            
            # "停止攻击" - 塑心自身不造成直接攻击伤害
            
            # "攻击力+180%" - 影响凋亡损伤的攻击力基数
            skill_atk_multiplier = 1.80
            
            # "第二天赋效果提升至2.5倍"
            # 原始天赋2加成：0.20
            # 技能期间天赋2加成：0.20 * 2.5 = 0.50
            skill_talent2_boost = 0.20 * 2.5
            
            # 计算技能期间凋亡损伤的有效攻击力
            effective_atk_for_decay = self.final_base_atk * (1 + skill_atk_multiplier)
            
            # 计算技能期间每秒凋亡损伤
            # (有效攻击力) * (天赋1凋亡损伤比例) * (1 + 技能强化后的天赋2加成)
            skill_decay_damage_per_sec = effective_atk_for_decay * self.decay_damage_ratio_talent1 * (1 + skill_talent2_boost)
            
            # 技能期间的总伤害 = 每秒凋亡损伤 * 持续时间
            total_damage = skill_decay_damage_per_sec * duration
            
            # DPS = 每秒凋亡损伤
            dps = skill_decay_damage_per_sec
            
            # 友方干员的增益不计入塑心自身的伤害计算
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
