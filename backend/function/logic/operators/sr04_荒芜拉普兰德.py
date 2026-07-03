from backend.function.logic.professions import MechAccordCaster
from backend.function.logic.formulas import calculate_arts_damage

class Sr04荒芜拉普兰德(MechAccordCaster):
    """
    干员：荒芜拉普兰德
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化浮游单元的基础属性
        # 浮游单元基础数量 (从角色描述“操作浮游单元”推断为1)
        self.floating_unit_count = 1 
        # 浮游单元伤害上限比例 (从角色描述“最高造成干员110%攻击力的伤害”得出)
        self.floating_unit_damage_cap_ratio = 1.1 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：头狼 (Head Wolf)
        # "每在场上停留20秒，浮游单元依次获得以下一个效果：伤害上限提高10%、造成伤害时使目标特殊能力失效2秒、数量+1"
        # 根据规则，我们取对伤害提升最大的效果。
        # 伤害上限提高10%：在原有110%基础上增加10%，变为120%
        self.floating_unit_damage_cap_ratio += 0.1 
        # 数量+1：在原有基础上增加1个浮游单元
        self.floating_unit_count += 1 

        # 技能 1 被动效果：慵怠者悲鸣 (Sloth's Lament)
        # "被动效果：浮游单元+1"
        # 这是一个技能的被动效果，但它永久生效，因此也影响普攻时的浮游单元数量。
        # 普攻时总浮游单元数量：1 (基础) + 1 (天赋) + 1 (S1被动) = 3个
        self.floating_unit_count += 1 

        # 天赋 2：叙拉古的荣幸 (Syracuse's Honor)
        # "编入队伍时所有【叙拉古】干员的初始技力+5"
        # 此天赋为队伍技力加成，不直接影响荒芜拉普兰德自身的伤害计算，故在此处忽略。

    def _calc_arts_hit_per_unit(self, atk_val: float, enemy) -> float:
        """
        计算单个浮游单元命中时的期望法术伤害。
        浮游单元攻击同一敌人伤害提升（最高造成干员X%攻击力的伤害），
        这里假设每次命中都已达到伤害上限。
        """
        unit_effective_atk = atk_val * self.floating_unit_damage_cap_ratio
        return calculate_arts_damage(unit_effective_atk, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 荒芜拉普兰德的普攻由浮游单元造成法术伤害。
        # 普攻时，浮游单元数量为 self.floating_unit_count (已包含天赋和S1被动)。
        # 父类MechAccordCaster的calculate_normal_hit是简化计算，这里提供更详细的计算。
        single_unit_damage = self._calc_arts_hit_per_unit(self.final_base_atk, enemy)
        total_damage = self.floating_unit_count * single_unit_damage
        return total_damage

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 技能期间的基础浮游单元数量，包含天赋和S1被动
        current_floating_unit_count = self.floating_unit_count
        
        if skill_index == 0:
            # 技能 1 (慵怠者悲鸣 - Sloth's Lament)
            # "被动效果：浮游单元+1" (已在 apply_talents 中处理)
            # "主动触发可以在下列状态和初始状态间切换：攻击力+35%，释放浮游单元随机锁定整个战场内的非移动敌人进行攻击..."
            # 这是一个永续技能（duration=null），主要计算DPS。
            
            atk_multiplier = 1.35 # 攻击力+35%
            skill_atk = self.final_base_atk * atk_multiplier
            
            # 计算所有浮游单元单次攻击的总伤害
            single_unit_damage = self._calc_arts_hit_per_unit(skill_atk, enemy)
            total_hit_damage = current_floating_unit_count * single_unit_damage
            
            # 永续技能的总伤为0，重点是DPS
            return {"total_damage": 0, "dps": total_hit_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (逐猎狂飙 - Chasing Frenzy)
            # duration = 22
            # "浮游单元+3，攻击范围扩大，攻击力+120%，释放浮游单元随机锁定敌人攻击..."
            
            duration = 22
            
            # 技能期间的浮游单元数量
            skill_floating_unit_count = current_floating_unit_count + 3
            atk_multiplier = 2.2 # 攻击力+120% (1 + 1.20)
            skill_atk = self.final_base_atk * atk_multiplier
            
            # 计算所有浮游单元单次攻击的总伤害
            single_unit_damage = self._calc_arts_hit_per_unit(skill_atk, enemy)
            total_hit_damage = skill_floating_unit_count * single_unit_damage
            
            # 计算技能持续期间的总伤害
            num_hits = (duration or 0) / actual_atk_interval
            total_damage = num_hits * total_hit_damage
            
            return {"total_damage": total_damage, "dps": total_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (终幕·浩劫 - Finale: Cataclysm)
            # duration = 40
            # "浮游单元+2，攻击力+80%，释放特殊形态的浮游单元散开后在整个战场范围各自追逐较近的敌人..."
            # "浮游单元周围的敌人移动速度-50%且每秒受到相当于攻击力120%的法术伤害（不叠加）"
            
            duration = 40
            
            # 技能期间的浮游单元数量
            skill_floating_unit_count = current_floating_unit_count + 2
            atk_multiplier = 1.8 # 攻击力+80% (1 + 0.80)
            skill_atk = self.final_base_atk * atk_multiplier
            
            # --- 1. 来自浮游单元攻击的伤害 ---
            # 浮游单元的每次攻击伤害
            single_unit_attack_damage = self._calc_arts_hit_per_unit(skill_atk, enemy)
            # 所有浮游单元单次攻击的总伤害
            total_attack_damage_per_hit = skill_floating_unit_count * single_unit_attack_damage
            
            # 技能持续期间的总攻击伤害
            num_hits = (duration or 0) / actual_atk_interval
            total_attack_damage_over_duration = num_hits * total_attack_damage_per_hit
            
            # --- 2. 来自浮游单元AoE DoT的伤害 ---
            # "每秒受到相当于攻击力120%的法术伤害（不叠加）"
            # 根据规则“严禁在代码中乘以任何目标数”，且“不叠加”意味着单个敌人只受一次DoT。
            # 因此，我们计算单个目标受到的DoT伤害，假设它处于一个浮游单元的AoE范围内。
            dot_atk_ratio = 1.2 # 攻击力120%
            dot_atk_value = skill_atk * dot_atk_ratio
            
            # 单个目标每秒受到的DoT伤害
            dot_damage_per_second = calculate_arts_damage(dot_atk_value, enemy.current_res)
            # 技能持续期间的总DoT伤害
            total_dot_damage_over_duration = dot_damage_per_second * duration
            
            # 总伤害是攻击伤害和DoT伤害之和
            total_damage = total_attack_damage_over_duration + total_dot_damage_over_duration
            
            # DPS是总伤害除以持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
