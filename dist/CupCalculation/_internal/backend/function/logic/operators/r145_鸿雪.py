from backend.function.logic.professions import HeavyShooter
from backend.function.logic.formulas import calculate_physical_damage

class R145鸿雪(HeavyShooter):
    """
    干员：鸿雪
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：自动打字机 (可使用一个持续25秒的“打字机”，拥有独立的再部署时间)
        # 此天赋描述了打字机的存在，其直接影响体现在天赋2的防御力下降效果上。
        
        # 天赋 2：弱点速记 (打字机的攻击会使命中目标的防御力下降18%；若打字机放在鸿雪周围四格则效果提升至23%)
        # 根据规则，天赋对提高伤害有帮助的均纳入考虑，且可叠加层数按最大层数叠加。
        # 因此，我们假设打字机放置在鸿雪周围四格，提供23%的防御力下降效果。
        self.typewriter_def_reduction_ratio = 0.23
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑打字机天赋的防御力下降）
        """
        # 敌人实际防御力 = 敌人当前防御力 * (1 - 打字机防御力下降比例)
        effective_def = enemy.current_def * (1 - self.typewriter_def_reduction_ratio)
        
        # 确保防御力不为负值
        effective_def = max(0, effective_def)
        
        return calculate_physical_damage(atk_val, effective_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望伤害，考虑打字机天赋的防御力下降。
        """
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员的基础实际攻击间隔（不受技能影响）
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (抑扬格)：攻击力+60%，攻击时，40%几率当次攻击的攻击力提升至225%
            # 永续技能 (duration: null)，total_damage为0，重点计算dps。
            
            # 技能提供的基础攻击力加成
            skill_base_atk_multiplier = 1.0 + 0.60
            
            # 40%几率提升至225%的期望倍率计算
            # 期望倍率 = (1 - 0.4) * 1 (不触发时为100%) + 0.4 * 2.25 (触发时为225%)
            expected_proc_multiplier = (0.6 * 1.0) + (0.4 * 2.25) # 0.6 + 0.9 = 1.5
            
            # 最终每次攻击的期望攻击力倍率
            final_expected_atk_multiplier = skill_base_atk_multiplier * expected_proc_multiplier
            
            atk_val = self.final_base_atk * final_expected_atk_multiplier
            
            damage_per_hit = self._calc_hit(atk_val, enemy)
            
            # 永续技能，总伤为0，DPS为单次命中伤害 / 基础实际攻击间隔
            return {"total_damage": 0, "dps": damage_per_hit / base_actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (点题)：立即对前方进行3次攻击，每次造成自身攻击力230%的物理伤害
            # 瞬发伤害技能。被动效果不影响鸿雪自身伤害，不纳入计算。
            
            atk_multiplier = 2.30
            num_hits = 3
            
            atk_val = self.final_base_atk * atk_multiplier
            
            damage_per_hit = self._calc_hit(atk_val, enemy)
            total_damage = damage_per_hit * num_hits
            
            # 瞬发技能的DPS计算方式，通常是总伤 / 普攻间隔
            return {"total_damage": total_damage, "dps": total_damage / base_actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (锐笔速写)：攻击范围扩大，攻击间隔缩短(-0.6)，每次攻击的攻击力提升至200%（对正前方3格提升至255%）
            # 增益类技能，持续30秒。
            
            skill_duration = 30
            
            # 攻击间隔缩短
            skill_attack_interval_raw = self.attack_interval - 0.6
            # 确保攻击间隔不为负或零，设置一个最小值
            skill_attack_interval = max(0.1, skill_attack_interval_raw) 
            
            # 技能期间的实际攻击间隔
            skill_actual_atk_interval = skill_attack_interval * 100 / self.attack_speed
            
            # 攻击力提升，根据规则，取最大值255%（假设目标在正前方3格）
            skill_atk_multiplier = 2.55
            
            atk_val = self.final_base_atk * skill_atk_multiplier
            
            damage_per_hit = self._calc_hit(atk_val, enemy)
            
            # 技能持续期间能打出的普攻次数
            num_hits_during_skill = skill_duration / skill_actual_atk_interval
            
            total_damage = damage_per_hit * num_hits_during_skill
            dps = damage_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)