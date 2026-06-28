from backend.function.logic.professions import Liberator
from backend.function.logic.formulas import calculate_physical_damage

class Kz08玛恩纳(Liberator):
    """
    干员：玛恩纳
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 解放者特性：技能未开启时40秒内攻击力逐渐提升至最高+200%。
        # 在计算伤害时，我们假设此特性已达到最大值。
        self.liberator_char_atk_multiplier = 1.0 + 2.0 # +200% ATK
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：游侠 (Ranger)
        # "攻击敌人时攻击力提升至110%。周围存在3名及以上敌人时改为提升至115%"
        self.talent_atk_multiplier_normal = 1.10
        self.talent_atk_multiplier_crowd = 1.15
        # "受到的伤害减少15%" - 此为受击减伤，不影响自身输出，故不纳入伤害计算。
        
        # 天赋 2：无动于衷 (Indifferent)
        # "在场时，自身嘲讽等级1，所有卡西米尔干员被攻击时反弹相当于玛恩纳攻击力15%的真实伤害"
        # 嘲讽等级和反弹真实伤害不属于玛恩纳自身的直接输出，故不纳入伤害计算。
        
    def _calc_hit(self, base_atk_val: float, enemy, target_count: int = 1) -> float:
        """
        计算单次命中时的期望物理伤害，考虑游侠天赋的攻击力加成。
        base_atk_val 应该已经包含了干员基础攻击力、信赖、以及解放者特性加成。
        """
        talent_multiplier = self.talent_atk_multiplier_normal
        if target_count >= 3:
            talent_multiplier = self.talent_atk_multiplier_crowd
            
        final_atk_for_hit = base_atk_val * talent_multiplier
        return calculate_physical_damage(final_atk_for_hit, enemy.current_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 解放者特性：通常不攻击。因此普攻伤害为0。
        # 玛恩纳的伤害主要通过技能体现。
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 基础实际攻击间隔，用于计算技能期间的攻击次数
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 技能期间解放者特性攻击力倍率 (默认为+200%)
        skill_liberator_char_atk_multiplier = self.liberator_char_atk_multiplier

        if skill_index == 0:
            # 技能 1 (未声张的怒火)：
            # "攻击造成相当于200%攻击力的物理伤害，防御力+60%"
            # 持续时间: 30 秒
            
            skill_duration = 30
            skill_atk_multiplier = 2.0
            
            # 计算包含解放者特性和技能倍率的攻击力
            atk_val = self.final_base_atk * skill_liberator_char_atk_multiplier * skill_atk_multiplier
            
            # 计算单次命中伤害
            single_hit_damage = self._calc_hit(atk_val, enemy, target_count)
            
            # 计算技能持续期间的攻击次数
            num_hits = skill_duration / base_actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (未宽解的悲哀)：
            # "攻击间隔延长(+0.3)，攻击范围扩大，攻击造成相当于190%攻击力的二连击。"
            # 持续时间: 20 秒
            
            skill_duration = 20
            skill_atk_multiplier = 1.9
            num_consecutive_hits = 2 # 二连击
            
            # 应用攻击间隔延长
            modified_attack_interval = self.attack_interval + 0.3
            actual_atk_interval = modified_attack_interval * 100 / self.attack_speed
            
            # 计算包含解放者特性和技能倍率的攻击力
            atk_val = self.final_base_atk * skill_liberator_char_atk_multiplier * skill_atk_multiplier
            
            # 计算单次攻击（包含二连击）的总伤害
            single_attack_instance_damage = self._calc_hit(atk_val, enemy, target_count) * num_consecutive_hits
            
            # 计算技能持续期间的攻击次数
            num_attack_instances = skill_duration / actual_atk_interval
            
            total_damage = num_attack_instances * single_attack_instance_damage
            dps = single_attack_instance_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (未照耀的荣光)：
            # "攻击范围扩大，特性提升至2倍（每击倒一名敌人时特性倍率-10%），攻击对5个目标造成相当于180%攻击力的物理伤害。"
            # 持续时间: 28 秒
            
            skill_duration = 28
            skill_atk_multiplier = 1.8
            
            # "特性提升至2倍" - 解放者特性变为 +400% ATK
            # "每击倒一名敌人时特性倍率-10%" - 为计算最大伤害，假设技能期间没有敌人被击倒。
            skill_liberator_char_atk_multiplier = 1.0 + 4.0 # +400% ATK
            
            # "攻击对5个目标造成..." - 根据规则，严禁将最终伤害乘以目标数，故忽略此描述。
            # "范围内所有敌人受到卡西米尔干员攻击时额外附带玛恩纳12%攻击力的真实伤害" - 此为其他干员攻击时触发的额外伤害，不属于玛恩纳自身的直接输出，故不纳入伤害计算。
            
            # 计算包含强化解放者特性和技能倍率的攻击力
            atk_val = self.final_base_atk * skill_liberator_char_atk_multiplier * skill_atk_multiplier
            
            # 计算单次命中伤害
            single_hit_damage = self._calc_hit(atk_val, enemy, target_count)
            
            # 计算技能持续期间的攻击次数
            num_hits = skill_duration / base_actual_atk_interval
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
