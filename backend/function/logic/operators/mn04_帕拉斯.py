from backend.function.logic.professions import Instructor
from backend.function.logic.formulas import calculate_physical_damage

class Mn04帕拉斯(Instructor):
    """
    干员：帕拉斯
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 教官职业特性：攻击自身未阻挡的敌人时攻击力提升至120%
        # 这是一个最终乘区，在伤害计算时应用
        self.unblocked_atk_multiplier = 1.2 
        
        self.apply_talents() # 在基础攻击力确定后应用天赋
        
    def apply_talents(self):
        # 天赋 1：英雄的诞生
        # "在场时，所有【米诺斯】干员生命值高于80%时获得+25%攻击力的精力充沛"
        # 假设帕拉斯自身是【米诺斯】干员，且生命值高于80%，以计算最大伤害。
        # 此为攻击力加成区，与基础攻击力相加。
        self.talent_1_atk_bonus_ratio = 0.25 
        
        # 天赋 2：女神的振奋
        # "每攻击一名敌人时为自身与身前一格的我方干员恢复40点生命值"
        # 此天赋提供生命恢复，不直接增加伤害，根据规则不纳入伤害计算。
        
    def _calc_hit(self, enemy, skill_atk_multiplier: float = 1.0, skill_atk_bonus_ratio: float = 0.0, include_skill_3_self_buff: bool = False) -> float:
        """
        计算单次命中时的期望物理伤害，综合考虑：
        1. 帕拉斯自身天赋1 (英雄的诞生) 的攻击力加成
        2. 技能带来的攻击力加成区 (skill_atk_bonus_ratio)
        3. 技能带来的攻击力乘区 (skill_atk_multiplier)
        4. 技能3的自身额外攻击力加成 (include_skill_3_self_buff)
        5. 教官职业特性 (攻击未阻挡敌人时攻击力提升至120%)
        """
        # 从最终基础攻击力开始计算
        current_atk = self.final_base_atk
        
        # 应用天赋1加成：+25%攻击力 (加算)
        # 假设帕拉斯满足天赋条件
        current_atk *= (1 + self.talent_1_atk_bonus_ratio)
        
        # 应用技能的攻击力加成区 (例如S2的+80%，S3的+100%)
        current_atk *= (1 + skill_atk_bonus_ratio)
        
        # 如果技能3的自身额外攻击力加成条件满足 (额外+50%攻击力，加算)
        # 假设满足条件："若身前一格不存在干员或不为近战位时，该效果由自身获得"
        if include_skill_3_self_buff:
            current_atk *= (1 + 0.50) # S3自身额外+50%攻击力
            
        # 应用技能的攻击力乘区 (例如S1的175%)
        current_atk *= skill_atk_multiplier
        
        # 应用教官职业特性：攻击未阻挡敌人时攻击力提升至120%
        # 这是最终的攻击力乘区，在所有加成和乘区之后应用
        final_atk_for_damage = current_atk * self.unblocked_atk_multiplier
        
        return calculate_physical_damage(final_atk_for_damage, enemy.current_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻伤害计算，包含天赋1和教官职业特性
        # 普攻时没有技能的攻击力加成或乘区
        return self._calc_hit(enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (胜利的连击)：下次攻击造成相当于攻击力175%的物理伤害，并连续攻击两次
            # 这是一个“下次攻击”技能，用2次强化攻击取代一次普攻循环。
            # 每次攻击有175%的攻击力倍率。
            
            # _calc_hit 会应用天赋1、教官特性和175%的技能倍率
            single_hit_damage = self._calc_hit(enemy, skill_atk_multiplier=1.75)
            total_damage = single_hit_damage * 2 # 连续攻击两次
            
            # 对于“下次攻击”类技能，DPS为总伤害除以实际攻击间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (信念的长鞭)：攻击范围向前延伸一格，攻击力+80%，每次攻击有85%几率使目标晕眩0.2秒
            # 持续时间：25秒。
            # 攻击力加成：+80% (加算)
            
            # _calc_hit 会应用天赋1、教官特性和+80%的攻击力加成
            single_hit_damage = self._calc_hit(enemy, skill_atk_bonus_ratio=0.80)
            
            duration = 25.0
            num_attacks = (duration or 0) / actual_atk_interval
            
            total_damage = single_hit_damage * num_attacks
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (英勇的祝福)：攻击力+100%，额外攻击两个目标，身前一格为近战位并部署我方干员时使其获得以下增益：
            # 生命值高于80%获得+50%攻击力的精力充沛、防御力+35%、阻挡数+1
            # （若身前一格不存在干员或不为近战位时，该效果由自身获得）
            # 持续时间：30秒。
            # 攻击力加成：+100% (加算)
            # "额外攻击两个目标"：根据规则，严禁将最终伤害乘以目标数，因此此部分不影响单目标总伤和DPS计算。
            # 假设自身获得额外增益：攻击力+50% (加算)。
            
            # _calc_hit 会应用天赋1、教官特性、+100%攻击力加成和+50%自身额外加成。
            single_hit_damage = self._calc_hit(enemy, skill_atk_bonus_ratio=1.00, include_skill_3_self_buff=True)
            
            duration = 30.0
            num_attacks = (duration or 0) / actual_atk_interval
            
            total_damage = single_hit_damage * num_attacks
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
