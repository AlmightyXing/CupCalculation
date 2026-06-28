from backend.function.logic.professions import MechAccordCaster
from backend.function.logic.formulas import calculate_arts_damage

class Vc09澄闪(MechAccordCaster):
    """
    干员：澄闪
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 澄闪的浮游单元攻击同一敌人伤害提升，最高造成干员110%攻击力的伤害。
        # 在计算普攻和技能伤害时，我们直接取这个最高值。
        self.floaty_unit_max_atk_ratio = 1.1 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：信标的愤怒
        # 技能开启后浮游单元攻击时有10%概率自爆（回到干员身边）对小范围敌人造成澄闪300%攻击力的法术伤害
        self.talent_1_proc_chance = 0.1
        self.talent_1_proc_damage_multiplier = 3.0
        
        # 天赋 2：精准导流
        # 自身与浮游单元无视敌人15点法术抗性
        self.res_ignore_ratio = 15
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑精准导流天赋的无视法抗）
        """
        return calculate_arts_damage(atk_val, enemy.current_res, res_ignore_ratio=self.res_ignore_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 澄闪的普攻由浮游单元造成，且攻击同一敌人伤害提升至最高110%攻击力
        # 注意：父类MechAccordCaster的calculate_normal_hit中2.1的系数是本体100% + 浮游单元110%的简化总和。
        # 澄闪的特性描述更倾向于只有浮游单元攻击，且最高110%，因此此处覆写以体现其具体机制。
        atk_val = self.final_base_atk * self.floaty_unit_max_atk_ratio
        return self._calc_arts_hit(atk_val, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 干员基础攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 计算天赋1“信标的愤怒”的期望额外伤害，该伤害基于干员未强化的基础攻击力
        talent_1_proc_base_damage = self._calc_arts_hit(self.final_base_atk * self.talent_1_proc_damage_multiplier, enemy)
        expected_talent_1_damage_per_hit = self.talent_1_proc_chance * talent_1_proc_base_damage

        if skill_index == 0:
            # 技能 1 (火花四溅)：
            # 持续时间 25s
            # 攻击力+40%
            # 攻击速度+50
            duration = 25
            skill_atk_buff_ratio = 1.4 # 攻击力+40%
            skill_attack_speed_bonus = 50
            
            # 计算技能期间浮游单元的实际攻击力 (考虑技能加成和浮游单元110%上限)
            skill_effective_atk = self.final_base_atk * skill_atk_buff_ratio * self.floaty_unit_max_atk_ratio
            
            # 计算技能期间的实际攻击速度和攻击间隔
            skill_effective_attack_speed = self.attack_speed + skill_attack_speed_bonus
            skill_actual_atk_interval = self.attack_interval * 100 / skill_effective_attack_speed
            
            # 单次普攻伤害 (技能加成后)
            damage_per_hit = self._calc_arts_hit(skill_effective_atk, enemy)
            
            # 技能期间总伤害 = (单次普攻伤害 + 天赋1期望伤害) * 攻击次数
            num_hits = duration / skill_actual_atk_interval
            total_damage = num_hits * (damage_per_hit + expected_talent_1_damage_per_hit)
            
            # DPS = (单次普攻伤害 + 天赋1期望伤害) / 技能期间实际攻击间隔
            dps = (damage_per_hit + expected_talent_1_damage_per_hit) / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (电流翻涌)：
            # 持续时间无限 (永续技能)
            # 攻击力+60%
            # 无攻击速度加成，使用干员自身攻速
            skill_atk_buff_ratio = 1.6 # 攻击力+60%
            
            # 计算技能期间浮游单元的实际攻击力 (考虑技能加成和浮游单元110%上限)
            skill_effective_atk = self.final_base_atk * skill_atk_buff_ratio * self.floaty_unit_max_atk_ratio
            
            # 单次普攻伤害 (技能加成后)
            damage_per_hit = self._calc_arts_hit(skill_effective_atk, enemy)
            
            # 永续技能的总伤为0，重点计算DPS
            total_damage = 0
            
            # DPS = (单次普攻伤害 + 天赋1期望伤害) / 实际攻击间隔 (无攻速加成)
            dps = (damage_per_hit + expected_talent_1_damage_per_hit) / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (澄净闪耀)：
            # 持续时间 30s
            # 停止攻击 (指干员自身普攻，但浮游单元继续攻击)
            # 攻击力+80%
            # 无攻击速度加成，使用干员自身攻速
            duration = 30
            skill_atk_buff_ratio = 1.8 # 攻击力+80%
            
            # 计算技能期间浮游单元的实际攻击力 (考虑技能加成和浮游单元110%上限)
            skill_effective_atk = self.final_base_atk * skill_atk_buff_ratio * self.floaty_unit_max_atk_ratio
            
            # 单次普攻伤害 (技能加成后)
            damage_per_hit = self._calc_arts_hit(skill_effective_atk, enemy)
            
            # 技能期间总伤害 = (单次普攻伤害 + 天赋1期望伤害) * 攻击次数
            # 浮游单元的攻击间隔与干员自身攻击间隔一致
            num_hits = duration / actual_atk_interval
            total_damage = num_hits * (damage_per_hit + expected_talent_1_damage_per_hit)
            
            # DPS = (单次普攻伤害 + 天赋1期望伤害) / 实际攻击间隔 (无攻速加成)
            dps = (damage_per_hit + expected_talent_1_damage_per_hit) / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
