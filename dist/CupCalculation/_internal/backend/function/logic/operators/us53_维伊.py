from backend.function.logic.professions import MysticCaster
from backend.function.logic.formulas import calculate_arts_damage

class Us53维伊(MysticCaster):
    """
    干员：维伊
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋相关的额外伤害，将在 apply_talents 中设置
        self.talent_dot_per_sec = 0 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：在挥刀之前
        # "特性储存的能量达到3个时，合成为1个转置能量（至多储存等同于9倍的能量），拥有转置能量时攻击力+10%，未拥有转置能量时攻击速度+15"
        # 根据规则，只要天赋对提高伤害有帮助，均纳入考虑，并按最大层数/最有利状态叠加。
        # 因此，假设维伊拥有转置能量，攻击力+10%。
        self.final_base_atk *= 1.10
        
        # 天赋 2：战争技艺
        # "攻击和储存的能量使目标在5秒内每秒受到90点法术伤害（至多叠加3次，发射转置能量可以叠加3次）"
        # 最大叠加3次，所以每秒额外法术伤害为 90 * 3 = 270。
        # 这个DoT伤害将计入DPS。
        self.talent_dot_per_sec = 270
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害，不包含秘术师的能量储存倍率。
        维伊的攻击造成法术伤害。
        """
        return calculate_arts_damage(atk_val, enemy.current_res)

    def _get_mystic_caster_base_hit_damage(self, atk_val: float, enemy) -> float:
        """
        封装秘术师职业的普攻特性：攻击造成法术伤害，并包含能量储存的2.1倍率。
        """
        # 秘术师的普攻特性是储存能量后一齐发射，父类定义为2.1倍率
        return self._calc_arts_hit(atk_val * 2.1, enemy)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 维伊的普攻造成法术伤害，并继承秘术师的能量储存机制
        return self._get_mystic_caster_base_hit_damage(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取基础攻击间隔和攻击速度，以便在技能计算中进行修改
        # self.attack_interval 来自 JSON 的 atk_time，在 super().__init__ 中被 MysticCaster 设置为 3.0
        # self.attack_speed 默认为 100，可能被天赋修改
        original_atk_interval = self.attack_interval
        original_attack_speed = self.attack_speed
        original_final_base_atk = self.final_base_atk

        # 天赋2的持续伤害，作为DPS的一部分
        base_dps_dot = self.talent_dot_per_sec

        # 技能 0: 自呼号生发
        if skill_index == 0:
            # "攻击速度+100"
            skill_attack_speed = original_attack_speed + 100
            actual_atk_interval = original_atk_interval * 100 / skill_attack_speed
            
            # 技能期间攻击力不变
            skill_atk_val = original_final_base_atk
            
            # 单次普攻伤害，需要包含秘术师的能量储存倍率
            single_hit_damage = self._get_mystic_caster_base_hit_damage(skill_atk_val, enemy)
            
            # 技能持续时间
            duration = self.skills[skill_index]["duration"]
            
            # 技能期间普攻次数
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * single_hit_damage
            dps = single_hit_damage / actual_atk_interval + base_dps_dot
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 技能 1: 以鲜血洗去
        elif skill_index == 1:
            # "攻击间隔小幅缩短(-0.5)"
            skill_atk_interval = original_atk_interval - 0.5
            
            # "每次攻击或发射储存能量后，使自身后续攻击力+15%，攻击速度+8（至多叠加9层）"
            # 根据规则，假设达到最大层数（9层）以计算最大伤害。
            max_stacks = 9
            atk_buff_ratio = 1 + (0.15 * max_stacks) # 1 + 1.35 = 2.35
            aspd_buff = 8 * max_stacks # 72
            
            skill_attack_speed = original_attack_speed + aspd_buff
            
            actual_atk_interval = skill_atk_interval * 100 / skill_attack_speed
            
            # 强化后的攻击力
            skill_atk_val = original_final_base_atk * atk_buff_ratio
            
            # 单次普攻伤害，需要包含秘术师的能量储存倍率
            single_hit_damage = self._get_mystic_caster_base_hit_damage(skill_atk_val, enemy)
            
            # 技能持续时间
            duration = self.skills[skill_index]["duration"]
            
            # 技能期间普攻次数
            hits_during_skill = (duration or 0) / actual_atk_interval
            
            total_damage = hits_during_skill * single_hit_damage
            dps = single_hit_damage / actual_atk_interval + base_dps_dot
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 技能 2: 用赤铁铭记
        elif skill_index == 2:
            # 永续技能 (duration: null)，根据规则 total_damage = 0，重点计算DPS。
            # "攻击速度+180"
            skill_attack_speed = original_attack_speed + 180
            actual_atk_interval = original_atk_interval * 100 / skill_attack_speed
            
            # "储存的能量发射后会在敌人间（优先不同目标）跳跃一次，并造成相当于165%攻击力的法术伤害"
            # "转置能量改为跳跃3次"
            # 维伊的特性是“在找不到攻击目标时可以将攻击能量储存起来之后一齐发射（最多3个）”
            # 天赋1是“特性储存的能量达到3个时，合成为1个转置能量”
            # 技能3的弹药消耗：“仅在发射每个储存能量时消耗1发弹药，发射转置能量消耗3发弹药”
            # 为了最大化DPS，我们假设总是发射“转置能量”。
            # 发射一个转置能量消耗3发弹药，并造成相当于165%攻击力的法术伤害，且跳跃3次。
            # 这里的“跳跃3次”意味着对单个目标造成3次165%攻击力的伤害。
            
            # 强化后的攻击力 (天赋1的10%已在__init__和apply_talents中计算)
            skill_atk_val = original_final_base_atk
            
            # 单次攻击（发射一个转置能量）的总伤害
            # 每次跳跃造成165%攻击力伤害，跳跃3次。此处的伤害倍率是技能特有的，不叠加秘术师的2.1倍率。
            single_attack_total_damage = self._calc_arts_hit(skill_atk_val * 1.65, enemy) * 3
            
            # DPS = 单次攻击总伤害 / 实际攻击间隔 + 天赋DoT
            dps = single_attack_total_damage / actual_atk_interval + base_dps_dot
            
            return {"total_damage": 0, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
