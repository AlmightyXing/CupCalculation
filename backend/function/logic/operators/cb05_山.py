from backend.function.logic.professions import Fighter
from backend.function.logic.formulas import calculate_physical_damage

class Cb05山(Fighter):
    """
    干员：山
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：巨力重拳
        # "攻击时有20%的几率攻击力提升至160%"
        self.talent_1_prob = 0.20
        self.talent_1_atk_multiplier = 1.60
        # "并在3秒内使目标攻击力降低15%（不可叠加）" - 此效果为敌方debuff，不直接增加自身伤害，故不纳入伤害计算。

        # 天赋 2：强壮肉体
        # "防御力+10%"
        self.base_def *= 1.10 # 将防御力加成直接应用到基础防御力上
        # "获得15%的物理闪避" - 此效果为生存向，不直接增加自身伤害，故不纳入伤害计算。
        
    def _calc_hit(self, atk_val: float, enemy, talent_prob_override: float = None) -> float:
        """
        计算单次命中时的期望物理伤害，考虑巨力重拳天赋的攻击力提升概率。
        talent_prob_override: 用于覆盖天赋1的触发概率，例如技能3。
        """
        # 获取实际的天赋1触发概率
        prob = talent_prob_override if talent_prob_override is not None else self.talent_1_prob
        
        # 天赋1触发时的伤害
        dmg_talent_activated = calculate_physical_damage(atk_val * self.talent_1_atk_multiplier, enemy.current_def)
        
        # 天赋1未触发时的伤害
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 计算期望伤害
        return prob * dmg_talent_activated + (1 - prob) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻使用最终基础攻击力，并考虑天赋1的默认触发概率
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，考虑攻速加成
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (左勾扫拳): "下次攻击的攻击力提升至230%，额外攻击一个目标"
            # 这是一个单次爆发伤害技能。
            
            # 计算强化后的攻击力
            atk_val = self.final_base_atk * 2.30
            
            # 计算单次爆发伤害（"额外攻击一个目标"不计入单目标总伤）
            total_damage = self._calc_hit(atk_val, enemy)
            
            # 对于瞬发技能，DPS = 总伤 / 实际攻击间隔（代表技能的“冷却”或触发频率）
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (横扫架势): "防御力-20%，攻击距离缩短，攻击力+80%，阻挡数+1，同时攻击阻挡的所有敌人，每秒恢复最大生命的7.0%"
            # 这是一个切换姿态的永续技能（JSON中duration为5，但描述暗示为切换，按永续处理）。
            
            # 应用攻击力加成
            modified_atk = self.final_base_atk * (1 + 0.80) # 攻击力+80%
            
            # 计算强化后的单次普攻伤害
            single_hit_damage = self._calc_hit(modified_atk, enemy)
            
            # 对于永续技能，总伤为0，DPS为技能期间的持续伤害
            # 其他效果（防御力降低、攻击距离缩短、阻挡数增加、攻击阻挡的所有敌人、生命恢复）不计入单目标伤害计算。
            return {"total_damage": 0, "dps": single_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (震地碎岩击):
            # "攻击间隔增大(+70%)"
            # "攻击力+100%"
            # "攻击变为2连击"
            # "第一天赋的发动几率提升至75%"
            # "每次攻击周围最多4个敌人并将其中等力度地推动" (多目标攻击和推力不计入单目标伤害计算)
            
            duration = 30 # 技能持续时间
            
            # 计算修改后的攻击间隔
            modified_atk_interval = actual_atk_interval * (1 + 0.70)
            
            # 计算强化后的攻击力
            modified_atk = self.final_base_atk * (1 + 1.00) # 攻击力+100%
            
            # 计算单次攻击的伤害，并覆盖天赋1的触发概率
            single_hit_damage = self._calc_hit(modified_atk, enemy, talent_prob_override=0.75)
            
            # 攻击变为2连击
            hits_per_attack = 2
            
            # 计算技能持续期间能打出的攻击次数
            num_attacks = duration / modified_atk_interval
            
            # 计算总伤害 = (单次攻击伤害 * 连击数) * 攻击次数
            total_damage = num_attacks * single_hit_damage * hits_per_attack
            
            # 计算DPS = (单次攻击伤害 * 连击数) / 修改后的攻击间隔
            dps = (single_hit_damage * hits_per_attack) / modified_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)