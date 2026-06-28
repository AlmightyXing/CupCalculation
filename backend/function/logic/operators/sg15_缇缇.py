from backend.function.logic.professions import MysticCaster
from backend.function.logic.formulas import calculate_arts_damage

class Sg15缇缇(MysticCaster):
    """
    干员：缇缇
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：凝固的时光
        # "自身可以攻击沉睡的敌人" - 机制效果，不直接影响伤害数值计算。
        # "攻击非移动敌人时对其额外造成相当于攻击力15%的法术伤害"
        # 假设敌人为非移动状态，以获得最大收益。此效果视为直接提升攻击倍率。
        self.talent1_bonus_atk_ratio = 0.15
        
        # "在场时沉睡中的敌人每秒受到缇缇攻击力30%的法术伤害"
        # 此为全局持续伤害效果，不与单次攻击挂钩，且影响“所有”沉睡敌人。
        # 根据规则“严禁在代码中乘以任何目标数”和“最终的 total_damage 和 dps 必须严格是对单个目标造成的伤害！”，
        # 此全局DoT不计入单目标伤害计算。
        
        # 天赋 2：勇气的报偿
        # "场上的【米诺斯】或【萨尔贡】干员生命值高于50%时，获得+20攻速的精力充沛"
        # 假设条件满足，获得最大收益。
        self.attack_speed += 20
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑天赋1的额外伤害）
        """
        # 天赋1的额外伤害视为直接提升本次攻击的攻击力倍率
        effective_atk = atk_val * (1 + self.talent1_bonus_atk_ratio)
        return calculate_arts_damage(effective_atk, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻使用最终基础攻击力，并应用天赋1效果
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (缓蚀): 攻击力+100%，每次攻击有50%概率使目标沉睡3秒
            # 持续时间: 17秒
            skill_atk_multiplier = 1.00 # +100% 攻击力，即最终攻击力为基础的 200%
            
            # 计算技能期间的强化攻击力
            enhanced_atk_for_hits = self.final_base_atk * (1 + skill_atk_multiplier)
            
            # 计算单次命中伤害（包含天赋1加成）
            single_hit_damage = self._calc_arts_hit(enhanced_atk_for_hits, enemy)
            
            # 计算技能持续期间的攻击次数
            num_attacks = self._duration_to_hits(17, actual_atk_interval)
            
            total_damage = num_attacks * single_hit_damage
            dps = single_hit_damage / actual_atk_interval # 增益类技能的DPS为强化后单次普攻伤害/实际攻击间隔
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (封护): 停止攻击，攻击力+180%，技能开启时使自身与攻击范围内生命比例最低的干员陷入沉睡直到技能结束，
            # 期间持续使自身与该目标周围的敌人陷入沉睡，第一天赋效果提升至3.3倍，可主动关闭技能
            # 持续时间: 15秒
            
            # 技能描述明确“停止攻击”，因此干员自身不造成直接伤害。
            # 天赋1效果提升主要影响全局DoT，该DoT因单目标计算规则而被排除。
            # 因此，此技能的直接伤害贡献为0。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 2:
            # 技能 3 (旧日绽放): 攻击力+180%，同时攻击两名敌人，攻击非沉睡目标时使其沉睡5秒，
            # 技能期间，全场敌人从沉睡状态醒来或于沉睡中被击倒时，受到法术伤害（随沉睡时长提高至攻击力460%），
            # 并使周围一名其他敌人沉睡5秒，攻击范围内的其他友方干员受到致命伤害时，陷入沉睡至生命值完全恢复或技能结束
            # 持续时间: 25秒
            
            skill_atk_multiplier = 1.80 # +180% 攻击力，即最终攻击力为基础的 280%
            
            # 计算技能期间的强化攻击力
            enhanced_atk_for_hits = self.final_base_atk * (1 + skill_atk_multiplier)
            
            # 计算单次命中伤害（包含天赋1加成）
            # "同时攻击两名敌人" - 根据规则，不乘以目标数，只计算单个目标的伤害。
            single_hit_damage = self._calc_arts_hit(enhanced_atk_for_hits, enemy)
            
            # 计算技能持续期间的攻击次数
            num_attacks = self._duration_to_hits(25, actual_atk_interval)
            
            damage_from_hits = num_attacks * single_hit_damage
            
            # 瞬发伤害: "全场敌人从沉睡状态醒来或于沉睡中被击倒时，受到法术伤害（随沉睡时长提高至攻击力460%）"
            # 假设此瞬发伤害对单个目标触发一次，并取最大倍率460%。
            # 此伤害不属于“攻击”，因此不享受天赋1的“攻击非移动敌人时额外伤害”加成。
            burst_atk_val = self.final_base_atk * 4.60
            burst_damage = calculate_arts_damage(burst_atk_val, enemy.current_res)
            
            total_damage = damage_from_hits + burst_damage
            dps = total_damage / 25 # 技能期间DPS = 总伤 / 技能持续时间
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)

    def _duration_to_hits(self, duration: float, actual_atk_interval: float) -> int:
        """
        计算在给定持续时间内，干员能进行多少次攻击。
        """
        if actual_atk_interval <= 0:
            return 0
        return int(duration / actual_atk_interval)