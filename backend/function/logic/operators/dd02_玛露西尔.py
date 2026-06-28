from backend.function.logic.professions import Caster
from backend.function.logic.formulas import calculate_arts_damage

class Dd02玛露西尔(Caster):
    """
    干员：玛露西尔
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：建校以来第一才女
        # "有魔力时，攻击力+15%" - 假设有魔力，直接加成到最终基础攻击力
        self.final_base_atk *= (1 + 0.15)
        # "攻击溅射范围扩大" - 不影响单体伤害计算
        # "技能消耗魔力且可随时开启，魔力不自然回复，不在场时每秒回复1点" - 机制描述，不影响面板属性

        # 天赋 2：可靠的同伴
        # "初始魔力+25" - 不影响伤害计算
        # "编队中有4名【莱欧斯小队】干员时，所有【莱欧斯小队】干员攻击速度+25" - 假设条件满足，直接加成攻击速度
        self.attack_speed += 25
        # "防御力+35%" - 不影响玛露西尔的伤害输出
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害
        """
        return calculate_arts_damage(atk_val, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 玛露西尔是扩散术师，造成法术伤害
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (才女的实力)：永续技能，攻击力+140%
            # 技能描述：每次攻击消耗2点魔力，攻击力+140%，在找不到攻击目标时改为治疗友方干员，技能可随时主动关闭
            
            # 永续技能，total_damage为0，主要计算DPS
            total_damage = 0.0
            
            # 攻击力加成
            skill_atk_multiplier = 1.40
            enhanced_atk = self.final_base_atk * (1 + skill_atk_multiplier)
            
            # 计算单次强化普攻伤害
            single_hit_damage = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 计算DPS
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (召唤使魔)：永续技能，攻击力+100%，第二次使用时使魔升级，攻击速度+60
            # 技能描述：吟唱11秒后，消耗35点魔力制作并使用使魔攻击，攻击力+100%，攻击使所有命中目标停顿0.5秒；
            # 第二次使用时使魔升级，攻击距离+1，攻击速度+60，攻击晕眩主目标0.5秒；技能持续时间无限，第一次使用可随时停止
            
            # 永续技能，total_damage为0，主要计算DPS
            total_damage = 0.0
            
            # 攻击力加成
            skill_atk_multiplier = 1.00
            enhanced_atk = self.final_base_atk * (1 + skill_atk_multiplier)
            
            # 攻击速度加成 (假设为最大层数，即使魔已升级)
            skill_as_buff = 60
            skill_actual_atk_speed = self.attack_speed + skill_as_buff
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / skill_actual_atk_speed
            
            # 计算单次强化普攻伤害
            single_hit_damage = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 计算DPS
            dps = single_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (爆破魔法)：爆发技能，造成390%攻击力的法术伤害，可追加爆炸
            # 技能描述：吟唱5秒后，消耗8点魔力，在正前方位置造成爆炸，对周围敌人造成390%攻击力的法术伤害，
            # 炸到的高台会崩开碎片晕眩其周围敌人4秒；可追加吟唱10秒，完成后消耗剩余所有魔力，每额外消耗8点魔力，追加1次爆炸；追加吟唱可随时停止
            
            # 爆发伤害，计算总伤和DPS
            
            # 基础爆炸伤害倍率
            skill_atk_multiplier = 3.90
            explosion_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 计算爆炸次数：初始魔力25 (天赋2)，第一次爆炸消耗8点，后续每8点追加一次
            initial_magic = 25 # 来自天赋2
            first_explosion_cost = 8
            
            # 至少有1次爆炸
            total_explosions = 1
            
            # 计算剩余魔力可追加的爆炸次数 (假设初始魔力足够进行追加)
            if initial_magic > first_explosion_cost:
                remaining_magic = initial_magic - first_explosion_cost
                additional_explosion_cost_per_hit = 8
                num_additional_explosions = remaining_magic // additional_explosion_cost_per_hit
                total_explosions += num_additional_explosions
            
            # 计算单次爆炸伤害
            single_explosion_damage = self._calc_arts_hit(explosion_atk_val, enemy)
            
            # 计算总伤害
            total_damage = single_explosion_damage * total_explosions
            
            # 爆发技能的DPS按总伤除以普攻间隔（简化处理，不考虑吟唱时间）
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)