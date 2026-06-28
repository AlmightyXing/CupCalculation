from backend.function.logic.professions import Thrower
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Re45迷迭香(Thrower):
    """
    干员：迷迭香
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：歼灭战装备 (攻击无视目标160防御力)
        self.flat_def_ignore = 160
        
        # 天赋 2：感知稳定 (部署后随机选择一名在场的【术师】干员，自身和其的攻击力+8%)
        # 只要天赋对提高伤害有帮助，均纳入考虑！
        self.final_base_atk *= (1 + 0.08)
        
    def _calc_physical_hit(self, atk_val: float, enemy, additional_def_ignore: float = 0) -> float:
        """
        计算单次命中时的期望物理伤害（考虑歼灭战装备天赋的无视防御力）
        """
        # 总的无视防御力 = 天赋自带 + 技能额外提供的
        total_def_ignore = self.flat_def_ignore + additional_def_ignore
        
        return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_flat=total_def_ignore)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻：对小范围的地面敌人造成两次物理伤害（第一次为正常伤害，第二次为余震，伤害降低至攻击力的一半）
        main_hit_damage = self._calc_physical_hit(self.final_base_atk, enemy)
        aftershock_damage = self._calc_physical_hit(self.final_base_atk * 0.5, enemy)
        
        return main_hit_damage + aftershock_damage

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取基础实际攻击间隔
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (思维膨大)：下次攻击额外造成一次相当于攻击力180%的法术伤害
            # 这是普攻触发的额外伤害，因此总伤包含普攻的物理伤害和额外的法术伤害。
            
            # 普攻物理伤害部分
            normal_physical_damage = self.calculate_normal_hit(enemy)
            
            # 额外法术伤害部分
            arts_atk_val = self.final_base_atk * 1.8
            arts_damage = calculate_arts_damage(arts_atk_val, enemy.current_res)
            
            total_damage = normal_physical_damage + arts_damage
            return {"total_damage": total_damage, "dps": total_damage / base_actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (末梢阻断)：
            # 攻击间隔增大(+50%)
            # 攻击力+55%
            # 每次攻击额外造成2次余震 (总共 1次主攻 + 1次原余震 + 2次额外余震 = 1次主攻 + 3次余震)
            
            skill_duration = 40
            
            # 攻击间隔调整
            skill_atk_interval_multiplier = 1.5 # 攻击间隔增大50%
            skill_actual_atk_interval = self.attack_interval * skill_atk_interval_multiplier * 100 / self.attack_speed
            
            # 攻击力调整
            skill_atk_multiplier = 1.55 # 攻击力+55%
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次强化普攻的伤害
            # 1次主攻
            main_hit_damage = self._calc_physical_hit(enhanced_atk, enemy)
            # 3次余震 (每次攻击力一半)
            aftershock_damage_per_hit = self._calc_physical_hit(enhanced_atk * 0.5, enemy) * 3
            
            damage_per_enhanced_attack = main_hit_damage + aftershock_damage_per_hit
            
            # 计算技能期间总伤
            hits_during_skill = skill_duration / skill_actual_atk_interval
            total_damage = hits_during_skill * damage_per_enhanced_attack
            
            return {"total_damage": total_damage, "dps": damage_per_enhanced_attack / skill_actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (“如你所愿”)：
            # 攻击间隔缩短(-50%)
            # 攻击力+75%
            # 立即部署战术装备（阻挡的敌人防御力-160）
            
            skill_duration = 30
            
            # 攻击间隔调整
            skill_atk_interval_multiplier = 0.5 # 攻击间隔缩短50%
            skill_actual_atk_interval = self.attack_interval * skill_atk_interval_multiplier * 100 / self.attack_speed
            
            # 攻击力调整
            skill_atk_multiplier = 1.75 # 攻击力+75%
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 战术装备带来的额外防御力降低，这会影响后续的普攻伤害计算
            tactical_equipment_def_reduction = 160
            
            # 计算单次强化普攻的伤害
            # 1次主攻
            main_hit_damage = self._calc_physical_hit(enhanced_atk, enemy, additional_def_ignore=tactical_equipment_def_reduction)
            # 1次余震 (每次攻击力一半)
            aftershock_damage_per_hit = self._calc_physical_hit(enhanced_atk * 0.5, enemy, additional_def_ignore=tactical_equipment_def_reduction)
            
            damage_per_enhanced_attack = main_hit_damage + aftershock_damage_per_hit
            
            # 计算技能期间总伤
            # 立即部署战术装备不造成直接伤害，但其效果影响后续普攻。
            hits_during_skill = skill_duration / skill_actual_atk_interval
            total_damage = hits_during_skill * damage_per_enhanced_attack
            
            return {"total_damage": total_damage, "dps": damage_per_enhanced_attack / skill_actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)