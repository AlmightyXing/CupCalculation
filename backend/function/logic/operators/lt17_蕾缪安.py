from backend.function.logic.professions import Deadeye
from backend.function.logic.formulas import calculate_physical_damage

class Lt17蕾缪安(Deadeye):
    """
    干员：蕾缪安
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：跨境追缉许可
        # 只要天赋对提高伤害有帮助，均纳入考虑。
        # 假设目标为被通缉的精英或领袖敌人，获得15%伤害提升。
        self.talent_1_dmg_boost = 1.15
        
        # 天赋 2：逃犯引渡手续
        # 假设在场20秒后，攻击力+10%，自身弹药类技能弹药上限+1。
        # 攻击力+10%直接作用于最终基础攻击力。
        self.final_base_atk *= (1 + 0.10) 
        # 弹药上限+1，存储为属性，在技能计算时使用。
        self.talent_2_ammo_boost = 1 
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑天赋1的伤害提升）
        """
        # 蕾缪安的攻击是物理伤害
        dmg = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 应用天赋1：跨境追缉许可 (对被通缉敌人伤害提升15%)
        dmg *= self.talent_1_dmg_boost
        
        return dmg

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻使用最终基础攻击力
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于DPS计算。
        # 注意：技能可能会修改攻击速度，所以这里先用基础值，技能内部再根据情况调整。
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (重逢问候)：
            # 攻击时攻击力提升至210%，额外攻击1名敌人；攻击装有6发弹药，打完后结束。
            
            # 攻击力提升至210%
            skill_atk_multiplier = 2.10
            skill_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 弹药数：6发 + 天赋2的1发
            ammo_count = 6 + self.talent_2_ammo_boost
            
            # 单次命中伤害
            single_hit_dmg = self._calc_hit(skill_atk_val, enemy)
            
            # 总伤害 = 弹药数 * 单次命中伤害 (严禁乘以目标数)
            total_damage = ammo_count * single_hit_dmg
            
            # DPS = 单次命中伤害 / 实际攻击间隔 (技能期间攻击间隔不变)
            dps = single_hit_dmg / base_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (归乡邀约)：
            # 攻击速度+80，攻击力+70%，场上有被通缉敌人时会消耗1发弹药对其瞄准最多3.5秒后进行无视闪避的狙击
            # （期间攻击力从180%逐渐提升至425%，攻击力高于或等于敌人剩余生命值和防御力之和时停止瞄准并立刻攻击）；
            # 攻击装有7发弹药，打完后结束。
            
            # 技能期间攻击力加成 (先触发)
            skill_base_atk_boost_ratio = 0.70
            
            # 狙击攻击力倍率：取最大值425% (后触发，基于强化后的攻击力)
            sniper_atk_multiplier = 4.25
            
            # 技能期间的攻击力 = (最终基础攻击力 * (1 + 技能基础攻击力加成)) * 狙击攻击力倍率
            skill_atk_val = self.final_base_atk * (1 + skill_base_atk_boost_ratio) * sniper_atk_multiplier
            
            # 技能期间攻击速度加成
            skill_aspd_boost = 80
            skill_actual_atk_interval = self.attack_interval * 100 / (self.attack_speed + skill_aspd_boost)
            
            # 弹药数：7发 + 天赋2的1发
            ammo_count = 7 + self.talent_2_ammo_boost
            
            # 单次命中伤害
            single_hit_dmg = self._calc_hit(skill_atk_val, enemy)
            
            # 总伤害 = 弹药数 * 单次命中伤害 (严禁乘以目标数)
            total_damage = ammo_count * single_hit_dmg
            
            # DPS = 单次命中伤害 / 技能期间实际攻击间隔
            dps = single_hit_dmg / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (礼炮·强制追思)：
            # 停止攻击，每0.5秒消耗1发弹药依次锁定敌人，技能结束时对每名被锁定的敌人所在位置进行轰炸，
            # 轰炸造成攻击力300%的范围物理伤害（中心伤害提升至攻击力的450%）；攻击装有5发弹药，打完后结束。
            
            # 轰炸攻击力倍率：中心伤害提升至450%
            bomb_atk_multiplier = 4.50
            skill_atk_val = self.final_base_atk * bomb_atk_multiplier
            
            # 弹药数：5发 + 天赋2的1发
            ammo_count = 5 + self.talent_2_ammo_boost
            
            # 单次轰炸伤害 (针对一个目标，假设该目标处于中心区域)
            single_bomb_dmg = self._calc_hit(skill_atk_val, enemy)
            
            # 总伤害：由于规则要求只计算对单个目标的伤害，且技能描述是“对每名被锁定的敌人所在位置进行轰炸”，
            # 我们假设一个目标只会被一次轰炸命中。因此总伤就是单次轰炸伤害。
            total_damage = single_bomb_dmg
            
            # 技能持续时间 = 弹药数 * 每发弹药消耗时间
            skill_duration = ammo_count * 0.5
            
            # DPS = 总伤害 / 技能持续时间
            dps = total_damage / skill_duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)