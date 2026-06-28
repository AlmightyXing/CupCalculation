from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_physical_damage

class Uss4早露(UnknownProfession):
    """
    干员：早露
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：深入骨髓 (攻击重量较重（重量等级大于等于3）的敌人时，无视其防御力的60%)
        self.talent_ignore_def_ratio = 0.6
        self.talent_weight_threshold = 3 # 重量等级阈值
        
        # 天赋 2：学生楷模 (编入队伍时，所有【乌萨斯学生自治团】干员攻击力+8%)
        # 此天赋为光环效果，影响其他【乌萨斯学生自治团】干员，不直接提高早露自身的伤害。
        # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑！”，此天赋不直接提高早露自身伤害，故在此处不作处理。
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑深入骨髓天赋的无视防御条件）
        """
        # 检查敌人重量等级是否满足天赋条件
        if hasattr(enemy, 'weight_level') and enemy.weight_level >= self.talent_weight_threshold:
            return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.talent_ignore_def_ratio)
        else:
            return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=0.0)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻直接调用内部的 _calc_hit 方法，处理天赋的条件无视防御
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算技能期间的普攻次数和DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (攻击力强化·γ型)：攻击力+100%，持续30秒
            skill_duration = 30
            skill_atk_multiplier = 1 + 1.00 # 攻击力+100%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能持续期间能打出的普攻次数
            hits_during_skill = skill_duration / actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 总伤害 = 普攻次数 * 单次强化普攻伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # DPS = 单次强化普攻伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (分裂射击)：攻击力+90%，可以额外攻击一个敌人，持续60秒
            # "可以额外攻击一个敌人" 属于群体攻击描述，根据规则，严禁在代码中乘以任何目标数。
            skill_duration = 60
            skill_atk_multiplier = 1 + 0.90 # 攻击力+90%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能持续期间能打出的普攻次数
            hits_during_skill = skill_duration / actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 总伤害 = 普攻次数 * 单次强化普攻伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # DPS = 单次强化普攻伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (雪崩击)：攻击力+25%，立即向至多4个重量最重的敌人发射束缚叉枪；
            # 技能持续时间内所有目标受到束缚效果，每秒受到一次攻击，持续8秒
            skill_duration = 8
            skill_atk_multiplier = 1 + 0.25 # 攻击力+25%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # "立即向至多4个重量最重的敌人发射束缚叉枪" 视为技能触发效果，不单独计算伤害。
            # 伤害来源是 "每秒受到一次攻击"。
            
            # 技能持续期间的攻击次数 (每秒一次攻击，持续8秒，即攻击8次)
            hits_during_skill = skill_duration 
            
            # 计算单次攻击的伤害（使用强化后的攻击力）
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 总伤害 = 攻击次数 * 单次攻击伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # DPS = 单次攻击伤害 / 1.0 (因为是每秒一次攻击，攻击间隔为1秒)
            dps = single_hit_damage / 1.0
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果技能索引不匹配，调用基类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)