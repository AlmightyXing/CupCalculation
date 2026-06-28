from backend.function.logic.professions import Marksman
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage # 导入所需的伤害计算公式

class Rs01灰烬(Marksman):
    """
    干员：灰烬
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：辅助装备 (部署后立即对攻击范围内一个敌人投掷闪光弹，使其和周围敌人晕眩4秒)
        # 天赋 2：突击手 (首次部署时部署费用-3，并在部署后立即获得17技力)
        # 这两个天赋主要提供部署时效果或控制，不直接修改干员的常驻攻击属性或普攻模式，
        # 因此在 apply_talents 中无需进行数值修改。
        # 技能2会触发天赋1的眩晕效果，这部分逻辑将在技能2的计算中体现。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 灰烬的普攻没有特殊天赋加成，直接使用基类的物理伤害计算
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (支援射击)：攻击力+15%，攻击变为2连击
            # 持续时间为null，视为永续技能，计算DPS
            atk_multiplier = 1.15
            hits_per_attack = 2 # 攻击变为2连击
            
            # 技能期间的强化攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier
            
            # 单次命中伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 每次攻击造成的总伤害 (2连击)
            damage_per_attack = single_hit_damage * hits_per_attack
            
            # 技能期间的DPS
            dps = damage_per_attack / actual_atk_interval
            
            # 永续技能 total_damage 为 0
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (突击战术)：立即触发第一天赋，攻击间隔大幅度缩短(-80%)，
            # 且攻击被晕眩目标时攻击力提高至250%，攻击装有31发子弹，打完后技能结束
            
            # 1. 立即触发第一天赋意味着目标被眩晕，因此攻击力提高至250%生效
            atk_bonus_stunned = 2.50
            enhanced_atk = self.final_base_atk * atk_bonus_stunned
            
            # 2. 攻击间隔大幅度缩短(-80%)
            # 原始基础攻击间隔: self.attack_interval (例如灰烬为1.0)
            # 技能期间的基础攻击间隔: 原始基础攻击间隔 * (1 - 0.80)
            skill_base_atk_interval = self.attack_interval * 0.20
            
            # 技能期间的实际攻击间隔 (考虑干员自身攻速加成)
            skill_actual_atk_interval = skill_base_atk_interval * 100 / self.attack_speed
            
            # 3. 攻击装有31发子弹
            bullet_count = 31
            
            # 单发子弹的伤害
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 技能期间的总伤害
            total_damage = single_hit_damage * bullet_count
            
            # 技能持续时间 = 子弹数 * 技能期间实际攻击间隔
            skill_duration = skill_actual_atk_interval * bullet_count
            
            # 技能期间的DPS
            dps = total_damage / skill_duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (攻坚榴弹)：向前发射破墙弹，对沿途敌人造成300%的物理伤害并向后较大力度推动；
            # 爆炸对周围造成400%的物理伤害（从低地撞到高台直接爆炸且造成800%的物理伤害）
            
            # 这是一个瞬发爆发伤害技能。
            # 1. 沿途伤害
            path_atk_multiplier = 3.0
            path_damage = calculate_physical_damage(self.final_base_atk * path_atk_multiplier, enemy.current_def)
            
            # 2. 爆炸伤害 (根据期望伤害原则，取常规400%，不考虑特殊800%条件)
            explosion_atk_multiplier = 4.0
            explosion_damage = calculate_physical_damage(self.final_base_atk * explosion_atk_multiplier, enemy.current_def)
            
            # 总伤害为沿途伤害和爆炸伤害之和 (对单个目标)
            total_damage = path_damage + explosion_damage
            
            # 瞬发伤害的DPS计算方式 (参考艾丽妮S1/S2范例)
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)