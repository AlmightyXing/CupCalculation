from backend.function.logic.professions import Trapmaster
from backend.function.logic.formulas import calculate_physical_damage

class Rs05艾拉(Trapmaster):
    """
    干员：艾拉
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：雷鸣地雷
        # 描述陷阱机制，不直接影响自身面板数值，但其“雷鸣地雷效果”是天赋2和技能2/3触发条件。
        # 为最大化伤害，在计算时假设敌人可能受到雷鸣地雷效果影响。
        
        # 天赋 2：“正中靶心”
        # 攻击有30%几率造成相当于攻击力150%的物理伤害，对受到雷鸣地雷效果影响的目标必定触发。
        self.talent2_prob_normal = 0.3  # 正常情况触发概率
        self.talent2_prob_landmine = 1.0 # 受到雷鸣地雷影响时触发概率
        self.talent2_dmg_multiplier = 1.5 # 触发时的伤害倍率
        
    def _calc_hit(self, atk_val: float, enemy, is_enemy_affected_by_landmine: bool = False, def_ignore_flat: float = 0.0, fragile_ratio: float = 0.0) -> float:
        """
        计算单次命中时的期望物理伤害，考虑天赋2“正中靶心”、平坦无视防御和脆弱效果。
        
        Args:
            atk_val (float): 当前攻击力。
            enemy: 敌人对象。
            is_enemy_affected_by_landmine (bool): 敌人是否受到雷鸣地雷效果影响，影响天赋2触发概率。
            def_ignore_flat (float): 平坦无视防御值。
            fragile_ratio (float): 脆弱效果比例（例如0.35表示35%脆弱）。
        
        Returns:
            float: 单次命中时的期望伤害。
        """
        # 确定天赋2的触发概率
        prob_talent2 = self.talent2_prob_landmine if is_enemy_affected_by_landmine else self.talent2_prob_normal
        
        # 计算触发天赋2时的伤害
        dmg_talent2 = calculate_physical_damage(atk_val * self.talent2_dmg_multiplier, enemy.current_def, def_ignore_flat=def_ignore_flat)
        
        # 计算未触发天赋2时的伤害
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def, def_ignore_flat=def_ignore_flat)
        
        # 计算期望伤害（考虑天赋2概率）
        expected_dmg = prob_talent2 * dmg_talent2 + (1 - prob_talent2) * dmg_normal
        
        # 应用脆弱效果
        return expected_dmg * (1 + fragile_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻时，为最大化伤害，假设敌人受到雷鸣地雷效果影响，使天赋2必定触发。
        return self._calc_hit(self.final_base_atk, enemy, is_enemy_affected_by_landmine=True)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔（未受技能攻速影响前）
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (眩目阻滞)
            # 被动效果为控制和命中率降低，主动效果为获得陷阱。
            # 不直接提供伤害加成或攻击次数，因此总伤和DPS为0。
            return {"total_damage": 0.0, "dps": 0.0}
            
        elif skill_index == 1:
            # 技能 2 (震荡坚守)
            # duration: 20秒
            # 主动效果：自身防御力+300%，攻击范围缩小，攻击对目标周围造成溅射物理伤害且无视其800的防御力。
            # 技能结束时获得一个陷阱。
            
            duration = 20.0
            def_ignore_flat = 800.0
            
            # 攻击力无加成
            atk_val = self.final_base_atk
            
            # 假设敌人受到雷鸣地雷效果影响，使天赋2必定触发
            single_hit_dmg = self._calc_hit(atk_val, enemy, 
                                             is_enemy_affected_by_landmine=True, 
                                             def_ignore_flat=def_ignore_flat)
            
            # 技能期间的攻击次数
            hits = duration / actual_atk_interval
            
            total_damage = single_hit_dmg * hits
            dps = single_hit_dmg / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (“博萨克风暴”)
            # duration: null (由子弹数决定)
            # 主动效果：攻击间隔缩短(-0.35)，攻击力+90%，优先攻击受到雷鸣地雷效果影响的敌人，
            # 攻击装有40发子弹，打完后技能结束。
            # 被动效果：陷阱触发时使周围所有目标停顿，移动速度降低80%并获得35%的脆弱效果，持续7秒。
            # 由于技能主动效果明确“优先攻击受到雷鸣地雷效果影响的敌人”，且被动有脆弱效果，
            # 因此计算时应考虑脆弱和天赋2的满触发。
            
            atk_buff_ratio = 0.90
            atk_interval_reduction = 0.35 # 攻击间隔缩短0.35秒
            fragile_ratio = 0.35 # 被动效果：35%脆弱
            bullet_count = 40
            
            # 计算技能期间的攻击力
            skill_atk_val = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 计算技能期间的实际攻击间隔
            # 实际攻击间隔 = (基准攻击间隔 - 技能缩短值) * 100 / (基准攻速 + 攻速加成)
            # self.attack_interval 是干员的基准攻击间隔，self.attack_speed 是包含了天赋加成的攻速值。
            # 确保攻击间隔不为负数，设置一个最小值（例如0.1秒）
            effective_base_atk_interval = max(0.1, self.attack_interval - atk_interval_reduction)
            actual_skill_atk_interval = effective_base_atk_interval * 100 / self.attack_speed
            
            # 技能明确指出“优先攻击受到雷鸣地雷效果影响的敌人”，所以天赋2必定触发
            # 且被动有35%脆弱效果
            single_hit_dmg = self._calc_hit(skill_atk_val, enemy, 
                                             is_enemy_affected_by_landmine=True, 
                                             fragile_ratio=fragile_ratio)
            
            total_damage = single_hit_dmg * bullet_count
            dps = single_hit_dmg / actual_skill_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)