from backend.function.logic.professions import PhalanxCaster
from backend.function.logic.formulas import calculate_arts_damage
import math

class Ln04卡涅利安(PhalanxCaster):
    """
    干员：卡涅利安
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：生命之餐 (开启技能时立即恢复40%最大生命值；蓄力时效果翻倍)
        # 该天赋主要影响生存和回复，不直接影响伤害输出，因此在伤害计算中忽略。

        # 天赋 2：蓄势待发 (技力超过上限时，技力自然回复速度+0.6/秒)
        # 该天赋影响技能回转，不直接影响单次攻击伤害，因此在伤害计算中忽略。
        pass
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害
        """
        return calculate_arts_damage(atk_val, enemy.current_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 阵法术师通常时不攻击，因此普攻伤害为0
        return 0.0

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 阵法术师的攻击间隔在技能开启时才生效
        # 实际攻击间隔会根据攻速和技能效果调整
        
        # 默认攻击间隔 (self.attack_interval是基准攻击间隔)
        base_atk_interval = self.attack_interval
        current_attack_speed = self.attack_speed
        
        # 技能期间的攻击力，初始为最终基础攻击力
        skill_atk = self.final_base_atk
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (沙暴守卫)：攻击力+60%，防御力+100%；蓄力额外效果：特性效果在技能期间继续生效
            # 假设计算蓄力效果下的最大伤害潜力
            skill_atk *= (1 + 0.60) # 攻击力+60%
            duration = 20
            
            actual_atk_interval = base_atk_interval * 100 / current_attack_speed
            num_hits = math.floor(duration / actual_atk_interval)
            
            single_hit_damage = self._calc_arts_hit(skill_atk, enemy)
            total_damage = single_hit_damage * num_hits
            dps = single_hit_damage / actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (沙缚镣锁)：攻击间隔大幅度缩短(-1.1)，每次攻击对目标造成0.3秒停顿；
            # 蓄力额外效果：攻击力+20%且停顿变为束缚0.6秒
            # 假设计算蓄力效果下的最大伤害潜力
            skill_atk *= (1 + 0.20) # 蓄力额外效果：攻击力+20%
            duration = 25
            
            # 攻击间隔缩短
            modified_base_atk_interval = base_atk_interval - 1.1
            actual_atk_interval = modified_base_atk_interval * 100 / current_attack_speed
            num_hits = math.floor(duration / actual_atk_interval)
            
            single_hit_damage = self._calc_arts_hit(skill_atk, enemy)
            total_damage = single_hit_damage * num_hits
            dps = single_hit_damage / actual_atk_interval
            
        elif skill_index == 2:
            # 技能 3 (食噬之印)：攻击范围扩大，攻击力逐渐增至+280%；
            # 蓄力额外效果：每次攻击使目标受到来自卡涅利安的伤害提升20%（最多叠加5次），持续至技能结束
            # 假设计算蓄力效果下的最大伤害潜力
            skill_atk *= (1 + 2.80) # 攻击力逐渐增至+280% (取最大值)
            duration = 21
            
            actual_atk_interval = base_atk_interval * 100 / current_attack_speed
            num_hits = math.floor(duration / actual_atk_interval)
            
            single_hit_base_damage = self._calc_arts_hit(skill_atk, enemy)
            
            # 计算叠加伤害提升的平均值和最大值
            total_damage_sum = 0.0
            
            for i in range(num_hits):
                # 伤害提升20%（最多叠加5次），即最多提升100%伤害，总倍率为2.0
                current_debuff_multiplier = min(1.0 + 0.2 * i, 2.0)
                total_damage_sum += single_hit_base_damage * current_debuff_multiplier
            
            total_damage = total_damage_sum
            # DPS通常取技能稳定后的最大输出，即满层debuff下的伤害
            dps = (single_hit_base_damage * 2.0) / actual_atk_interval # 假设满层2.0倍率
            
        else:
            # 如果技能索引不匹配，调用基类方法
            return super().calculate_skill_damage(enemy, skill_index, target_count)
            
        return {"total_damage": total_damage, "dps": dps}