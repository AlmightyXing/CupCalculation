from backend.function.logic.professions import HeavyShooter
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Mh05焰狐龙梓兰(HeavyShooter):
    """
    干员：焰狐龙梓兰
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：强击瓶专家
        # "部署后首次开启技能时，接下来50次攻击的攻击力提升至115%"
        # 这是一个条件性增益，在技能伤害计算时，我们假设条件满足且攻击次数在50次内。
        self.talent_1_atk_buff_multiplier = 1.15
        self.talent_1_buff_hit_count = 50 

        # 天赋 2：翔虫机动
        # "部署至上次部署位置周围时，30秒内攻击力+15%"
        # 为了最大化伤害计算，我们假设此条件已满足，直接将攻击力加成应用到最终基础攻击力上。
        # "再部署时间(-15)秒且不提高部署费用" 和 "可以部署在近战位" 不影响伤害计算。
        self.final_base_atk *= (1 + 0.15)
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻为物理伤害。
        # 天赋2 (翔虫机动) 的攻击力加成已在 apply_talents 中应用到 self.final_base_atk。
        # 天赋1 (强击瓶专家) 仅在首次开启技能后的特定攻击中生效，不影响默认普攻。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 技能基础攻击力，已包含天赋2的加成
        skill_base_atk = self.final_base_atk
        
        # 为了最大化伤害，假设当前技能是“部署后首次开启的技能”，
        # 且技能的所有攻击次数都在天赋1的50次攻击范围内。
        # 因此，将天赋1的攻击力乘数应用到技能攻击力上。
        current_atk_for_skill = skill_base_atk * self.talent_1_atk_buff_multiplier
        
        total_damage = 0.0
        
        if skill_index == 0:
            # 技能 1 (刚射)：
            # "发射4支攻击力160%的箭矢，若还有充能则额外消耗1层施展刚连射：发射5支攻击力200%的箭矢"
            # 为最大化伤害，假设“刚连射”总是触发。
            # 总计 4 + 5 = 9 次攻击。9次攻击均在天赋1的50次范围内。
            
            # 第一部分：刚射 (4次攻击，每次160%攻击力)
            dmg_part1 = calculate_physical_damage(current_atk_for_skill * 1.6, enemy.current_def) * 4
            
            # 第二部分：刚连射 (5次攻击，每次200%攻击力)
            dmg_part2 = calculate_physical_damage(current_atk_for_skill * 2.0, enemy.current_def) * 5
            
            total_damage = dmg_part1 + dmg_part2
            
            # 这是一个瞬发伤害技能
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (飞翔瞪射)：
            # "立刻起飞并对前方范围的所有目标射击3次，分别射出3、4、5支攻击力提升至180%的箭矢；
            # 之后降落并对前方小范围内的所有敌人造成攻击力300%的物理伤害"
            # 总计 (3+4+5) = 12 次攻击，每次180%攻击力；外加 1 次攻击，300%攻击力。
            # 总计 13 次攻击。13次攻击均在天赋1的50次范围内。
            
            # 第一部分：空中射击 (12次攻击，每次180%攻击力)
            dmg_part1 = calculate_physical_damage(current_atk_for_skill * 1.8, enemy.current_def) * 12
            
            # 第二部分：落地伤害 (1次攻击，300%攻击力)
            dmg_part2 = calculate_physical_damage(current_atk_for_skill * 3.0, enemy.current_def) * 1
            
            total_damage = dmg_part1 + dmg_part2
            
            # 这是一个瞬发伤害技能
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (龙之箭)：
            # "蓄力3秒后射出直线飞行的贯穿箭矢，每飞行一段距离都会对周围所有敌人造成攻击力360%的物理伤害和攻击力60%的法术伤害"
            # 技能描述未明确箭矢对单个目标造成伤害的次数。
            # 为进行计算，我们假设箭矢对单个目标造成3次伤害（这是此类技能常见的默认假设）。
            # 3次攻击均在天赋1的50次范围内。
            
            # 单次伤害实例的物理部分
            single_hit_phys_dmg = calculate_physical_damage(current_atk_for_skill * 3.6, enemy.current_def)
            # 单次伤害实例的法术部分
            single_hit_arts_dmg = calculate_arts_damage(current_atk_for_skill * 0.6, enemy.current_res)
            
            # 假设对单个目标造成3次伤害
            total_damage = (single_hit_phys_dmg + single_hit_arts_dmg) * 3
            
            # 这是一个瞬发伤害技能（在蓄力后）
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)