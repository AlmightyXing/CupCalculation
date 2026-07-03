from backend.function.logic.professions import IncantationMedic
from backend.function.logic.formulas import calculate_arts_damage

class Ct01酒神(IncantationMedic):
    """
    干员：酒神
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：形为心役
        # "攻击附带相当于攻击力30%的神经损伤，并对目标周围其他敌人造成一次相当于攻击力20%的神经损伤"
        # 神经损伤属于元素损伤，不直接计入普攻或技能的法术/物理伤害总伤和DPS。
        # 但为了记录天赋效果，可以定义属性。
        self.talent_nerve_damage_main_target_ratio = 0.3
        self.talent_nerve_damage_splash_target_ratio = 0.2
        
        # 天赋 2：堕梦
        # "在场时，全场处于神经损伤爆发期间的敌人攻击速度-12；攻击范围内的敌人普通攻击时受到70点神经损伤"
        # 攻击速度-12是敌方debuff，不影响自身面板。
        # 70点神经损伤是敌方普攻触发的被动伤害，不计入自身普攻或技能的法术/物理伤害总伤和DPS。
        self.talent_nerve_damage_on_enemy_attack = 70
        
        # 酒神是巫役，攻击造成法术伤害。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 酒神的普攻造成法术伤害
        # 巫役特性：攻击造成法术伤害
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (暗夜回声)：
            # "下次攻击造成两次相当于攻击力150%的法术伤害并使目标束缚3秒..."
            # 这是一个瞬发技能，只影响下一次攻击。
            
            # 强化后的攻击力
            atk_val = self.final_base_atk * 1.5
            
            # 单次命中伤害 (法术伤害)
            single_hit_damage = calculate_arts_damage(atk_val, enemy.current_res)
            
            # 造成两次伤害，总伤为两次伤害之和
            total_damage = single_hit_damage * 2
            
            # DPS计算：总伤 / 攻击间隔 (模拟一次攻击的爆发)
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (群体性谵妄)：
            # "攻击速度+35...持续时间无限..."
            # 永续技能，total_damage为0，主要计算DPS。
            # "本能的召唤"部分是召唤物的伤害，不计入干员自身的总伤和DPS。
            
            # 攻击速度加成
            buffed_attack_speed = self.attack_speed + 35
            
            # 计算强化后的实际攻击间隔
            buffed_actual_atk_interval = self.attack_interval * 100 / buffed_attack_speed
            
            # 永续技能，攻击力无直接加成，普攻伤害不变
            single_hit_damage = calculate_arts_damage(self.final_base_atk, enemy.current_res)
            
            # DPS计算：单次普攻伤害 / 强化后的攻击间隔
            dps = single_hit_damage / buffed_actual_atk_interval
            
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (空剧场)：
            # "攻击范围扩大，攻击力+125%...持续时间30秒..."
            # 增益类技能，计算技能持续期间的普攻总伤和DPS。
            
            duration = 30
            
            # 攻击力加成
            buffed_atk = self.final_base_atk * (1 + 1.25)
            
            # 单次命中伤害 (法术伤害)
            single_hit_damage = calculate_arts_damage(buffed_atk, enemy.current_res)
            
            # 技能期间能打出的普攻次数
            attacks_during_skill = (duration or 0) / actual_atk_interval
            
            # 总伤害 = 单次强化普攻伤害 * 普攻次数
            total_damage = single_hit_damage * attacks_during_skill
            
            # DPS计算：单次强化普攻伤害 / 攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果技能索引不匹配，调用基类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)
