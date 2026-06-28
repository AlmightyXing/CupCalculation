from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_arts_damage

class Re10电弧(UnknownProfession):
    """
    干员：电弧
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：卡带里的灵感 (召唤物数量和功能)
        # 此天赋主要影响召唤物，不直接修改电弧自身的攻击力、攻速等属性，因此不影响电弧自身的伤害计算。
        
        # 天赋 2：加油~ (召唤物属性加成)
        # 此天赋影响召唤物的属性，不直接修改电弧自身的攻击力、攻速等属性，因此不影响电弧自身的伤害计算。
        # 根据规则，只考虑对提高干员自身伤害有帮助的天赋。
        pass
        
    def _calc_arts_hit(self, atk_val: float, enemy_res: float, res_ignore_ratio: float = 0.0) -> float:
        """
        计算单次命中时的期望法术伤害
        """
        return calculate_arts_damage(atk_val, enemy_res, res_ignore_ratio=res_ignore_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 电弧的攻击造成法术伤害
        return self._calc_arts_hit(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (律动线): 防御性技能，不直接增加电弧自身的伤害。
            # 描述："自身和召唤物防御力+80%并获得100%最大生命值的屏障，持续至技能结束"
            # 描述："技能开启时获得1个召唤物"
            # 技能持续期间，电弧的普攻伤害不变，且无瞬发伤害。
            
            # 计算技能期间的普攻DPS
            normal_hit_damage = self._calc_arts_hit(self.final_base_atk, enemy.current_res)
            dps = normal_hit_damage / actual_atk_interval
            
            # 对于有持续时间但无伤害爆发或伤害加成的技能，总伤为0。
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (环形鳞地): 攻击力增益技能。
            # 描述："自身和召唤物攻击力+80%"
            # 持续时间: 25秒
            
            # 应用攻击力加成
            enhanced_atk = self.final_base_atk * (1 + 0.80)
            
            # 计算强化后的单次普攻伤害
            enhanced_single_hit_damage = self._calc_arts_hit(enhanced_atk, enemy.current_res)
            
            # 计算技能持续期间的攻击次数
            duration = 25
            num_attacks = duration / actual_atk_interval
            
            total_damage = num_attacks * enhanced_single_hit_damage
            dps = enhanced_single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (手牵手): 攻击力增益与法术脆弱技能。
            # 描述："自身和召唤物攻击力+150%，对敌人造成伤害时，使敌人受到停顿与35％法术脆弱效果"
            # 持续时间: 30秒
            
            # 应用攻击力加成
            enhanced_atk = self.final_base_atk * (1 + 1.50)
            
            # 应用法术脆弱效果 (35%法术脆弱意味着敌人受到的法术伤害提高35%，等同于敌人法术抗性降低35%)
            effective_enemy_res = enemy.current_res * (1 - 0.35)
            
            # 计算强化后的单次普攻伤害 (考虑法术脆弱)
            enhanced_single_hit_damage = self._calc_arts_hit(enhanced_atk, effective_enemy_res)
            
            # 计算技能持续期间的攻击次数
            duration = 30
            num_attacks = duration / actual_atk_interval
            
            total_damage = num_attacks * enhanced_single_hit_damage
            dps = enhanced_single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)