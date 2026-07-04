from backend.function.logic.professions import CoreCaster
from backend.function.logic.formulas import calculate_arts_damage # 导入法术伤害计算公式

class Cb88霍尔海雅(CoreCaster):
    """
    干员：霍尔海雅
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.atk_boost_vs_aerial = 1.0 # 默认对空攻击力倍率，由天赋修改
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：传承终焉 (攻击空中目标时攻击力提升至120%)
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑。
        # 因此，在计算伤害时，我们假设目标是空中单位，以应用此攻击力加成。
        self.atk_boost_vs_aerial = 1.2
        # "并使其特殊能力失效3秒" - 此为控制效果，不影响伤害计算，故忽略。
        
        # 天赋 2：曾有羽翼 (攻击范围内所有生命值高于80%的敌人失重)
        # 此为控制效果，不影响伤害计算，故忽略。
        
    def _calc_arts_hit(self, base_atk_val: float, enemy, is_aerial: bool = True) -> float:
        """
        计算单次命中时的期望法术伤害（考虑对空天赋）。
        is_aerial: 默认为True，因为天赋对空有加成，计算期望伤害时取最大值。
        """
        current_atk = base_atk_val
        if is_aerial:
            current_atk *= self.atk_boost_vs_aerial
            
        return calculate_arts_damage(current_atk, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻默认考虑对空加成，以计算最大期望伤害
        return self._calc_arts_hit(self.final_base_atk, enemy, is_aerial=True)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取干员的基础攻击间隔（不受技能影响的原始值）
        base_atk_interval_stat = self.attack_interval 
        
        # 计算实际攻击间隔（考虑攻速加成，未考虑技能对间隔的修改）
        actual_atk_interval = base_atk_interval_stat * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (但为求索)：下次攻击额外攻击一个目标并造成相当于攻击力300%的法术伤害
            # 这是一个瞬发技能，只计算单次爆发伤害。
            # 规则：严禁在代码中乘以任何目标数。因此，忽略“额外攻击一个目标”的描述，只计算对单个目标的伤害。
            skill_atk_multiplier = 3.0
            
            # 瞬发伤害，使用强化后的攻击力（包含信赖和对空天赋）
            enhanced_atk_val = self.final_base_atk * skill_atk_multiplier
            total_damage = self._calc_arts_hit(enhanced_atk_val, enemy, is_aerial=True)
            
            # 瞬发技能的DPS计算方式：总伤 / 普攻间隔（因为是替代一次普攻）
            dps = total_damage / actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (群星逶迤)：攻击变为攻击力45%的9连发，随机攻击范围内的目标
            # 持续时间: 16秒
            skill_duration = 16
            skill_atk_multiplier = 0.45
            hits_per_attack_cycle = 9 # 9连发
            
            # 计算单次攻击循环（9连发）对单个目标的伤害
            # 规则：严禁乘以目标数。对于多段伤害，假设所有段数都命中同一个目标，以计算单目标最大伤害。
            enhanced_atk_val_per_hit = self.final_base_atk * skill_atk_multiplier
            damage_per_hit = self._calc_arts_hit(enhanced_atk_val_per_hit, enemy, is_aerial=True)
            damage_per_attack_cycle = damage_per_hit * hits_per_attack_cycle
            
            # 计算技能持续期间能打出的攻击循环次数
            num_attacks_during_skill = skill_duration / actual_atk_interval
            total_damage = damage_per_attack_cycle * num_attacks_during_skill
            
            # 计算技能期间的DPS
            dps = damage_per_attack_cycle / actual_atk_interval
            
        elif skill_index == 2:
            # 技能 3 (博览者的狂语)：攻击范围扩大，攻击间隔延长(+1.4)，攻击变为向前吹出平行的旋风...
            # 造成最低280%、最高420%攻击力的法术伤害
            # 持续时间: 45秒
            skill_duration = 45
            atk_interval_increase = 1.4
            
            # 攻击间隔延长，计算新的实际攻击间隔
            modified_atk_interval_stat = base_atk_interval_stat + atk_interval_increase
            modified_actual_atk_interval = modified_atk_interval_stat * 100 / self.attack_speed
            
            # 规则：天赋对提高伤害有帮助，均纳入考虑。因此，伤害取最大值 (420%)
            skill_atk_multiplier = 4.2 
            
            # 计算单次攻击（旋风）对单个目标的伤害
            enhanced_atk_val = self.final_base_atk * skill_atk_multiplier
            damage_per_attack = self._calc_arts_hit(enhanced_atk_val, enemy, is_aerial=True)
            
            # 计算技能持续期间能打出的攻击次数
            num_attacks_during_skill = skill_duration / modified_actual_atk_interval
            total_damage = damage_per_attack * num_attacks_during_skill
            
            # 计算技能期间的DPS
            dps = damage_per_attack / modified_actual_atk_interval
            
        return {"total_damage": total_damage, "dps": dps}