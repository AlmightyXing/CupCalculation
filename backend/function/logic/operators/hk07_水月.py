from backend.function.logic.professions import Ambusher
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Hk07水月(Ambusher):
    """
    干员：水月
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：创伤性癔症 (攻击时对攻击目标中生命值最少的敌人额外造成相当于攻击力50%的法术伤害)
        # 存储天赋1的法术伤害倍率
        self.talent1_arts_ratio = 0.5
        
        # 天赋 2：反移情 (攻击范围内存在生命值低于一半的敌人时，攻击力+10%)
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，因此假设条件满足
        self.final_base_atk *= (1 + 0.10) # 将10%攻击力加成应用到最终基础攻击力
        
    def _calc_hit(self, atk_val: float, enemy, talent1_arts_multiplier: float = 1.0) -> float:
        """
        计算单次命中时的期望伤害（物理伤害 + 天赋1的法术伤害）
        :param atk_val: 当前用于计算伤害的攻击力数值
        :param enemy: 敌人对象
        :param talent1_arts_multiplier: 天赋1法术伤害的额外倍率，默认为1.0
        :return: 单次命中造成的总期望伤害
        """
        # 计算物理伤害
        physical_dmg = calculate_physical_damage(atk_val, enemy.current_def)
        
        # 计算天赋1的法术伤害
        # 法术伤害的攻击力基数 = 当前攻击力 * 天赋1基础倍率 * 天赋1额外倍率
        arts_dmg_base = atk_val * self.talent1_arts_ratio * talent1_arts_multiplier
        arts_dmg = calculate_arts_damage(arts_dmg_base, enemy.current_res)
        
        return physical_dmg + arts_dmg

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻直接调用内部计算方法，天赋1的额外倍率为默认值1.0
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于DPS计算
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (唤醒)：下次攻击造成相当于攻击力300%的物理伤害，且第一天赋伤害倍率提升至3倍；可充能3次
            # 这是一个瞬发伤害技能，替换一次普攻
            
            # 技能描述是“下次攻击造成...”，所以是基于当前攻击力进行倍率计算
            skill_atk_val = self.final_base_atk * 3.0
            # 天赋1的法术伤害倍率提升至3倍
            skill_talent1_arts_multiplier = 3.0
            
            # 计算单次爆发的总伤害
            total_damage = self._calc_hit(skill_atk_val, enemy, skill_talent1_arts_multiplier)
            
            # 瞬发伤害技能的DPS计算方式：总伤 / 实际攻击间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (囚徒困境)：攻击间隔较大幅度缩短(-1.5s)，攻击力+30%，第一天赋额外攻击1个目标并附加1.3秒束缚
            # 这是一个持续增益技能
            duration = 21 # 技能持续时间
            atk_buff_ratio = 0.30 # 攻击力+30%
            
            # 1. 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 2. 计算强化后的实际攻击间隔
            # 原始攻击间隔为 self.attack_interval (水月为3.5s)
            # 攻击间隔缩短1.5s，所以新的基础攻击间隔为 3.5 - 1.5 = 2.0s
            new_base_attack_interval = self.attack_interval - 1.5
            enhanced_actual_atk_interval = new_base_attack_interval * 100 / self.attack_speed
            
            # 3. 计算技能期间单次普攻的伤害（天赋1倍率不变，仍为1.0）
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 4. 计算技能期间的总伤害和DPS
            # 技能期间的攻击次数
            num_attacks = duration / enhanced_actual_atk_interval
            
            total_damage = single_hit_damage * num_attacks
            dps = single_hit_damage / enhanced_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (镜花水月)：攻击范围扩大，攻击力+150%，第一天赋额外攻击2个目标并附加1秒晕眩；每次攻击命中目标少于3名敌人时，自身流失最大生命值的12%
            # 这是一个持续增益技能
            duration = 30 # 技能持续时间
            atk_buff_ratio = 1.50 # 攻击力+150%
            
            # 1. 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 2. 攻击间隔没有变化，使用原始的 actual_atk_interval
            
            # 3. 计算技能期间单次普攻的伤害（天赋1倍率不变，仍为1.0）
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 4. 计算技能期间的总伤害和DPS
            # 技能期间的攻击次数
            num_attacks = (duration or 0) / actual_atk_interval
            
            total_damage = single_hit_damage * num_attacks
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果技能索引不匹配，调用基类的处理方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)