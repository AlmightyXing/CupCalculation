from backend.function.logic.professions import Executor
from backend.function.logic.formulas import calculate_physical_damage

class R109傀影(Executor):
    """
    干员：傀影
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：镜中虚影 (可以使用一个属性更强的虚影，虚影拥有和自己一样的技能，拥有独立的再部署时间(45s))
        # 此天赋主要影响虚影的机制，不直接修改傀影自身的攻击力、攻速等面板属性，因此不在此处进行数值修改。
        
        # 天赋 2：虚影精通 (虚影的再部署时间-10秒)
        # 此天赋影响虚影的再部署时间，不直接修改傀影自身的攻击力、攻速等面板属性，因此不在此处进行数值修改。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        计算单次普攻命中时的期望物理伤害。
        傀影的普攻为纯物理伤害，无特殊机制。
        """
        # Executor职业本身没有特殊的普攻倍率，因此直接计算物理伤害即可。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔会受到攻速加成影响
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (暗夜魅影)：部署后立即获得50%的物理闪避和可吸收相当于自己最大生命80%物理伤害的屏障，持续10秒
            # 此技能为防御/生存类技能，不造成伤害。
            total_damage = 0.0
            dps = 0.0
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (血色乐章)：部署后立即获得10层可叠加的攻击力+20%的增益（每攻击一次消耗一层）
            # 技能效果为10次攻击，每次攻击时攻击力提升20%。
            
            # 计算单次强化普攻的攻击力
            buffed_atk_per_hit = self.final_base_atk * (1 + 0.20)
            
            # 计算单次强化普攻的伤害
            damage_per_buffed_hit = calculate_physical_damage(buffed_atk_per_hit, enemy.current_def)
            
            # 总伤害为10次强化普攻的总和
            total_damage = damage_per_buffed_hit * 10
            
            # DPS为强化普攻的单次伤害除以实际攻击间隔
            # 此处DPS表示单次强化攻击的瞬时DPS，而非技能持续期间的平均DPS
            dps = damage_per_buffed_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (夜幕突袭)：部署后立即对周围所有敌人造成相当于攻击力300%的物理伤害
            # 此技能为瞬发爆发伤害。
            
            # 计算爆发伤害的攻击力
            burst_atk_val = self.final_base_atk * 3.0
            
            # 计算爆发伤害
            total_damage = calculate_physical_damage(burst_atk_val, enemy.current_def)
            
            # DPS为爆发伤害除以实际攻击间隔（瞬发技能的DPS计算方式，假设替代一次普攻）
            dps = total_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
