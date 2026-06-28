from backend.function.logic.professions import PrimalProtector
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Nm06余(PrimalProtector):
    """
    干员：余
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.talent_1_arts_dmg_ratio = 0.0
        self.talent_1_burn_dmg_ratio = 0.0
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：礼尚往来
        # "阻挡敌人时自身获得25%的庇护" -> 防御性天赋，不影响输出伤害，忽略。
        # "并使阻挡的目标每秒受到相当于攻击力40%的法术伤害和相当于攻击力12%的灼燃损伤"
        self.talent_1_arts_dmg_ratio = 0.40
        self.talent_1_burn_dmg_ratio = 0.12 # 灼燃损伤通常视为固定伤害，无视防御/抗性。
        
        # 天赋 2：闲云隐市
        # "场上干员数量不低于4时，自身每秒回复相当于生命上限1.5%的生命与元素损伤" -> 恢复/生存天赋，不影响输出伤害，忽略。
        
    def _calc_talent_1_continuous_dps(self, enemy, atk_val: float) -> float:
        """
        计算天赋1“礼尚往来”带来的每秒持续伤害（法术伤害 + 灼燃损伤）。
        此伤害是每秒结算一次，与攻击间隔无关。
        """
        if self.talent_1_arts_dmg_ratio == 0 and self.talent_1_burn_dmg_ratio == 0:
            return 0.0
            
        arts_dmg_per_sec = calculate_arts_damage(atk_val * self.talent_1_arts_dmg_ratio, enemy.current_res)
        burn_dmg_per_sec = atk_val * self.talent_1_burn_dmg_ratio # 假设元素损伤为固定伤害
        
        return arts_dmg_per_sec + burn_dmg_per_sec

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望伤害。
        余的普攻默认为物理伤害。
        """
        # PrimalProtector 自身没有特殊的普攻逻辑，继承自Operator，为单次物理伤害。
        # 此处直接计算或调用super()效果相同。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 辅助函数：计算技能期间单次普攻的伤害
        def _get_skill_normal_hit_damage(current_atk: float, atk_type: str = 'physical') -> float:
            if atk_type == 'physical':
                return calculate_physical_damage(current_atk, enemy.current_def)
            elif atk_type == 'arts':
                return calculate_arts_damage(current_atk, enemy.current_res)
            return 0.0 # 不应发生

        if skill_index == 0:
            # 技能 0 (今日做东)：
            # "被动效果：自身更容易受到敌人攻击，生命上限+70%，防御力+70%，每次受到攻击对目标造成相当于余攻击力50%的灼燃损伤"
            # 持续时间: 30秒
            # 该技能提供防御性增益和反击伤害。反击伤害取决于敌人攻击频率，不计入干员主动输出DPS。
            # 仅计算普攻和天赋1的持续伤害。
            
            duration = 30
            current_atk = self.final_base_atk # 技能不直接提供攻击力加成
            
            normal_hit_dmg = _get_skill_normal_hit_damage(current_atk, 'physical')
            talent_1_dps_component_skill = self._calc_talent_1_continuous_dps(enemy, current_atk)
            
            # 总伤害 = (普攻次数 * 单次普攻伤害) + (天赋1持续伤害DPS * 持续时间)
            num_hits = duration / actual_atk_interval
            total_damage = (normal_hit_dmg * num_hits) + (talent_1_dps_component_skill * duration)
            
            # DPS = (单次普攻伤害 / 实际攻击间隔) + 天赋1持续伤害DPS
            dps = (normal_hit_dmg / actual_atk_interval) + talent_1_dps_component_skill
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 1 (厚礼上宾)：
            # 持续时间: 20秒
            # "立即对周围所有敌人造成相当于攻击力100%的法术伤害并将其中的地面可达目标传送至自身位置"
            # "阻挡数+2，生命上限+160%，攻击力+290%，普通攻击造成法术伤害"
            
            duration = 20
            atk_buff_ratio = 2.90 # 攻击力+290%
            
            # 计算强化后的攻击力（增益先于爆发伤害触发）
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 瞬发爆发伤害
            burst_atk_ratio = 1.0 # 100%攻击力
            burst_damage = calculate_arts_damage(enhanced_atk * burst_atk_ratio, enemy.current_res)
            
            # 技能期间普攻伤害（变为法术伤害）
            normal_hit_dmg = _get_skill_normal_hit_damage(enhanced_atk, 'arts')
            # 天赋1持续伤害也使用强化后的攻击力
            talent_1_dps_component_skill = self._calc_talent_1_continuous_dps(enemy, enhanced_atk)
            
            # 总伤害 = 爆发伤害 + (普攻次数 * 单次普攻伤害) + (天赋1持续伤害DPS * 持续时间)
            num_hits = duration / actual_atk_interval
            total_damage = burst_damage + (normal_hit_dmg * num_hits) + (talent_1_dps_component_skill * duration)
            
            # DPS = (强化后的单次普攻伤害 / 实际攻击间隔) + 天赋1持续伤害DPS
            dps = (normal_hit_dmg / actual_atk_interval) + talent_1_dps_component_skill
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 2 (灶里乾坤)：
            # 持续时间: 45秒
            # "生命上限+110%，攻击力+110%，防御力+110%"
            # "将第二天赋效果赋予全场所有干员；生成一面跨越整个战场的火墙，其他友方穿过火墙造成法术伤害时附带相当于余攻击力10%的灼燃损伤，敌方子弹穿过火墙时有20%几率被清除"
            # 其他效果为辅助/功能性，不计入余的直接输出伤害。
            
            duration = 45
            atk_buff_ratio = 1.10 # 攻击力+110%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 技能期间普攻伤害（仍为物理伤害）
            normal_hit_dmg = _get_skill_normal_hit_damage(enhanced_atk, 'physical')
            # 天赋1持续伤害也使用强化后的攻击力
            talent_1_dps_component_skill = self._calc_talent_1_continuous_dps(enemy, enhanced_atk)
            
            # 总伤害 = (普攻次数 * 单次普攻伤害) + (天赋1持续伤害DPS * 持续时间)
            num_hits = duration / actual_atk_interval
            total_damage = (normal_hit_dmg * num_hits) + (talent_1_dps_component_skill * duration)
            
            # DPS = (强化后的单次普攻伤害 / 实际攻击间隔) + 天赋1持续伤害DPS
            dps = (normal_hit_dmg / actual_atk_interval) + talent_1_dps_component_skill
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
