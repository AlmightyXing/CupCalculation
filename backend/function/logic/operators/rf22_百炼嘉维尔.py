from backend.function.logic.professions import Centurion
from backend.function.logic.formulas import calculate_physical_damage

class Rf22百炼嘉维尔(Centurion):
    """
    干员：百炼嘉维尔
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 信赖防御力，虽然不直接用于自身伤害计算，但作为干员属性一并初始化
        self.trust_def = self.raw_data.get("confidence_def", 0)
        self.final_base_def = self.base_def + self.trust_def
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：战地巨斧 (Battlefield Great Axe)
        # "攻击力和防御力提升10%，每再阻挡一个敌人提升4%"
        # 规则：按最大层数叠加。
        # 百炼嘉维尔（强攻手）基础阻挡数为1。技能3可使阻挡数+2，达到最大阻挡3。
        # 因此，最大额外阻挡敌人数量为 3 - 1 = 2。
        # 最大攻击力/防御力提升比例 = 10% (基础) + 2 * 4% (额外) = 18%。
        talent1_bonus_ratio = 0.18
        self.final_base_atk *= (1 + talent1_bonus_ratio)
        # self.final_base_def *= (1 + talent1_bonus_ratio) # 防御力提升不影响自身伤害输出，故此处不修改，但如果需要计算承伤则应修改。
        
        # 天赋 2：医学背景 (Medical Background)
        # "受到的治疗效果提升20%，生命值低于一半时提升至40%"
        # 此天赋影响治疗效果，不直接影响伤害输出，故在伤害计算中忽略。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 百炼嘉维尔是强攻手，造成物理伤害。
        # 强攻手特性“同时攻击阻挡的所有敌人”影响的是目标数量，而非单次攻击的伤害倍率。
        # 因此，单次普攻的伤害计算与基类Operator的物理伤害计算一致。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 技能期间的攻击速度，初始为干员基础攻击速度
        current_attack_speed = self.attack_speed
        
        # 技能期间的攻击力乘数，初始为1.0
        skill_atk_multiplier = 1.0
        
        # 技能持续时间
        duration = 0
        
        # 技能期间的攻击速度加成（直接加到攻速值上）
        skill_atk_speed_bonus = 0 
        
        if skill_index == 0:
            # 技能 1 (精准痛击)：攻击力+80%，每次伤害治疗自身相当于造成伤害40%的生命值
            duration = 25
            skill_atk_multiplier = 1.80 # 1 + 0.80
            # 治疗效果不影响伤害输出，忽略。
            
        elif skill_index == 1:
            # 技能 2 (链锯强袭)：攻击范围扩大，攻击力+180%，防御力+50%
            duration = 40
            skill_atk_multiplier = 2.80 # 1 + 1.80
            # 攻击范围扩大、防御力+50%和拖拽效果不影响自身伤害输出，忽略。
            
        elif skill_index == 2:
            # 技能 3 (丛林之魂)：攻击力+140%，攻击速度+100，阻挡数+2
            duration = 25
            skill_atk_multiplier = 2.40 # 1 + 1.40
            skill_atk_speed_bonus = 100
            # 阻挡数+2、受伤害减免和延后生命流失不影响自身伤害输出，忽略。
            
        else:
            # 如果技能索引不匹配，调用基类方法
            return super().calculate_skill_damage(enemy, skill_index, target_count)

        # 应用技能期间的攻击速度加成
        current_attack_speed += skill_atk_speed_bonus
        
        # 计算实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / current_attack_speed
        
        # 计算技能期间的强化攻击力
        enhanced_atk_val = self.final_base_atk * skill_atk_multiplier
        
        # 计算单次强化普攻的伤害
        # 强攻手特性“同时攻击阻挡的所有敌人”影响的是目标数量，而非单次攻击的伤害倍率。
        # 因此，单次强化普攻的伤害计算与基类Operator的物理伤害计算一致。
        single_hit_damage = calculate_physical_damage(enhanced_atk_val, enemy.current_def)
        
        # 计算技能期间的总伤害和DPS
        if duration > 0:
            # 技能持续期间的普攻次数
            hits_during_skill = duration / actual_atk_interval
            total_damage = single_hit_damage * hits_during_skill
            dps = single_hit_damage / actual_atk_interval
        else: 
            # 对于永续技能或瞬发技能（百炼嘉维尔的技能都有duration），
            # 如果是永续，total_damage为0，dps为强化普攻dps。
            # 如果是瞬发，total_damage为爆发伤害，dps为爆发伤害/实际攻击间隔。
            # 百炼嘉维尔的技能都是有duration的增益类技能，所以上面的if分支会执行。
            total_damage = 0 
            dps = single_hit_damage / actual_atk_interval
            
        return {"total_damage": total_damage, "dps": dps}
