from backend.function.logic.professions import Vanguard
from backend.function.logic.formulas import calculate_physical_damage

class Kz11焰尾(Vanguard):
    """
    干员：焰尾
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.talent_1_double_hit_multiplier = 1 # 默认为1，如果天赋生效则为2
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：前锋剑术 (触发闪避时，下次攻击变为二连击并攻击所有阻挡的敌人)
        # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑！”，且焰尾技能组有高额闪避，
        # 我们假设此天赋的二连击效果在计算伤害时是常驻触发的。
        # 注意：严禁在代码中乘以任何目标数，所以只考虑“二连击”部分。
        self.talent_1_double_hit_multiplier = 2
        
        # 天赋 2：红松骑士团团长 (在场时，所有【卡西米尔】势力的干员获得22%的物理闪避)
        # 此天赋为团队增益，不直接影响焰尾自身的单体伤害输出，故不在此处体现。
        
    def _calc_single_physical_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次物理命中时的期望伤害。
        """
        return calculate_physical_damage(atk_val, enemy.current_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻伤害 = 单次命中伤害 * (天赋1二连击乘数)
        single_hit_dmg = self._calc_single_physical_hit(self.final_base_atk, enemy)
        return single_hit_dmg * self.talent_1_double_hit_multiplier

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (迅敏直觉)：立即获得6点部署费用，并闪避下次物理攻击
            # 此技能无直接伤害，只提供费用和闪避。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (“红松林”)：立即获得13点部署费用；对周围最多6名敌人造成两次相当于攻击力240%的物理伤害
            # 瞬发爆发伤害。
            # 攻击力倍率：240%
            # 攻击次数：2次 (技能描述)
            # 天赋1的二连击效果：如果此技能是“下次攻击”，则会使每次攻击变为二连击。
            # 那么总攻击次数为 2 (技能描述) * self.talent_1_double_hit_multiplier (天赋1)
            
            atk_val = self.final_base_atk * 2.40
            single_hit_dmg = self._calc_single_physical_hit(atk_val, enemy)
            
            # 技能描述的2次伤害 * 天赋1的二连击效果
            total_damage = single_hit_dmg * 2 * self.talent_1_double_hit_multiplier
            
            # 瞬发技能的DPS计算方式：总伤 / 攻击间隔 (这里用实际攻击间隔作为爆发时间基准)
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (焰心)：技能持续时间内逐渐获得8点部署费用，攻击间隔70%缩短(*70%)，攻击力+90%，阻挡数+1，获得80%的物理和法术闪避
            # 增益类技能。
            duration = 8.0
            atk_buff_ratio = 0.90
            # "攻击间隔70%缩短(*70%)" 通常理解为攻击间隔变为原来的70%
            attack_interval_multiplier = 0.70 
            
            # 计算技能期间的实际攻击间隔
            skill_actual_atk_interval = actual_atk_interval * attack_interval_multiplier
            
            # 计算技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能持续期间能打出的普攻次数
            num_attacks = duration / skill_actual_atk_interval
            
            # 计算单次强化普攻的伤害（考虑天赋1的二连击效果，因为技能提供了80%高额闪避，天赋1几乎常驻）
            single_enhanced_hit_dmg = self._calc_single_physical_hit(enhanced_atk, enemy)
            
            # 技能期间的总伤害 = (单次强化普攻伤害 * 天赋1二连击乘数) * 普攻次数
            total_damage = single_enhanced_hit_dmg * self.talent_1_double_hit_multiplier * num_attacks
            
            # 技能期间的DPS = (单次强化普攻伤害 * 天赋1二连击乘数) / 技能期间的实际攻击间隔
            dps = (single_enhanced_hit_dmg * self.talent_1_double_hit_multiplier) / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)