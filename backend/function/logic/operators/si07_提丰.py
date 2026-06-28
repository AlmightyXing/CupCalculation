from backend.function.logic.base_operator import Operator
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage
from backend.function.logic.professions import Besieger # Corrected import

class Si07提丰(Besieger): # Corrected inheritance
    """
    干员：提丰
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：锐如兽牙 (连续攻击时逐渐无视敌人的防御力，最高无视其防御力的50%)
        # 根据规则，可叠加层数的天赋按最大层数计算，因此直接视为拥有50%无视防御
        self.ignore_def_ratio = 0.5
        
        # 天赋 2：重如沼泥 (技能期间对每个敌人首次造成伤害时，攻击力提升至160%)
        # 存储首次伤害的攻击力乘数，在技能计算中应用
        self.first_hit_atk_multiplier = 1.6
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑锐如兽牙天赋的无视防御）
        """
        # 提丰的天赋1是直接无视防御，而非概率无视
        return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.ignore_def_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻直接享受天赋1的50%无视防御
        # Besieger父类没有特殊的普攻逻辑，因此直接计算提丰的普攻伤害即可
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取基础攻击速度和实际攻击间隔
        base_attack_speed = self.attack_speed
        # Besieger的attack_interval为2.4，这里会正确继承
        actual_atk_interval = self.attack_interval * 100 / base_attack_speed
        
        if skill_index == 0:
            # 技能 1 (迅捷打击·γ型)：攻击力+45%，攻击速度+45，持续35秒
            skill_duration = 35
            atk_buff_ratio = 0.45
            atk_speed_buff = 45
            
            # 计算强化后的攻击力
            buffed_atk_val = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算强化后的攻击速度和实际攻击间隔
            skill_attack_speed = base_attack_speed + atk_speed_buff
            skill_actual_atk_interval = self.attack_interval * 100 / skill_attack_speed
            
            # 计算技能期间的普攻次数
            num_hits = skill_duration / skill_actual_atk_interval
            
            # 考虑天赋2：重如沼泥 (对每个敌人首次造成伤害时，攻击力提升至160%)
            # 第一次伤害享受1.6倍攻击力加成
            first_hit_damage = self._calc_hit(buffed_atk_val * self.first_hit_atk_multiplier, enemy)
            
            # 后续伤害使用常规强化攻击力
            subsequent_hit_damage = self._calc_hit(buffed_atk_val, enemy)
            
            # 计算总伤害
            total_damage = first_hit_damage + (num_hits - 1) * subsequent_hit_damage
            
            # DPS计算基于持续的强化普攻伤害
            dps = subsequent_hit_damage / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (冰原秩序)：攻击力+50%，每次攻击发射两支箭矢，持续20秒
            skill_duration = 20
            atk_buff_ratio = 0.50
            
            # 计算强化后的攻击力
            buffed_atk_val = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 攻击间隔不变
            skill_actual_atk_interval = actual_atk_interval
            
            # 计算技能期间的攻击次数
            num_attacks = skill_duration / skill_actual_atk_interval
            # 每次攻击发射两支箭矢，对单目标视为2次伤害
            num_damage_instances = num_attacks * 2 
            
            # 考虑天赋2：重如沼泥 (对每个敌人首次造成伤害时，攻击力提升至160%)
            # 第一次伤害实例享受1.6倍攻击力加成
            first_damage_instance = self._calc_hit(buffed_atk_val * self.first_hit_atk_multiplier, enemy)
            
            # 后续伤害实例使用常规强化攻击力
            subsequent_damage_instance = self._calc_hit(buffed_atk_val, enemy)
            
            # 计算总伤害
            total_damage = first_damage_instance + (num_damage_instances - 1) * subsequent_damage_instance
            
            # DPS计算基于持续的强化普攻伤害，每次攻击造成两次伤害
            dps = (2 * subsequent_damage_instance) / skill_actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (“永恒狩猎”)：攻击间隔大幅增大(+3.1)，攻击变为对标记目标发射一轮箭雨
            # 箭雨共造成5次相当于攻击力175%的物理伤害；攻击装有10发弹药
            
            skill_atk_interval_increase = 3.1
            skill_atk_multiplier = 1.75
            hits_per_shot = 5
            num_shots = 10 # 10发弹药
            
            # 计算技能期间的实际攻击间隔 (攻击间隔直接增加)
            skill_actual_atk_interval = (self.attack_interval + skill_atk_interval_increase) * 100 / base_attack_speed
            
            # 计算总伤害实例数
            total_damage_instances = num_shots * hits_per_shot
            
            # 计算每次伤害实例的基础攻击力
            base_damage_instance_atk_val = self.final_base_atk * skill_atk_multiplier
            
            # 考虑天赋2：重如沼泥 (对每个敌人首次造成伤害时，攻击力提升至160%)
            # 第一次伤害实例享受1.6倍攻击力加成
            first_damage_instance = self._calc_hit(base_damage_instance_atk_val * self.first_hit_atk_multiplier, enemy)
            
            # 后续伤害实例使用常规攻击力
            subsequent_damage_instance = self._calc_hit(base_damage_instance_atk_val, enemy)
            
            # 计算总伤害
            total_damage = first_damage_instance + (total_damage_instances - 1) * subsequent_damage_instance
            
            # 计算技能总持续时间
            skill_total_duration = num_shots * skill_actual_atk_interval
            
            # DPS计算
            dps = total_damage / skill_total_duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
