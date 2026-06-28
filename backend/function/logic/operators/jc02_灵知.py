from backend.function.logic.professions import Hexer
from backend.function.logic.formulas import calculate_arts_damage

class Jc02灵知(Hexer):
    """
    干员：灵知
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：坚冰 (攻击造成1秒寒冷；范围内寒冷的敌人受到25%的脆弱，范围内冻结的敌人脆弱效果提升至2倍)
        # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑！”，我们假设敌人处于最有利于灵知伤害输出的状态。
        # 即敌人处于“冻结”状态，此时脆弱效果为25% * 2 = 50%。
        # 脆弱效果表现为敌人受到的伤害增加，因此是乘法加成。
        self.talent_fragile_multiplier = 1 + 0.50 # 1 (基础伤害) + 0.50 (50%脆弱)
        
        # 天赋 2：殊途同归 (灵知在场且部署后经过10秒后，使所有【谢拉格】干员获得抵抗)
        # 此天赋为辅助效果，不直接影响灵知自身的伤害输出，故不在此处体现。
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑坚冰天赋的脆弱效果）
        灵知攻击造成法术伤害。
        """
        # 计算基础法术伤害
        damage = calculate_arts_damage(atk_val, enemy.current_res)
        # 应用天赋“坚冰”带来的脆弱效果（假设敌人处于冻结状态）
        return damage * self.talent_fragile_multiplier

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 灵知普攻造成法术伤害，并享受天赋脆弱加成
        # 父类Hexer的特性是“攻击造成法术伤害”，因此这里直接计算法术伤害是正确的。
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于DPS计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (高速思考)：下次攻击连续攻击两次，每次造成相当于攻击力170%的法术伤害
            # 这是一个瞬发技能，替换一次普攻循环。
            atk_val = self.final_base_atk * 1.70
            # 连续攻击两次
            total_damage = self._calc_arts_hit(atk_val, enemy) * 2
            # DPS按替换一次普攻的周期计算
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (零度爆发)：对范围内所有敌人造成4秒寒冷和相当于攻击力200%的法术伤害；蓄力：额外造成一层寒冷
            # 这是一个瞬发爆发伤害技能。
            # “蓄力：额外造成一层寒冷”是状态效果，不直接增加本次爆发伤害的倍率。
            atk_val = self.final_base_atk * 2.0
            total_damage = self._calc_arts_hit(atk_val, enemy)
            # DPS按替换一次普攻的周期计算
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (失温症)：攻击速度+130，同时攻击2个敌人；范围内所有敌人的冻结延长至技能结束，
            # 且技能结束时对所有冻结的敌人造成600%的法术伤害并结束冻结；优先攻击未冻结的单位
            # 这是一个持续性增益+爆发伤害技能。
            duration = 13 # 技能持续时间
            
            # 攻击速度加成
            skill_atk_speed = self.attack_speed + 130
            skill_actual_atk_interval = self.attack_interval * 100 / skill_atk_speed
            
            # 技能期间的普攻次数
            num_attacks = duration / skill_actual_atk_interval
            
            # 技能期间的普攻伤害
            # “范围内所有敌人的冻结延长至技能结束”确保了天赋的冻结脆弱效果全程生效。
            # “同时攻击2个敌人”不计入总伤和DPS的乘数，只计算对单个目标的伤害。
            dmg_per_hit = self._calc_arts_hit(self.final_base_atk, enemy)
            normal_attack_total_damage = dmg_per_hit * num_attacks
            
            # 技能结束时的爆发伤害
            # “对所有冻结的敌人造成600%的法术伤害”
            burst_atk_val = self.final_base_atk * 6.0
            burst_damage = self._calc_arts_hit(burst_atk_val, enemy)
            
            # 总伤害 = 技能期间普攻总伤害 + 技能结束时爆发伤害
            total_damage = normal_attack_total_damage + burst_damage
            
            # DPS = 总伤害 / 技能持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果没有匹配的技能，调用父类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)
