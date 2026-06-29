from backend.function.logic.professions import CoreCaster
from backend.function.logic.formulas import calculate_arts_damage

class Re03逻各斯(CoreCaster):
    """
    干员：逻各斯
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：语汇演化
        # 对一个目标发起攻击时，有40%几率额外对攻击范围内一个随机目标造成相当于攻击力60%的法术伤害
        self.talent1_prob = 0.4
        self.talent1_extra_dmg_ratio = 0.6
        
        # 天赋 2：剜魂具辞
        # 攻击使目标在5秒内法术抗性-10且受到的法术伤害提高150点
        # 按照“只要天赋对提高伤害有帮助，均纳入考虑”的原则，假设每次攻击都享受此加成
        self.talent2_res_debuff = 10
        self.talent2_flat_dmg_bonus = 150
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑剜魂具辞天赋的法抗降低和额外伤害）
        """
        # 应用天赋2的法术抗性降低和额外伤害
        # 注意：这里是假设天赋2的debuff在当前次攻击时就生效，以最大化伤害计算
        effective_res = max(0, enemy.current_res - self.talent2_res_debuff)
        
        # calculate_arts_damage 已经包含了 (ATK - RES) * (1 - RES_RATIO) 的逻辑
        # 额外的150点伤害是直接加在最终伤害上的
        base_dmg = calculate_arts_damage(atk_val, effective_res)
        
        return base_dmg + self.talent2_flat_dmg_bonus

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 主目标伤害
        main_target_dmg = self._calc_arts_hit(self.final_base_atk, enemy)
        
        # 天赋1：语汇演化 额外伤害
        # 额外伤害的攻击力是基础攻击力 * 60%
        extra_hit_atk_val = self.final_base_atk * self.talent1_extra_dmg_ratio
        # 额外伤害也享受天赋2的加成
        expected_extra_dmg = self.talent1_prob * self._calc_arts_hit(extra_hit_atk_val, enemy)
        
        # 普攻的期望伤害是主目标伤害加上天赋1的期望额外伤害
        return main_target_dmg + expected_extra_dmg

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (殁亡)：永续技能
            # 攻击力+100%
            # "使攻击范围内生命值低于逻各斯攻击力150%的敌人立刻倒下、并对另一个随机目标造成与倒下单位生命值相等的法术伤害"
            # 这一部分无法量化为固定伤害，因此不计入总伤和DPS。
            # 仅计算攻击力加成带来的普攻DPS。
            
            skill_atk_multiplier_bonus = 1.00 # +100%攻击力
            enhanced_atk = self.final_base_atk * (1 + skill_atk_multiplier_bonus)
            
            # 强化后的主目标单次伤害
            enhanced_main_hit_dmg = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 强化后的天赋1额外伤害
            enhanced_extra_hit_atk_val = enhanced_atk * self.talent1_extra_dmg_ratio
            expected_enhanced_extra_dmg = self.talent1_prob * self._calc_arts_hit(enhanced_extra_hit_atk_val, enemy)
            
            total_hit_dmg_per_attack = enhanced_main_hit_dmg + expected_enhanced_extra_dmg
            
            # 永续技能，total_damage为0，dps为强化后的普攻dps
            return {"total_damage": 0.0, "dps": total_hit_dmg_per_attack / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (提喻)：持续20秒
            # 攻击改为锁定一个目标对其每0.5秒造成一次相当于攻击力75%的法术伤害
            # 对相同目标的伤害逐渐提高至3倍 (即75% -> 225%)，锁定5秒后达到上限
            
            duration = 20.0
            skill_hit_interval = 0.5
            
            # 伤害倍率从0.75线性提升到2.25，持续5秒
            ramp_up_duration = 5.0
            ramp_up_hits = int(ramp_up_duration / skill_hit_interval) # 10 hits
            
            initial_multiplier = 0.75
            max_multiplier = 2.25
            
            total_damage = 0.0
            
            # 线性提升阶段的伤害
            for i in range(ramp_up_hits):
                # 当前hit的倍率: initial + (max - initial) * (i / (ramp_up_hits - 1))
                # 确保ramp_up_hits至少为1，避免除以0
                current_multiplier = initial_multiplier + (max_multiplier - initial_multiplier) * (i / (ramp_up_hits - 1)) if ramp_up_hits > 1 else initial_multiplier
                total_damage += self._calc_arts_hit(self.final_base_atk * current_multiplier, enemy)
            
            # 达到上限后的持续时间
            max_dmg_duration = duration - ramp_up_duration
            max_dmg_hits = int(max_dmg_duration / skill_hit_interval) # 30 hits
            
            # 达到上限后的伤害
            for _ in range(max_dmg_hits):
                total_damage += self._calc_arts_hit(self.final_base_atk * max_multiplier, enemy)
            
            # S2是攻击模式改变，不触发天赋1的额外攻击
            
            return {"total_damage": total_damage, "dps": total_damage / duration}
            
        elif skill_index == 2:
            # 技能 3 (延异视阈)：持续30秒
            # 攻击范围扩大，攻击力+300%，同时攻击4个目标
            # "使攻击范围内敌方子弹的飞行速度大幅降低、并在技能结束时将其全部清除" - 无法量化为伤害
            
            duration = 30.0
            skill_atk_multiplier_bonus = 3.00 # +300%攻击力
            enhanced_atk = self.final_base_atk * (1 + skill_atk_multiplier_bonus)
            
            # 强化后的主目标单次伤害
            enhanced_main_hit_dmg = self._calc_arts_hit(enhanced_atk, enemy)
            
            # 强化后的天赋1额外伤害
            enhanced_extra_hit_atk_val = enhanced_atk * self.talent1_extra_dmg_ratio
            expected_enhanced_extra_dmg = self.talent1_prob * self._calc_arts_hit(enhanced_extra_hit_atk_val, enemy)
            
            total_hit_dmg_per_attack = enhanced_main_hit_dmg + expected_enhanced_extra_dmg
            
            # 技能期间攻击次数
            num_hits = duration / actual_atk_interval
            
            total_damage = num_hits * total_hit_dmg_per_attack
            
            return {"total_damage": total_damage, "dps": total_damage / duration}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
    def get_team_buffs(self, skill_index: int = -1) -> dict:
        buffs = {}
        # 逻各斯只要在场（不论技能），第二天赋剜魂具辞提供减抗和法强附加
        buffs['res_shred'] = getattr(self, 'talent2_res_debuff', 10)
        buffs['arts_flat_dmg'] = getattr(self, 'talent2_flat_dmg_bonus', 150)
        return buffs
