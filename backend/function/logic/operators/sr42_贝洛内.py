from backend.function.logic.professions import Fighter # "斗士" (Fighter) 是近卫的一个分支，这里假设存在 Fighter 类
from backend.function.logic.formulas import calculate_physical_damage

class Sr42贝洛内(Fighter):
    """
    干员：贝洛内
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        # 天赋1: 家族手段 - 防御力降低效果
        self.talent1_def_reduction_per_stack = 0.07 # 每次攻击降低7%防御力
        self.talent1_max_stacks_normal = 5 # 普攻和S3时最多叠加5次
        self.talent1_max_stacks_s2 = 8 # S2期间最多叠加8次
        
        # 天赋1: 家族手段 - 生命值比例伤害加成
        # 假设计算时敌人生命值处于最低20%以下，以获得最高伤害加成
        self.talent1_hp_threshold_multiplier = 1.28 # 伤害提高到最高128% (即1.28倍)
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：家族手段
        # "攻击使目标在10秒内防御力降低7%（最多叠加5次）"
        # "并且目标剩余生命值比例越低自身对其造成的伤害越高，在剩余20%以下生命值时伤害提高到最高128%"
        # 这些效果在 _calc_hit 方法中统一处理，无需在此直接修改面板属性。
        
        # 天赋 2：街头直觉
        # "获得40%的物理和法术闪避，部署后提高到80%并在20秒内逐渐衰减"
        # 此天赋为防御性天赋（闪避），不直接提高伤害输出，因此根据规则不纳入伤害计算。
        pass
        
    def _calc_hit(self, atk_val: float, enemy, def_reduction_stacks: int) -> float:
        """
        计算单次命中时的期望物理伤害，考虑家族手段天赋的防御力降低和生命值比例伤害加成。
        :param atk_val: 当前攻击力数值。
        :param enemy: 敌人对象。
        :param def_reduction_stacks: 天赋1防御力降低的叠加层数。
        :return: 单次命中期望伤害。
        """
        # 计算总防御力降低比例
        total_def_reduction_ratio = min(def_reduction_stacks * self.talent1_def_reduction_per_stack, 1.0) # 确保不超过100%
        
        # 计算物理伤害
        damage = calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=total_def_reduction_ratio)
        
        # 应用生命值比例伤害加成（假设最佳情况：敌人生命值 <= 20%）
        damage *= self.talent1_hp_threshold_multiplier
        
        return damage

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻时，天赋1防御力降低效果按默认最大层数（5层）计算
        return self._calc_hit(self.final_base_atk, enemy, def_reduction_stacks=self.talent1_max_stacks_normal)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 基础攻击间隔，用于计算DPS
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (家主的余裕)：下次攻击对目标造成两次相当于攻击力250%的物理伤害
            # 这是一个瞬发爆发技能，计算单次技能的总伤害。
            atk_multiplier = 2.5
            atk_val = self.final_base_atk * atk_multiplier
            
            # 造成两次伤害
            total_damage = self._calc_hit(atk_val, enemy, def_reduction_stacks=self.talent1_max_stacks_normal) * 2
            
            # 瞬发技能的DPS通常按总伤除以攻击间隔（或技能回转时间，这里简化为攻击间隔）
            return {"total_damage": total_damage, "dps": total_damage / base_actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (军师的手段)：
            # 持续时间: 22秒
            # 效果: 攻击速度+80，每次攻击对3名目标造成相当于攻击力200%的物理伤害
            # 特殊: 技能期间第一天赋使目标防御力降低的效果改为最多叠加8次
            
            skill_duration = 22
            skill_atk_speed_boost = 80
            skill_atk_multiplier = 2.0
            skill_def_reduction_stacks = self.talent1_max_stacks_s2 # S2期间天赋1改为8层
            
            # 计算技能期间的实际攻击速度和攻击间隔
            skill_attack_speed = self.attack_speed + skill_atk_speed_boost
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 计算技能期间的单次攻击力
            skill_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 计算单次攻击的伤害（使用S2期间的天赋1防御力降低层数）
            damage_per_hit = self._calc_hit(skill_atk_val, enemy, def_reduction_stacks=skill_def_reduction_stacks)
            
            # 计算技能持续期间的攻击次数
            num_attacks = skill_duration / skill_actual_atk_interval
            
            # 计算总伤害和DPS
            total_damage = num_attacks * damage_per_hit
            dps = damage_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (清算)：
            # 持续时间: 30秒
            # 效果: 攻击力+170%，攻击速度+50，攻击时有50%的几率造成相当于攻击力185%的物理伤害
            
            skill_duration = 30
            skill_atk_boost_ratio = 1.70 # 攻击力+170%
            skill_atk_speed_boost = 50
            
            # 计算技能期间的实际攻击速度和攻击间隔
            skill_attack_speed = self.attack_speed + skill_atk_speed_boost
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 计算强化后的基础攻击力
            boosted_base_atk = self.final_base_atk * (1 + skill_atk_boost_ratio)
            
            # 计算每次攻击的期望伤害倍率
            # 每次攻击造成100%攻击力伤害，并有50%几率额外造成185%攻击力伤害
            # 期望倍率 = 1.0 (基础) + 0.5 * 1.85 (额外伤害期望)
            effective_hit_multiplier = 1.0 + (0.5 * 1.85)
            
            # 计算用于_calc_hit的最终攻击力数值
            skill_atk_val = boosted_base_atk * effective_hit_multiplier
            
            # 计算单次攻击的伤害（S3期间天赋1防御力降低层数按默认5层计算）
            damage_per_hit = self._calc_hit(skill_atk_val, enemy, def_reduction_stacks=self.talent1_max_stacks_normal)
            
            # 计算技能持续期间的攻击次数
            num_attacks = skill_duration / skill_actual_atk_interval
            
            # 计算总伤害和DPS
            total_damage = num_attacks * damage_per_hit
            dps = damage_per_hit / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)