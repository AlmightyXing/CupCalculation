from backend.function.logic.professions import Specialist
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class R117温蒂(Specialist):
    """
    干员：温蒂
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1: 工程蓄水炮 (部署蓄水炮，不直接影响温蒂自身伤害计算)
        # 天赋 2: 蓄水炮强化 (增加推力，提供技力回复，不直接影响温蒂自身伤害计算)
        # 根据规则，只有对提高伤害有帮助的天赋才纳入考虑。
        # 温蒂的天赋不直接修改自身攻击力、攻速或提供伤害倍率/穿透，因此在此处无需额外处理。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 温蒂普攻为物理伤害，无特殊机制（如破甲、连击等）
        # "同时攻击阻挡的所有敌人" - 严禁在代码中乘以任何目标数，所以按单个目标计算
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员自身的基础实际攻击间隔，用于瞬发技能的DPS计算
        # 注意：技能2会修改攻击间隔，需要单独计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (炮管敲击): 下次攻击造成攻击力150%的物理伤害
            # 这是一个瞬发伤害技能，修改单次普攻的倍率
            atk_val = self.final_base_atk * 1.50
            total_damage = calculate_physical_damage(atk_val, enemy.current_def)
            
            # 瞬发伤害技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (水炮模式): 攻击间隔增大(+220%)，攻击力+200%，切换为远程群体攻击
            # 这是一个持续增益类技能，duration为null，视为永续技能
            
            # 攻击力增益
            enhanced_atk = self.final_base_atk * (1 + 2.00) # +200%攻击力
            
            # 攻击间隔增大 (+220% 是基于基础攻击间隔)
            # self.attack_interval 是干员的基础攻击间隔
            modified_base_attack_interval = self.attack_interval * (1 + 2.20)
            
            # 计算技能期间的实际攻击间隔 (使用修改后的基础间隔和干员自身攻速)
            skill_actual_atk_interval = modified_base_attack_interval * 100 / self.attack_speed
            
            # 计算强化后的单次普攻伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 永续技能 total_damage 为 0，重点是返回正确的 dps
            return {"total_damage": 0, "dps": single_hit_damage / skill_actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (液氮大炮): 立即发射，造成攻击力350%的群体法术伤害
            # 这是一个瞬发爆发伤害技能
            
            atk_val = self.final_base_atk * 3.50
            
            # 伤害类型为法术伤害
            total_damage = calculate_arts_damage(atk_val, enemy.current_res)
            
            # "如果蓄水炮在周围4格内的话也会同样进行发射" - 
            # 根据规则"严禁在代码中乘以任何目标数"以及对干员自身伤害的关注，
            # 蓄水炮的伤害不计入干员自身的total_damage，除非明确说明是干员自身造成两次伤害。
            # "令其8秒内移动时受到正比于距离的真实伤害" 是DoT效果，且与移动距离相关，不计入瞬发总伤。
            
            # 瞬发伤害技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)