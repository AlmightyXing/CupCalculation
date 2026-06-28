from backend.function.logic.professions import Dreadnought
from backend.function.logic.formulas import calculate_physical_damage

class Aa01斯卡蒂(Dreadnought):
    """
    干员：斯卡蒂
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents() # 在 final_base_atk 计算完成后调用天赋
        
    def apply_talents(self):
        # 天赋 1：深海掠食者
        # "编入队伍时，所有【深海猎人】干员的攻击力+14%"
        # 斯卡蒂自身作为深海猎人，也受益于此天赋。
        self.final_base_atk *= (1 + 0.14)
        
        # 天赋 2：迅捷出击
        # "自身再部署时间-10秒" - 不影响伤害计算，因此在此处忽略。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 斯卡蒂的普攻没有特殊的伤害类型、无视防御或多段伤害机制
        # Dreadnought基类没有覆写此方法，因此直接调用super()即可获得默认物理伤害计算
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算技能期间的攻击次数和DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1: 迅捷打击·γ型
            # 持续时间: 35秒
            # 描述: "攻击力+45%，攻击速度+45"
            
            skill_duration = 35
            atk_buff_ratio = 0.45
            atk_speed_buff = 45
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + atk_buff_ratio)
            # 计算强化后的攻击速度
            buffed_atk_speed = self.attack_speed + atk_speed_buff
            
            # 计算强化后的实际攻击间隔
            buffed_actual_atk_interval = self.attack_interval * 100 / buffed_atk_speed
            
            # 计算技能持续期间的普攻次数
            num_attacks = skill_duration / buffed_actual_atk_interval
            
            # 计算单次普攻的期望伤害（使用强化后的攻击力）
            dmg_per_hit = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            # 计算总伤害和DPS
            total_damage = num_attacks * dmg_per_hit
            dps = dmg_per_hit / buffed_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2: 跃浪击
            # 持续时间: 描述中为"部署后30秒内"，即30秒
            # 描述: "部署后30秒内攻击力+170%"
            
            skill_duration = 30
            atk_buff_ratio = 1.70
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 此技能无攻击速度加成，使用基础实际攻击间隔
            
            # 计算技能持续期间的普攻次数
            num_attacks = skill_duration / actual_atk_interval
            
            # 计算单次普攻的期望伤害（使用强化后的攻击力）
            dmg_per_hit = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            # 计算总伤害和DPS
            total_damage = num_attacks * dmg_per_hit
            dps = dmg_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3: 涌潮悲歌
            # 持续时间: 50秒
            # 描述: "攻击力、防御力和生命上限各+130%"
            
            skill_duration = 50
            atk_buff_ratio = 1.30
            
            # 计算强化后的攻击力
            buffed_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 此技能无攻击速度加成，使用基础实际攻击间隔
            
            # 计算技能持续期间的普攻次数
            num_attacks = skill_duration / actual_atk_interval
            
            # 计算单次普攻的期望伤害（使用强化后的攻击力）
            dmg_per_hit = calculate_physical_damage(buffed_atk, enemy.current_def)
            
            # 计算总伤害和DPS
            total_damage = num_attacks * dmg_per_hit
            dps = dmg_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果没有匹配的技能，调用基类的计算方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)
