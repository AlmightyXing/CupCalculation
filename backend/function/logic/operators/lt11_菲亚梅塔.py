from backend.function.logic.professions import Artilleryman # '炮手' 对应 Artilleryman 职业
from backend.function.logic.formulas import calculate_physical_damage

class Lt11菲亚梅塔(Artilleryman):
    """
    干员：菲亚梅塔
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：陈述苦难 (自身生命会不断流失；生命值高于50%时获得25%攻击力的精力充沛；高于80%效果翻倍)
        # 按照最大收益计算，假设生命值高于80%，获得25% * 2 = 50%攻击力加成
        self.final_base_atk *= (1 + 0.50)
        
        # 天赋 2：宣告终局 (技能持续期间外，攻击速度+27)
        # 这个天赋影响普攻和不带攻速加成的技能的实际攻击间隔
        self.attack_speed += 27
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 菲亚梅塔是炮手，攻击造成群体物理伤害，但计算时仍按单个目标计算伤害
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，考虑天赋2的攻速加成
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1: “你须直面”
            # 描述：攻击距离+1，攻击力+100%
            # 持续时间：30秒
            
            duration = 30
            skill_atk_multiplier = 1 + 1.00 # 攻击力+100%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            # 计算强化后单次普攻伤害
            damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的普攻次数
            hits_during_skill = duration / actual_atk_interval
            # 计算总伤害
            total_damage = hits_during_skill * damage_per_hit
            # 计算DPS
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2: “你须愧悔” (瞬发技能)
            # 描述：向前发射灼痕弹且每飞行一段距离在弹道上留下灼痕，
            # 到达攻击范围最远距离时爆炸造成400%的物理伤害；
            # 之后灼痕依次爆炸造成200%的物理伤害
            # 假设“灼痕依次爆炸”为一次额外的200%伤害，共计一次400%和一次200%伤害。
            
            # 主爆炸伤害
            main_explosion_atk = self.final_base_atk * 4.0
            main_explosion_dmg = calculate_physical_damage(main_explosion_atk, enemy.current_def)
            
            # 灼痕爆炸伤害 (假设为一次)
            scorched_mark_atk = self.final_base_atk * 2.0
            scorched_mark_dmg = calculate_physical_damage(scorched_mark_atk, enemy.current_def)
            
            # 瞬发技能的总伤害为所有爆发伤害之和
            total_damage = main_explosion_dmg + scorched_mark_dmg
            # 瞬发技能的DPS计算方式
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3: “你须偿还” (永续技能)
            # 描述：持续固定攻击范围内正前方最远一格，爆炸范围扩大，
            # 攻击力提升至125%，对目标位置附近小范围内的敌人攻击力额外提升至220%，持续时间无限
            # 永续技能 total_damage 为 0，主要计算 dps
            # 按照最大收益计算，攻击力提升至220%
            
            skill_atk_multiplier = 2.20 # 攻击力提升至220%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            # 计算强化后单次普攻伤害
            damage_per_hit = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            total_damage = 0 # 永续技能总伤为0
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)