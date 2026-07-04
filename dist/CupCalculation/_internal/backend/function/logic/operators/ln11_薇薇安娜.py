from backend.function.logic.professions import ArtsFighter
from backend.function.logic.formulas import calculate_arts_damage

class Ln11薇薇安娜(ArtsFighter):
    """
    干员：薇薇安娜
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化法术伤害乘数，用于天赋加成
        self.arts_damage_multiplier = 1.0 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：燃烛施明
        # "造成的法术伤害+8%，受到的物理和法术伤害-8%。攻击范围内存在精英或领袖敌人时，该效果提升至2倍"
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，并按最大层数/效果叠加。
        # 因此，假设攻击范围内存在精英或领袖敌人，取最大伤害加成。
        # 法术伤害加成 = 8% * 2 = 16%
        self.arts_damage_multiplier *= (1 + 0.08 * 2) 
        
        # 天赋 2：散华
        # "攻击精英或领袖敌人时，有18%概率获得一层仅抵挡敌方近战攻击的护盾（最多1层）"
        # 该天赋为防御性天赋，不直接影响伤害输出，故不在此处实现。
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑天赋1的法术伤害加成）
        atk_val: 经过技能倍率加成后的攻击力
        """
        # 将天赋1的法术伤害乘数应用于最终攻击力
        return calculate_arts_damage(atk_val * self.arts_damage_multiplier, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 薇薇安娜的普攻造成法术伤害
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，考虑攻速加成
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (光影迅捷剑)：
            # "下次攻击的攻击力提高至200%，并连续攻击两次；蓄力额外效果：攻击范围延长，改为连续攻击三次"
            # 根据规则，取最大伤害效果，即假设为蓄力状态。
            atk_multiplier = 2.0
            hits = 3 # 蓄力后三连击
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            # 计算总伤害
            total_damage = self._calc_arts_hit(enhanced_atk, enemy) * hits
            
            # 瞬发伤害技能，DPS为总伤除以普攻间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (烛燃影息)：
            # "攻击力+40%，防御力+160%，阻挡数+1，同时攻击阻挡的所有敌人。
            # 每次攻击有20%的概率变为150%攻击力的二连击，并偷取目标40点攻击速度（最多40点，持续至技能结束或薇薇安娜离场）"
            duration = 35
            atk_buff_ratio = 0.40
            prob_double_hit = 0.20
            double_hit_atk_multiplier = 1.50
            
            # 计算技能期间强化后的基础攻击力
            skill_enhanced_base_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算单次普攻的期望伤害（考虑20%概率的二连击）
            # 正常单次攻击伤害
            normal_hit_dmg = self._calc_arts_hit(skill_enhanced_base_atk, enemy)
            # 150%攻击力的二连击伤害
            double_hit_dmg = self._calc_arts_hit(skill_enhanced_base_atk * double_hit_atk_multiplier, enemy) * 2
            
            # 单次攻击的期望伤害 = (1-概率) * 正常伤害 + 概率 * 二连击伤害
            expected_dmg_per_attack = (1 - prob_double_hit) * normal_hit_dmg + prob_double_hit * double_hit_dmg
            
            # 技能持续期间的攻击次数
            num_attacks = (duration or 0) / actual_atk_interval
            
            total_damage = expected_dmg_per_attack * num_attacks
            dps = expected_dmg_per_attack / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (“明灭”)：
            # "攻击间隔延长(+0.5)，攻击力+110%，防御力+90%，法术抗性+25，攻击变为二连击，第二天赋的触发几率提升至2.5倍，优先攻击精英或领袖敌人。
            # 第二次及以后使用时，攻击范围延长，攻击变为三连击，持续时间延长至25秒"
            # 根据规则，取最大伤害效果，即假设为第二次及以后使用。
            duration = 25 # 延长后的持续时间
            atk_buff_ratio = 1.10
            attack_interval_increase = 0.5
            hits_per_attack = 3 # 第二次及以后使用时三连击
            
            # 计算新的基础攻击间隔
            new_base_attack_interval = self.attack_interval + attack_interval_increase
            # 计算新的实际攻击间隔，考虑攻速加成
            new_actual_atk_interval = new_base_attack_interval * 100 / self.attack_speed
            
            # 计算技能期间强化后的基础攻击力
            skill_enhanced_base_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算单次攻击的伤害（三连击）
            dmg_per_attack = self._calc_arts_hit(skill_enhanced_base_atk, enemy) * hits_per_attack
            
            # 技能持续期间的攻击次数
            num_attacks = duration / new_actual_atk_interval
            
            total_damage = dmg_per_attack * num_attacks
            dps = dmg_per_attack / new_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)