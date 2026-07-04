from backend.function.logic.professions import Earthshaker
from backend.function.logic.formulas import calculate_physical_damage

class Uss0怒潮凛冬(Earthshaker):
    """
    干员：怒潮凛冬
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 撼地者职业特性：攻击使目标周围的其他敌人受到相当于攻击力50%的群体物理伤害
        # 这个溅射伤害是针对“其他敌人”的，不计入对“单个目标”的伤害计算。
        # 但其比例会受天赋影响，因此在此初始化并存储。
        self.characteristic_splash_ratio = 0.5 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：汹涌怒火
        # "特性溅射造成的物理伤害提升24%"
        # 溅射伤害比例从50%提升至 50% * (1 + 0.24) = 62%
        # 注意：根据规则，此溅射伤害是针对“其他敌人”的，不计入对“单个目标”的total_damage和dps。
        self.characteristic_splash_ratio *= (1 + 0.24)
        
        # 天赋 2：万众巨潮
        # "技能期间所有场上干员攻击力和防御力+14%，【乌萨斯学生自治团】干员获得加成效果翻倍"
        # 此天赋影响的是“其他干员”，不直接提升怒潮凛冬自身的伤害，因此在计算怒潮凛冬自身伤害时无需体现。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 撼地者的普攻对主要目标造成标准物理伤害。
        # 溅射伤害是针对其他目标的，不计入对单个目标的总伤。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取当前攻击间隔（受攻速影响）
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 0: 誓不低头
            # 描述: "攻击力+50%，攻击速度+50"
            # 持续时间: 30秒
            
            # 计算技能期间的强化攻击力
            skill_atk_multiplier = 1.0 + 0.50
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 计算技能期间的强化攻击速度
            enhanced_attack_speed = self.attack_speed + 50
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / enhanced_attack_speed
            
            # 计算单次普攻的伤害
            dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的普攻次数
            num_hits = self.skills[skill_index]["duration"] / skill_actual_atk_interval
            
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 1: 绝不罢休
            # 描述: "被动效果...自动开启：攻击范围扩大，攻击力+90%，防御力+60%；
            #       第二次及以后使用时能力加成变为最初的两倍，且持续时间无限"
            # 根据规则，对于可叠加/进化的技能，按最大层数/最终状态计算。
            # 因此，我们考虑第二次及以后使用的状态：攻击力+180%，防御力+120%，持续时间无限。
            # 持续时间: null (无限)
            
            # 计算技能期间的强化攻击力 (90% * 2 = 180%)
            skill_atk_multiplier = 1.0 + (0.90 * 2) # 1.0 + 1.80 = 2.8
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 此技能未提及攻击速度加成，沿用干员基础攻速
            
            # 计算单次普攻的伤害
            dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 永续技能的总伤为0，重点计算DPS
            total_damage = 0 
            dps = dmg_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 2: 无可抵挡
            # 描述: "攻击力+100%，对前方一格持续进行五次溅射范围更大的锤击，
            #       每次造成相当于攻击力240%的物理伤害并使攻击力额外+30%"
            # 持续时间: 27秒
            
            # 技能初始攻击力加成比例 (100%)
            initial_skill_atk_buff_ratio = 1.0 
            # 每次锤击的攻击力倍率 (240%)
            hit_damage_multiplier = 2.40 
            # 每次锤击后攻击力额外增加的比例 (30%)
            additional_atk_buff_per_hit = 0.30 
            # 锤击次数
            num_strikes = 5
            
            total_skill_damage = 0.0
            
            # 遍历计算每次锤击的伤害
            for i in range(num_strikes):
                # 计算当前锤击的攻击力加成：初始100% + (已进行锤击次数 * 额外30%)
                # 例如：
                # 第1次锤击 (i=0): 100% + (0 * 30%) = 100%
                # 第2次锤击 (i=1): 100% + (1 * 30%) = 130%
                # ...
                # 第5次锤击 (i=4): 100% + (4 * 30%) = 220%
                current_total_atk_buff_ratio = initial_skill_atk_buff_ratio + (i * additional_atk_buff_per_hit)
                
                # 计算本次锤击的最终攻击力 (基础攻击力 * (1 + 当前总攻击力加成) * 锤击伤害倍率)
                strike_atk_value = self.final_base_atk * (1 + current_total_atk_buff_ratio) * hit_damage_multiplier
                
                # 计算本次锤击造成的物理伤害
                strike_damage = calculate_physical_damage(strike_atk_value, enemy.current_def)
                
                total_skill_damage += strike_damage
            
            # 技能描述中关于“高台扩散效果”和“伤害效果提升至3.5倍”的部分，
            # 属于天赋的联动效果，且是针对高台单位的，不计入怒潮凛冬自身对单个目标的直接伤害。
            
            total_damage = total_skill_damage
            dps = total_skill_damage / self.skills[skill_index]["duration"]
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)