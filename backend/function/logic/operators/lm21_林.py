from backend.function.logic.professions import PhalanxCaster
from backend.function.logic.formulas import calculate_arts_damage

class Lm21林(PhalanxCaster):
    """
    干员：林
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：计出万全 (琉璃璧相关，被动触发伤害，且S3的触发条件是“击倒敌人”，难以量化为单次攻击的期望伤害，
        # 且伤害目标为“周围所有敌人”，不计入单目标总伤/DPS)
        # 天赋 2：韬光 (技力回复，不影响伤害)
        # 林的天赋不直接修改攻击力、攻速等面板属性，也不提供直接的攻击伤害加成。
        pass
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害
        """
        return calculate_arts_damage(atk_val, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 阵法术师的特性是“通常时不攻击”，只在技能开启时攻击。
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取技能数据
        skill_data = self.raw_data["skills"][skill_index]
        skill_duration = skill_data.get("duration") # duration可以为null (永续技能)

        # 基础攻击间隔和当前攻速
        base_attack_interval = self.attack_interval # 来自JSON的atk_time
        current_attack_speed = self.attack_speed # 默认100，可能被天赋或技能修改

        # 默认的实际攻击间隔 (在没有技能修改攻击间隔或攻速的情况下)
        actual_atk_interval = base_attack_interval * 100 / current_attack_speed
        
        total_damage = 0.0
        dps = 0.0

        if skill_index == 0:
            # 技能 1 (玲珑)：永续技能，攻击间隔略微增大(+1.0)，攻击力+60%
            
            # 攻击间隔修改
            skill0_modified_atk_interval = base_attack_interval + 1.0
            skill0_actual_atk_interval = skill0_modified_atk_interval * 100 / current_attack_speed
            
            # 攻击力加成
            buffed_atk = self.final_base_atk * (1 + 0.60)
            
            # 单次攻击伤害
            single_hit_dmg = self._calc_arts_hit(buffed_atk, enemy)
            
            # 永续技能，总伤为0，DPS为单次攻击伤害 / 实际攻击间隔
            total_damage = 0.0
            dps = single_hit_dmg / skill0_actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (荫庇)：持续25秒，攻击速度+130，自身不容易受到敌人攻击，友方享受第一天赋效果
            # 此技能本身不使林进行攻击，也不直接提供攻击力加成或爆发伤害。
            # 视为纯粹的辅助/生存技能，不产生直接伤害。
            total_damage = 0.0
            dps = 0.0
            
        elif skill_index == 2:
            # 技能 3 (流光乍裂)：持续30秒，攻击力+200%
            
            # 攻击力加成
            buffed_atk = self.final_base_atk * (1 + 2.00)
            
            # 单次攻击伤害
            single_hit_dmg = self._calc_arts_hit(buffed_atk, enemy)
            
            # 技能持续期间的攻击次数
            # S3没有修改攻击间隔或攻速，所以使用默认的actual_atk_interval
            if skill_duration is not None and skill_duration > 0:
                num_attacks = skill_duration / actual_atk_interval
                total_damage = num_attacks * single_hit_dmg
                dps = single_hit_dmg / actual_atk_interval
            else: 
                # 理论上S3有明确duration，此分支不应触发，作为安全措施
                total_damage = 0.0
                dps = 0.0
            
        return {"total_damage": total_damage, "dps": dps}