from backend.function.logic.professions import UnknownProfession
from backend.function.logic.formulas import calculate_physical_damage

class Pl08新约能天使(UnknownProfession):
    """
    干员：新约能天使
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1: 火力电台 (友方弹药消耗回血和召唤轰炸)
        # 此天赋描述的是对友方干员的辅助效果和外部触发的额外伤害，不直接修改新约能天使自身的攻击力、攻速等属性。
        # 因此，不在此处进行数值修改。
        
        # 天赋 2: 铳弹协约 (提升其他弹药类干员攻击力)
        # 此天赋是光环效果，提升其他干员的攻击力，不影响新约能天使自身的伤害输出。
        # 因此，不在此处进行数值修改。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 新约能天使的普攻没有特殊描述，按标准物理伤害计算
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 初始攻击间隔和攻击速度，可能被技能修改
        current_attack_interval = self.attack_interval
        current_attack_speed = self.attack_speed
        
        # 初始攻击力，可能被技能修改
        current_atk_val = self.final_base_atk

        total_damage = 0.0
        dps = 0.0

        if skill_index == 0:
            # 技能 1 (天空大扫除): 每次攻击造成攻击力250%的物理伤害，攻击装有8发弹药
            skill_atk_multiplier = 2.5
            skill_ammo_count = 8
            
            damage_per_hit = calculate_physical_damage(current_atk_val * skill_atk_multiplier, enemy.current_def)
            total_damage = damage_per_hit * skill_ammo_count
            
            # 技能期间DPS = 单次强化普攻伤害 / 实际攻击间隔
            actual_atk_interval = current_attack_interval * 100 / current_attack_speed
            dps = damage_per_hit / actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (开火成瘾症): 攻击间隔降低(-0.7)，每次攻击造成攻击力300%的物理伤害
            # 攻击装有35发弹药，如果成功偷取攻击速度则额外获得5发弹药 (总计40发)
            
            # 攻击间隔降低
            modified_attack_interval = current_attack_interval - 0.7
            # 确保攻击间隔不为负或零
            if modified_attack_interval <= 0:
                modified_attack_interval = 0.1 # 设定一个极小值以避免除零错误
            
            skill_atk_multiplier = 3.0
            skill_ammo_count = 35 + 5 # 假设成功偷取攻速，获得最大弹药数
            
            damage_per_hit = calculate_physical_damage(current_atk_val * skill_atk_multiplier, enemy.current_def)
            total_damage = damage_per_hit * skill_ammo_count
            
            # 计算实际攻击间隔，使用修改后的攻击间隔
            actual_atk_interval = modified_attack_interval * 100 / current_attack_speed
            dps = damage_per_hit / actual_atk_interval
            
        elif skill_index == 2:
            # 技能 3 (使命必达！): 攻击力+30%，每次攻击变为相当于攻击力160%的5连击
            # 瞬发伤害：立刻对该处造成一次相当于攻击力250%的物理溅射伤害 (假设触发一次)
            # 攻击装有50发弹药，每次攻击消耗5发 (总计10次攻击循环)
            
            # 攻击力增益先触发
            current_atk_val = self.final_base_atk * (1 + 0.30)
            
            # 瞬发伤害 (使用强化后的攻击力)
            initial_burst_multiplier = 2.50
            initial_burst_damage = calculate_physical_damage(current_atk_val * initial_burst_multiplier, enemy.current_def)
            
            # 每次攻击循环的伤害 (5连击，每击160%攻击力，使用强化后的攻击力)
            hit_multiplier_per_strike = 1.60
            strikes_per_attack_cycle = 5
            
            damage_per_strike = calculate_physical_damage(current_atk_val * hit_multiplier_per_strike, enemy.current_def)
            damage_per_attack_cycle = damage_per_strike * strikes_per_attack_cycle
            
            # 总攻击循环次数
            total_ammo = 50
            ammo_consumed_per_cycle = 5
            skill_attack_cycles = total_ammo // ammo_consumed_per_cycle # 10次攻击循环
            
            total_damage = initial_burst_damage + (damage_per_attack_cycle * skill_attack_cycles)
            
            # 技能期间DPS = 单次攻击循环伤害 / 实际攻击间隔
            actual_atk_interval = current_attack_interval * 100 / current_attack_speed
            dps = damage_per_attack_cycle / actual_atk_interval
            
        else:
            return super().calculate_skill_damage(enemy, skill_index, target_count)

        return {"total_damage": total_damage, "dps": dps}