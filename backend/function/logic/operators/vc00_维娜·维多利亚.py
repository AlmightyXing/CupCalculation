from backend.function.logic.professions import ArtsFighter
from backend.function.logic.formulas import calculate_arts_damage, calculate_true_damage

class Vc00维娜·维多利亚(ArtsFighter):
    """
    干员：维娜·维多利亚
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：诸王的叹息
        # "自身与周围8格友方单位受到的物理伤害减少20%" - 此为防御性天赋，不影响维娜自身伤害计算。
        # "且此范围内每个友方单位使维娜攻击力+5%"
        # 根据规则，可叠加层数的天赋按最大层数计算。周围8格友方单位，即最多8个友方单位。
        # 攻击力提升 = 8 * 5% = 40%
        self.final_base_atk *= (1 + 0.05 * 8)

        # 天赋 2：无拘的锋芒
        # "对每个敌人首次造成伤害时，使其战栗4秒"
        # "战栗"效果未量化为直接的伤害倍率，且通常为控制或受击效果，不直接计入维娜的攻击力或伤害倍率。
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 维娜·维多利亚是“术战者”，攻击造成法术伤害。
        # ArtsFighter父类特性即为攻击造成法术伤害，但父类未覆写calculate_normal_hit，
        # 因此此处需要显式覆写以确保计算法术伤害。
        return calculate_arts_damage(self.final_base_atk, enemy.current_res)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (重铸晖光)："下次攻击对四周所有地面敌人额外造成相当于攻击力180%的真实伤害"
            # 这是一个“下次攻击”技能，触发一次。
            
            # 普攻部分（法术伤害）
            normal_arts_hit = self.calculate_normal_hit(enemy)
            
            # 额外真实伤害部分
            true_damage_atk_val = self.final_base_atk * 1.80
            additional_true_damage = calculate_true_damage(true_damage_atk_val, enemy)
            
            total_damage = normal_arts_hit + additional_true_damage
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (进赴故土)：
            # "被动效果：天赋一生效范围内若有2个及以上友方单位，维娜技力回复速度+0.5/秒" - 不影响伤害计算。
            # "自动开启：攻击范围延长，攻击力+180%，攻击目标数+1，持续时间无限"
            
            # 永续技能，总伤害为0，重点计算DPS。
            # 攻击力提升：+180%
            skill_atk_multiplier = 1 + 1.80
            reinforced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 伤害类型仍为法术伤害
            single_hit_damage = calculate_arts_damage(reinforced_atk, enemy.current_res)
            
            return {"total_damage": 0, "dps": single_hit_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (俱以我之名)：
            # "立即在天赋一生效范围内可部署地面召唤“黄金盟誓”" - 不计入维娜自身伤害。
            # "技能期间可攻击被天赋一生效范围友方单位阻挡的敌人" - 攻击范围/目标条件，不直接影响伤害数值。
            # "攻击力+190%，攻击目标数+3，攻击间隔缩短(-0.25)，攻击时伤害类型变为真实"
            
            duration = 25 # 技能持续时间
            
            # 攻击力提升：+190%
            skill_atk_multiplier = 1 + 1.90
            reinforced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 攻击间隔缩短：-0.25
            # 原始攻击间隔 self.attack_interval 为 1.25 (来自ArtsFighter)
            skill_attack_interval_base = self.attack_interval - 0.25 # 1.25 - 0.25 = 1.0
            
            # 计算技能期间的实际攻击间隔
            actual_atk_interval_skill = skill_attack_interval_base * 100 / self.attack_speed
            
            # 伤害类型变为真实伤害
            single_hit_damage = calculate_true_damage(reinforced_atk, enemy)
            
            # 计算技能持续期间的攻击次数
            num_hits = (duration or 0) / actual_atk_interval_skill
            
            total_damage = num_hits * single_hit_damage
            dps = single_hit_damage / actual_atk_interval_skill
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
