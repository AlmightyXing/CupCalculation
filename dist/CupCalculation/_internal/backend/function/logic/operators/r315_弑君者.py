from backend.function.logic.professions import Executor # 弑君者是处决者，属于特种干员的一个分支
from backend.function.logic.formulas import calculate_physical_damage

class R315弑君者(Executor):
    """
    干员：弑君者
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：吞咽苦厄 (技能持续期间在自身周围产生烟雾，使其中的地面敌人物理与法术命中率-20%)
        # 此天赋为防御/控制类，不直接影响弑君者的伤害输出，故不在此处进行数值修改。
        
        # 天赋 2：弑君者威名 (对未伤害过自身的地面敌人造成的物理伤害提升20%)
        # 假设目标满足“未伤害过自身”的条件，以计算最大伤害。
        self.talent_2_dmg_boost = 0.20
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害，考虑“弑君者威名”天赋。
        """
        # 应用天赋2：对未伤害过自身的地面敌人造成的物理伤害提升20%
        # 假设当前目标满足此条件，因此直接将攻击力提升
        modified_atk_val = atk_val * (1 + self.talent_2_dmg_boost)
        return calculate_physical_damage(modified_atk_val, enemy.current_def)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻直接调用_calc_hit，应用天赋2
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 实际攻击间隔用于计算DPS和技能期间普攻次数
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (尘烟蔽目)：部署后攻击力+100%，并获得50%物理和法术闪避 (持续10秒)
            duration = 10
            atk_buff_ratio = 1.00 # +100%攻击力
            
            # 强化后的攻击力
            enhanced_atk = self.final_base_atk * (1 + atk_buff_ratio)
            
            # 技能期间能打出的普攻次数
            num_hits = (duration or 0) / actual_atk_interval
            
            # 单次强化普攻的伤害
            damage_per_hit = self._calc_hit(enhanced_atk, enemy)
            
            total_damage = damage_per_hit * num_hits
            dps = damage_per_hit / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (硝烟震爆)：部署后8秒内停止攻击，并在技能结束时对烟雾内的所有地面敌人造成相当于攻击力500%的物理伤害
            duration = 8
            burst_atk_multiplier = 5.00 # 500%攻击力
            
            # 爆发伤害使用基础攻击力计算
            burst_atk_val = self.final_base_atk * burst_atk_multiplier
            
            total_damage = self._calc_hit(burst_atk_val, enemy)
            
            # DPS为总伤害除以技能持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (烽烟行刑场)：每2秒现身对烟雾内的一名地面敌人造成两次相当于攻击力250%的物理伤害 (持续16秒)
            duration = 16
            skill_trigger_interval = 2.0 # 每2秒触发一次
            hits_per_trigger = 2 # 每次触发造成两次伤害
            atk_multiplier_per_hit = 2.50 # 250%攻击力
            
            # 技能期间触发次数
            num_triggers = duration / skill_trigger_interval
            
            # 技能期间总命中次数
            total_hits = num_triggers * hits_per_trigger
            
            # 每次命中强化后的攻击力
            enhanced_atk = self.final_base_atk * atk_multiplier_per_hit
            
            # 单次命中伤害
            damage_per_hit = self._calc_hit(enhanced_atk, enemy)
            
            total_damage = damage_per_hit * total_hits
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)