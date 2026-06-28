from backend.function.logic.professions import Dreadnought
from backend.function.logic.formulas import calculate_physical_damage, calculate_true_damage

class Kz01耀骑士临光(Dreadnought):
    """
    干员：耀骑士临光
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1: 不畏苦暗 (部署时对周围四格敌人造成80%攻击力的真实伤害并晕眩3秒，上一名部署干员势力为【卡西米尔】时额外造成一次伤害)
        # 此天赋为部署时的一次性效果，不影响普攻或技能期间的持续伤害计算，因此不在此处修改干员属性。

        # 天赋 2: 破晓 (攻击无视敌人20%的防御力)
        self.def_ignore_ratio = 0.2
        
    def _calc_physical_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑“破晓”天赋的无视防御）
        """
        return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.def_ignore_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻为物理伤害，受“破晓”天赋影响
        # Dreadnought父类没有特殊的普攻逻辑，因此直接实现耀骑士临光的普攻逻辑即可。
        return self._calc_physical_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员当前攻击速度（已包含天赋加成）
        current_attack_speed = self.attack_speed 
        # 计算实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / current_attack_speed
        
        total_damage = 0.0
        dps = 0.0

        if skill_index == 0:
            # 技能 1: 灿焰长刃 (攻击范围扩大，攻击力+70%，攻击速度+50，持续时间无限)
            # 永续技能，total_damage 为 0，主要计算 DPS。
            
            # 应用技能增益
            skill_atk_multiplier = 1 + 0.70
            skill_attack_speed_bonus = 50
            
            # 计算技能期间的有效攻击力
            effective_atk = self.final_base_atk * skill_atk_multiplier
            
            # 计算技能期间的实际攻击速度
            skill_current_attack_speed = current_attack_speed + skill_attack_speed_bonus
            skill_actual_atk_interval = self.attack_interval * 100 / skill_current_attack_speed
            
            # 计算单次普攻伤害（物理伤害，受天赋破甲影响）
            single_hit_damage = self._calc_physical_hit(effective_atk, enemy)
            
            dps = single_hit_damage / skill_actual_atk_interval
            total_damage = 0 # 永续技能总伤为0
            
        elif skill_index == 1:
            # 技能 2: 逐夜烁光 (被动效果：部署不消耗部署位。部署后攻击力+160%，获得4层护盾。技能结束后自动撤退，本次再部署时间延长25%，上一名部署干员势力为【卡西米尔】时本次再部署时间不再延长)
            # 部署型技能，持续至撤退，计算方式类似永续技能，主要计算 DPS。
            
            # 应用技能增益
            skill_atk_multiplier = 1 + 1.60
            
            # 计算技能期间的有效攻击力
            effective_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能描述中未提及攻速加成，沿用干员基础（含天赋）攻速
            
            # 计算单次普攻伤害（物理伤害，受天赋破甲影响）
            single_hit_damage = self._calc_physical_hit(effective_atk, enemy)
            
            dps = single_hit_damage / actual_atk_interval
            total_damage = 0 # 部署型技能总伤为0
            
        elif skill_index == 2:
            # 技能 3: 耀阳颔首 (在周围四格可部署地面召唤一把"耀阳"对周围敌人造成110%耀骑士临光攻击力的真实伤害并晕眩3秒，自身攻击范围扩大，攻击力+140%、防御力+100%，攻击自身与"耀阳"阻挡的单位时伤害类型变为真实)
            skill_duration = 25
            
            # 应用技能增益（根据规则，增益先触发，爆发伤害使用强化后的攻击力）
            skill_atk_multiplier = 1 + 1.40
            
            # 计算技能期间的有效攻击力
            effective_atk_during_skill = self.final_base_atk * skill_atk_multiplier
            
            # 1. 初始爆发伤害（来自“耀阳”的真实伤害）
            # 爆发伤害使用强化后的攻击力计算
            burst_damage_multiplier = 1.10
            burst_damage = calculate_true_damage(effective_atk_during_skill * burst_damage_multiplier)
            
            total_damage += burst_damage
            
            # 2. 技能持续期间的普攻伤害
            # “攻击自身与"耀阳"阻挡的单位时伤害类型变为真实”，计算时假设条件满足
            
            # 计算单次普攻伤害（真实伤害）
            single_hit_damage_skill = calculate_true_damage(effective_atk_during_skill)
            
            # 计算技能持续期间的普攻次数
            num_attacks = skill_duration / actual_atk_interval
            
            total_damage += single_hit_damage_skill * num_attacks
            
            dps = total_damage / skill_duration
            
        return {"total_damage": total_damage, "dps": dps}
