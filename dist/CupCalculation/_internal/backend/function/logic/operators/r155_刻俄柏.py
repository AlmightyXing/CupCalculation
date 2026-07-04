from backend.function.logic.professions import CoreCaster
from backend.function.logic.formulas import calculate_arts_damage, calculate_physical_damage

class R155刻俄柏(CoreCaster):
    """
    干员：刻俄柏
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：剥壳 (攻击时对目标额外造成相当于其防御力40%的法术伤害)
        # 存储防御力转化为法术伤害的比例
        self.def_damage_ratio = 0.4
        
        # 天赋 2：独行长路 (当周围四格内没有其他友方单位时，攻击力+8%，攻击速度+8)
        # 假设满足条件，取最大收益
        self.final_base_atk *= (1 + 0.08)
        self.attack_speed += 8
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算刻俄柏单次法术命中时的期望伤害，包含“剥壳”天赋。
        """
        # 基础法术伤害
        base_arts_dmg = calculate_arts_damage(atk_val, enemy.current_res)
        # 剥壳天赋：额外造成相当于目标防御力40%的法术伤害
        extra_arts_dmg_from_def = enemy.current_def * self.def_damage_ratio
        return base_arts_dmg + extra_arts_dmg_from_def

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 刻俄柏普攻造成法术伤害，并受“剥壳”天赋影响
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1：“很冰的斧” (下次攻击的攻击力提升至210%，可充能3次)
            # 这是一个瞬发技能，只计算单次强化攻击的伤害
            
            # 攻击力提升至210%
            enhanced_atk = self.final_base_atk * 2.10
            
            # 计算强化后的单次法术伤害（包含剥壳天赋）
            total_damage = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 瞬发技能的DPS计算方式：总伤 / 普攻间隔
            dps = total_damage / actual_atk_interval
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2：“很热的刀” (攻击间隔超大幅度缩短*0.33，持续40秒)
            skill_duration = 40
            
            # 技能期间的实际攻击间隔
            # 攻击间隔缩短为原来的0.33倍
            skill_atk_interval = self.attack_interval * 0.33 * 100 / self.attack_speed
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = skill_duration / skill_atk_interval
            
            # 单次普攻伤害（法术伤害，包含剥壳天赋）
            dmg_per_hit = self._calc_arts_hit(self.final_base_atk, enemy)
            
            # 技能总伤害 = 普攻次数 * 单次普攻伤害
            total_damage = num_hits * dmg_per_hit
            # 技能期间的DPS = 单次普攻伤害 / 技能期间的攻击间隔
            dps = dmg_per_hit / skill_atk_interval
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3：“很重的枪” (攻击力+210%，伤害类型变为物理，持续60秒)
            skill_duration = 60
            
            # 攻击力增益：攻击力+210% 意味着最终攻击力是基础的 (1 + 2.10) 倍
            atk_multiplier = 1 + 2.10 
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 伤害类型变为物理，此时“剥壳”天赋（额外造成法术伤害）不适用
            dmg_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间能打出的普攻次数
            num_hits = skill_duration / actual_atk_interval
            
            # 技能总伤害 = 普攻次数 * 单次普攻伤害
            total_damage = num_hits * dmg_per_hit
            # 技能期间的DPS = 单次普攻伤害 / 普攻间隔
            dps = dmg_per_hit / actual_atk_interval
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果技能索引不匹配，调用基类的处理方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)