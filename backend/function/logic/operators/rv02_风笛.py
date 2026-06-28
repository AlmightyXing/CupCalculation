from backend.function.logic.professions import Vanguard
from backend.function.logic.formulas import calculate_physical_damage

class Rv02风笛(Vanguard):
    """
    干员：风笛
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：精密填弹 (每次攻击有25%的概率攻击力提升至130%，且额外攻击一个目标)
        # "额外攻击一个目标" 在单目标伤害计算中，意味着如果天赋触发，该次攻击对单个目标造成双倍伤害。
        self.talent1_prob = 0.25
        self.talent1_atk_multiplier = 1.30
        
        # 天赋 2：军事传统 (编入队伍时所有【先锋】干员的初始技力+6)
        # 此天赋不直接影响风笛自身的伤害或面板，因此不在此处实现。
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑精密填弹天赋的概率触发和额外攻击）
        """
        # 天赋触发时：攻击力提升至130%，且额外攻击一个目标 (视为造成2次130%攻击力的伤害)
        dmg_on_proc_single_hit = calculate_physical_damage(atk_val * self.talent1_atk_multiplier, enemy.current_def)
        dmg_on_proc_total = dmg_on_proc_single_hit * 2 # "额外攻击一个目标" 视为对单目标造成双倍伤害
        
        # 天赋未触发时：正常攻击
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 期望伤害 = 触发概率 * 触发伤害 + (1 - 触发概率) * 未触发伤害
        return self.talent1_prob * dmg_on_proc_total + (1 - self.talent1_prob) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (迅捷打击·γ型)：攻击力+45%，攻击速度+45，持续35秒
            skill_atk_multiplier = 1.45 # 1 + 0.45
            skill_atk_speed_bonus = 45
            skill_duration = 35
            
            # 技能期间的强化攻击力
            buffed_atk = self.final_base_atk * skill_atk_multiplier
            # 技能期间的强化攻击速度
            buffed_atk_speed = self.attack_speed + skill_atk_speed_bonus
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = self.attack_interval * 100 / buffed_atk_speed
            
            # 计算技能期间的攻击次数
            num_hits = skill_duration / skill_actual_atk_interval
            
            # 计算单次攻击的期望伤害（已考虑天赋）
            dmg_per_hit = self._calc_hit(buffed_atk, enemy)
            
            total_damage = num_hits * dmg_per_hit
            dps = dmg_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (高效冲击)：下一次的攻击力提升至200%，且额外攻击一次，可充能3次
            # 瞬发伤害技能，计算单次爆发伤害
            skill_atk_multiplier = 2.0
            
            # 技能强化后的攻击力
            skill_buffed_atk = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次攻击的期望伤害（已考虑天赋），然后乘以技能的“额外攻击一次”
            # 注意：_calc_hit 已经包含了天赋触发时的“额外攻击一个目标”逻辑
            # 这里的“额外攻击一次”是技能本身的特性，意味着技能触发时会造成两次伤害判定
            # 每次伤害判定都会独立触发天赋
            dmg_per_hit_instance = self._calc_hit(skill_buffed_atk, enemy)
            
            total_damage = dmg_per_hit_instance * 2 # 技能描述中的“额外攻击一次”
            dps = total_damage / actual_atk_interval # 瞬发技能的DPS计算方式
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (闭膛连发)：攻击间隔增大(+70%)，阻挡数+1，攻击力和防御力+120%，攻击变为三连击，持续20秒
            skill_duration = 20
            skill_atk_multiplier = 2.20 # 1 + 1.20
            attack_interval_increase_ratio = 0.70
            
            # 技能期间的强化攻击力
            buffed_atk = self.final_base_atk * skill_atk_multiplier
            
            # 攻击间隔增大
            modified_attack_interval = self.attack_interval * (1 + attack_interval_increase_ratio)
            
            # 技能期间的实际攻击间隔 (攻击速度未变，但基础攻击间隔变了)
            skill_actual_atk_interval = modified_attack_interval * 100 / self.attack_speed
            
            # 技能期间的攻击次数 (指攻击动作的次数)
            num_attack_actions = skill_duration / skill_actual_atk_interval
            
            # 每次攻击变为三连击
            hits_per_action = 3
            
            # 计算单次连击的期望伤害（已考虑天赋）
            dmg_per_single_hit = self._calc_hit(buffed_atk, enemy)
            
            total_damage = num_attack_actions * hits_per_action * dmg_per_single_hit
            dps = (hits_per_action * dmg_per_single_hit) / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)