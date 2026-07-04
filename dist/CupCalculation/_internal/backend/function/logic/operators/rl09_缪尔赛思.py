from backend.function.logic.professions import Tactician
from backend.function.logic.formulas import calculate_physical_damage

class Rl09缪尔赛思(Tactician):
    """
    干员：缪尔赛思
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        # 假设 self.base_atk 由 super().__init__(data) 设置
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：净水即生命
        # 描述：可召唤流形来复制待部署干员的大部分（90%）属性...
        # 角色特性补充：自身攻击援军阻挡的敌人时攻击力提升至150%
        # 此特性与父类Tactician的职业特性相同，已由父类处理，无需在此重复设置。
        # 在计算缪尔赛思自身的伤害时，我们假设敌人被援军阻挡，以计算最大期望伤害。
        
        # 天赋 2：开源节流
        # 描述：携带时【莱茵生命】干员部署费用-2，首名【莱茵生命】干员部署费用额外-1
        # 此天赋不影响缪尔赛思自身的战斗属性或伤害输出，因此在伤害计算中忽略。
        pass # 移除冗余的 self.atk_boost_on_blocked_enemy 属性，因为它与父类特性重复

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 缪尔赛思的“攻击援军阻挡的敌人时攻击力提升至150%”是其职业特性，已由父类Tactician实现。
        # 直接调用父类的普攻计算方法即可，父类已包含150%的攻击力提升。
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算技能期间的普攻次数和DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 技能期间的攻击力加成（所有技能都有 "自身与流形攻击力+50%"）
        skill_atk_multiplier = 1.5 # 1 + 0.5
        
        # 考虑攻击援军阻挡的敌人时的攻击力提升 (150%)，这是Tactician的职业特性。
        # 技能期间的最终攻击力 = (基础攻击力 * 职业特性倍率) * 技能攻击力倍率
        # 职业特性倍率 (1.5) 应首先应用于基础攻击力，然后乘以技能的攻击力倍率。
        base_skill_atk = self.final_base_atk * 1.5 * skill_atk_multiplier
        
        if skill_index == 0:
            # 技能 1 (渐进性润化)：
            # 描述：期间逐渐回复13点费用，自身与流形攻击力+50%，攻击速度+50
            
            # 攻击速度加成
            buffed_attack_speed = self.attack_speed + 50
            buffed_actual_atk_interval = self.attack_interval * 100 / buffed_attack_speed
            
            # 技能持续时间
            duration = 15
            
            # 计算单次强化普攻伤害
            damage_per_hit = calculate_physical_damage(base_skill_atk, enemy.current_def)
            
            # 计算技能期间的普攻次数
            hits_during_skill = duration / buffed_actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / buffed_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (生态耦合)：
            # 描述：立即获得15点费用，自身与流形攻击力+50%，若流形为近战复制体时...若为远程复制体时，攻击变为二连击...
            # 注意：二连击是流形（复制体）的攻击效果，不影响缪尔赛思自身的攻击。
            # 缪尔赛思自身仅获得攻击力加成。
            
            # 技能持续时间
            duration = 15
            
            # 计算单次强化普攻伤害
            damage_per_hit = calculate_physical_damage(base_skill_atk, enemy.current_def)
            
            # 计算技能期间的普攻次数 (使用缪尔赛思自身的攻击间隔，因为没有攻速加成)
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (浅层非熵适应)：
            # 描述：立即获得15点费用，自身与流形攻击力+50%，若流形为近战复制体时每2秒对周围八格敌人...若为远程复制体时刷新所有流形且攻击附带持续1.5秒的束缚
            # 注意：这些都是流形（复制体）的效果或控制效果，不影响缪尔赛思自身的攻击。
            # 缪尔赛思自身仅获得攻击力加成。
            
            # 技能持续时间
            duration = 15
            
            # 计算单次强化普攻伤害
            damage_per_hit = calculate_physical_damage(base_skill_atk, enemy.current_def)
            
            # 计算技能期间的普攻次数 (使用缪尔赛思自身的攻击间隔，因为没有攻速加成)
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * damage_per_hit
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count) # Fallback to super if skill_index not handled
