from backend.function.logic.professions import Fighter
from backend.function.logic.formulas import calculate_physical_damage

class Yd06左乐(Fighter):
    """
    干员：左乐
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：秉烛照影
        # "在场时，自身获得最高+50攻击速度和技力自然回复速度+2/秒的坚忍（损失70%生命值时达到最大加成）"
        # 为计算最大伤害，假设达到最大加成
        self.attack_speed += 50
        # 技力自然回复速度不直接影响单次伤害计算，故不在此处体现
        
        # 天赋 2：守正自明
        # "攻击时有20%的概率获得1点技力，生命低于50%时概率变为70%"
        # 该天赋影响技力回复，不直接影响单次伤害计算，故不在此处体现

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 武者特性："不成为其他角色的治疗目标，每次攻击到敌人后回复自身70生命"
        # 该特性不影响伤害计算
        
        # 左乐的普攻没有特殊的伤害类型或无视防御机制，直接计算物理伤害
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (破虏)：
            # "下次攻击的攻击力提升至200%，自身生命低于80%时额外攻击1次，低于50%时额外攻击2次，可充能3次"
            # 为计算最大伤害，假设生命低于50%，触发额外2次攻击，总计3次攻击
            
            # 每次攻击的攻击力倍率
            atk_multiplier = 2.0
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 总攻击次数
            total_hits = 3
            
            # 计算单次强化攻击的伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 总伤害为多次强化攻击的总和
            total_damage = single_hit_damage * total_hits
            
            # 瞬发技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (行险)：
            # "立即流失50%当前生命并获得相当于最大生命120%的屏障，攻击力+170%，阻挡数+1，同时攻击所有阻挡的敌人，屏障最高叠加至最大生命的2倍，技能结束后逐渐流失"
            # 持续时间：12秒
            
            # 攻击力增益：+170%，即攻击力变为 (1 + 1.7) = 2.7 倍
            atk_multiplier = 2.7
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 技能期间的单次普攻伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能持续期间能打出的普攻次数
            duration = 12
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            # 总伤害为技能期间普攻伤害的总和
            total_damage = single_hit_damage * hits_during_skill
            
            # DPS为强化后的单次普攻伤害除以实际攻击间隔
            return {"total_damage": total_damage, "dps": single_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (佑序有炎)：
            # "立刻对前方进行7次斩击，每次对最多3名敌人造成攻击力245%的物理伤害（最后一击系数加倍且使目标晕眩5秒），期间特性的生命回复改为获得相当于回复量3倍的屏障，屏障最高叠加至最大生命的2倍，持续15秒"
            # 伤害部分是“立刻对前方进行7次斩击”，属于瞬发爆发伤害。
            # 持续15秒指的是特性转换，不影响伤害计算。
            
            # 前6次斩击的攻击力倍率
            normal_hit_multiplier = 2.45
            normal_hit_atk = self.final_base_atk * normal_hit_multiplier
            
            # 最后1次斩击的攻击力倍率 (系数加倍)
            final_hit_multiplier = 2.45 * 2
            final_hit_atk = self.final_base_atk * final_hit_multiplier
            
            # 计算前6次斩击的总伤害
            dmg_normal_hits = calculate_physical_damage(normal_hit_atk, enemy.current_def) * 6
            
            # 计算最后1次斩击的伤害
            dmg_final_hit = calculate_physical_damage(final_hit_atk, enemy.current_def) * 1
            
            # 总伤害为所有斩击伤害的总和
            total_damage = dmg_normal_hits + dmg_final_hit
            
            # 瞬发技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)