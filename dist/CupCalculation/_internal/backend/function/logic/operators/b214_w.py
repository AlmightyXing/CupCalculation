from backend.function.logic.professions import Artilleryman
from backend.function.logic.formulas import calculate_physical_damage

class B214W(Artilleryman):
    """
    干员：W
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.stun_damage_bonus = 0.0 # 对眩晕敌人的伤害加成
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：设伏 (在战场停留10秒后获得60%的物理和法术闪避，且不容易成为敌人的攻击目标)
        # 此天赋提供闪避和降低仇恨，不直接增加伤害，因此不纳入伤害计算。
        
        # 天赋 2：落井下石 (攻击范围内的敌人在被晕眩时受到的物理伤害+18%)
        # 此天赋增加对眩晕敌人的伤害。
        self.stun_damage_bonus = 0.18
        
    def _calc_hit(self, atk_val: float, enemy, is_enemy_stunned: bool = False) -> float:
        """
        计算单次命中时的期望物理伤害，考虑对眩晕敌人的伤害加成。
        """
        damage_multiplier = 1.0
        if is_enemy_stunned:
            damage_multiplier += self.stun_damage_bonus
        
        return calculate_physical_damage(atk_val * damage_multiplier, enemy.current_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # W的普攻造成群体物理伤害，但 calculate_normal_hit 方法通常计算单次命中对单个目标的伤害。
        # Artilleryman 父类特性是群体伤害，但没有额外的伤害倍率，因此无需 super() 调用来叠加倍率。
        # 普攻本身不附带眩晕，因此不享受“落井下石”天赋加成。
        return self._calc_hit(self.final_base_atk, enemy, is_enemy_stunned=False)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (红桃K)：立即发射一枚榴弹，造成相当于攻击力350%的物理伤害，并使命中目标晕眩3秒
            # 这是一个瞬发伤害技能。伤害发生时，目标尚未被此技能眩晕，因此不享受“落井下石”加成。
            atk_val = self.final_base_atk * 3.5
            total_damage = self._calc_hit(atk_val, enemy, is_enemy_stunned=False)
            # DPS计算对于瞬发技能可能需要考虑技能CD，此处沿用原逻辑
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (惊吓盒子)：下次攻击变为在攻击范围内的一个可放置地块埋下地雷（持续120秒）；
            # 地雷在敌人经过时会爆炸，爆炸后对周围所有敌人造成相当于攻击力280%的物理伤害并令其晕眩2.2秒
            # 这是一个瞬发伤害技能（地雷爆炸）。伤害发生时，目标尚未被此技能眩晕，因此不享受“落井下石”加成。
            atk_val = self.final_base_atk * 2.8
            total_damage = self._calc_hit(atk_val, enemy, is_enemy_stunned=False)
            # DPS计算对于瞬发技能可能需要考虑技能CD，此处沿用原逻辑
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (D12)：在攻击范围内生命值最多的4个敌人身上放置一枚炸弹；
            # 炸弹会在一定延迟后引爆，每个对其周围的所有敌人造成相当于攻击力310%的物理伤害并令其晕眩5秒
            # 这是一个瞬发伤害技能（炸弹引爆）。伤害发生时，目标尚未被此技能眩晕，因此不享受“落井下石”加成。
            # 严格按照规则，只计算单个炸弹对单个目标的伤害，不乘以目标数。
            atk_val = self.final_base_atk * 3.1
            total_damage = self._calc_hit(atk_val, enemy, is_enemy_stunned=False)
            # DPS计算对于瞬发技能可能需要考虑技能CD，此处沿用原逻辑
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
