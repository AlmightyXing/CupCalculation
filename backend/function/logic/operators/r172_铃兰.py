from backend.function.logic.professions import DecelBinder
from backend.function.logic.formulas import calculate_arts_damage

class R172铃兰(DecelBinder):
    """
    干员：铃兰
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关属性
        self.fragile_effect_ratio = 0.0 # 脆弱效果比例，默认为0
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：技力光环·辅助 (在场时所有【辅助】干员的技力自然回复速度+0.4/秒)
        # 此天赋为光环效果，不直接影响铃兰自身的伤害计算，故在此处忽略。
        
        # 天赋 2：画地为牢 (攻击范围内被停顿的敌人在下一瞬间起还会受到等长时间的20%的脆弱效果)
        # 铃兰的攻击自带停顿效果（凝滞师特性），因此此天赋的脆弱效果对铃兰自身造成的伤害是常驻的。
        self.fragile_effect_ratio = 0.20
        
    def _calc_arts_hit(self, atk_val: float, enemy, current_fragile_ratio: float) -> float:
        """
        计算单次命中时的期望法术伤害（考虑脆弱效果）
        """
        # 脆弱效果是敌人受到的伤害增加，直接乘以 (1 + current_fragile_ratio)
        # 铃兰造成法术伤害，使用敌人的法术抗性 (current_res)
        base_damage = calculate_arts_damage(atk_val, enemy.current_res)
        return base_damage * (1 + current_fragile_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻造成法术伤害，并考虑天赋2的脆弱效果
        # 凝滞师特性为攻击造成法术伤害，此处的覆写符合职业特性。
        return self._calc_arts_hit(self.final_base_atk, enemy, self.fragile_effect_ratio)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 记录原始攻击速度和脆弱效果比例，以便在技能计算中使用
        original_attack_speed = self.attack_speed
        current_fragile_ratio = self.fragile_effect_ratio # 技能期间可能改变，这里先取初始值

        # 实际攻击间隔，基于当前攻击速度
        actual_atk_interval = self.attack_interval * 100 / original_attack_speed
        
        total_damage = 0.0
        dps = 0.0

        if skill_index == 0:
            # 技能 1 (全力以赴)：攻击力+80%，攻击速度+30，持续30秒
            skill_duration = 30
            
            # 应用技能增益
            buffed_atk = self.final_base_atk * (1 + 0.80)
            buffed_attack_speed = original_attack_speed + 30
            
            # 计算增益后的实际攻击间隔
            buffed_actual_atk_interval = self.attack_interval * 100 / buffed_attack_speed
            
            # 计算技能持续期间的普攻次数
            num_hits = skill_duration / buffed_actual_atk_interval
            
            # 计算单次普攻伤害（考虑技能增益和天赋脆弱效果）
            damage_per_hit = self._calc_arts_hit(buffed_atk, enemy, current_fragile_ratio)
            
            total_damage = num_hits * damage_per_hit
            dps = damage_per_hit / buffed_actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (儿时的舞乐)：攻击力+60%，可以同时攻击3个敌方单位，永续
            # "可以同时攻击3个敌方单位" 不影响单目标总伤计算，严格遵守单目标原则
            
            # 应用技能增益
            buffed_atk = self.final_base_atk * (1 + 0.60)
            
            # 计算单次普攻伤害（考虑技能增益和天赋脆弱效果）
            damage_per_hit = self._calc_arts_hit(buffed_atk, enemy, current_fragile_ratio)
            
            # 永续技能的总伤为0，重点计算DPS
            total_damage = 0.0
            dps = damage_per_hit / actual_atk_interval # 技能不改变攻速，使用原始攻击间隔
            
        elif skill_index == 2:
            # 技能 3 (狐火渺然)：停止攻击，攻击范围扩大，第二天赋效果提升至2倍，持续35秒
            # "停止攻击" 意味着铃兰自身在此技能期间不造成任何伤害。
            # "第二天赋效果提升至2倍" (脆弱效果提升至40%) 是对敌人的debuff，会提高其他干员对敌人的伤害，
            # 但不属于铃兰自身造成的伤害，因此在计算铃兰个人伤害时，此技能的总伤和DPS均为0。
            total_damage = 0.0
            dps = 0.0
            
        return {"total_damage": total_damage, "dps": dps}
