from backend.function.logic.professions import Merchant
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Lm18老鲤(Merchant):
    """
    干员：老鲤
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：和气生财
        # "老鲤阻挡目标时，使其攻击速度-14，且自身攻击速度+14；当周围八格内仅存在一个敌人时效果翻倍"
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，并按最大层数叠加。
        # 假设处于最佳条件：阻挡目标且周围八格内仅存在一个敌人。
        # 自身攻击速度增加：14 * 2 = 28
        self.attack_speed += 28
        
        # 天赋 2：有备无患
        # "特性消耗费用时，若费用足够则改为消耗5费用，抵消自身受到的下一次晕眩/冻结，并使攻击来源晕眩3秒"
        # 此天赋提供控制免疫和反控，不直接影响老鲤的伤害输出，因此在伤害计算中无需额外实现。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 老鲤的普攻为物理伤害，天赋中没有对普攻的特殊破甲或连击效果。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算基础实际攻击间隔（不含技能自身带来的攻速加成，因为永续技能的DPS计算需要基于此）
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (小惩大诫)
            # "攻击力+60%，并获得40%的法术闪避"
            # duration: null -> 永续技能
            # total_damage = 0，重点是返回正确的 dps。
            
            # 攻击力增益
            skill_atk_val = self.final_base_atk * (1 + 0.60)
            
            # 计算强化后的单次普攻伤害
            damage_per_hit = calculate_physical_damage(skill_atk_val, enemy.current_def)
            
            # 法术闪避为防御性效果，不计入伤害计算。
            
            return {"total_damage": 0, "dps": damage_per_hit / base_actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (驱凶辟邪)
            # "被动效果：攻击速度+30；主动开启：标记目标使其更易受我方攻击，5秒后标记爆炸对周围造成300%的法术伤害。
            # 期间我方每对目标造成一次伤害，爆炸伤害增加老鲤攻击力的20%（最多增加30次，达到上限或目标被击倒时提前爆炸）"
            # duration: 5 秒
            
            # 这是一个瞬发爆发伤害技能，发生在技能持续时间结束时。
            # 根据规则，对于可叠加层数的天赋/技能效果，直接按最大层数叠加。
            # 因此，假设“我方每对目标造成一次伤害”的次数达到上限30次。
            max_bonus_hits = 30
            
            # 初始爆发伤害倍率：300%
            # 每次伤害增加的攻击力倍率：20%
            # 总额外攻击力倍率：max_bonus_hits * 0.20 = 30 * 0.20 = 6.0
            # 总爆发伤害倍率：3.0 (初始) + 6.0 (额外) = 9.0
            
            # 爆发伤害为法术伤害
            burst_atk_val = self.final_base_atk * 9.0
            total_damage = calculate_arts_damage(burst_atk_val, enemy.current_res)
            
            # "更易受我方攻击"是敌方debuff，不直接计入老鲤自身伤害。
            # 被动攻速+30会影响期间老鲤的攻击次数，但由于我们直接假设了最大层数，所以此处不直接用于计算攻击次数。
            
            # DPS = 总伤害 / 技能持续时间
            dps = total_damage / 5
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (贵客盈门)
            # "攻击范围扩大，攻击力和防御力+50%；攻击小力度推开范围内除当前目标外的敌人。
            # 自身嘲讽等级1，且有70%概率闪避来自范围外的物理或法术伤害"
            # duration: null -> 永续技能
            # total_damage = 0，重点是返回正确的 dps。
            
            # 攻击力增益
            skill_atk_val = self.final_base_atk * (1 + 0.50)
            
            # 计算强化后的单次普攻伤害
            damage_per_hit = calculate_physical_damage(skill_atk_val, enemy.current_def)
            
            # 防御力增加、推开、嘲讽等级、闪避均为防御性或控制性效果，不计入伤害计算。
            
            return {"total_damage": 0, "dps": damage_per_hit / base_actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)