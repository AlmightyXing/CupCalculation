from backend.function.logic.professions import Trapmaster
from backend.function.logic.formulas import calculate_arts_damage, calculate_physical_damage

class Nm07望(Trapmaster):
    """
    干员：望
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：铸子 (主要影响棋子数量和部署机制，不直接影响单次伤害数值，故不在此处修改属性)
        # "可以使用6枚棋子（最多拥有7枚），棋子相连时相互激活，敌人进入激活的棋子所在地块时触发其效果；
        # 手动部署棋子时，望在相邻位置额外部署一枚棋子（最多9枚，可以且优先部署在有敌人的不可部署地块）"
        pass # 此天赋不直接影响伤害数值，故无需在此处进行数值修改

        # 天赋 2：料敌机先 (棋子激活时所在的连续直线上每有一枚棋子，直线上所有棋子造成伤害提升10%并无视敌人9点法术抗性（最多叠加3次）)
        # 按照最大叠加层数计算
        self.talent_2_dmg_boost_ratio = 0.10 * 3 # 30% 伤害提升
        self.talent_2_res_ignore = 9 * 3         # 27 点法术抗性无视
        
    def _calc_trap_damage(self, atk_multiplier: float, enemy) -> float:
        """
        计算单次棋子触发时的期望法术伤害（考虑料敌机先天赋的伤害提升和法术抗性无视）
        """
        # 强化后的攻击力 = 基础攻击力 * 技能倍率 * (1 + 天赋伤害提升)
        effective_atk = self.final_base_atk * atk_multiplier * (1 + self.talent_2_dmg_boost_ratio)
        
        # 强化后的法术抗性 = 敌人当前法抗 - 天赋无视法抗 (最低为0)
        effective_res = max(0, enemy.current_res - self.talent_2_res_ignore)
        
        return calculate_arts_damage(effective_atk, effective_res)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 望的普攻为物理伤害，天赋和技能均作用于棋子（法术伤害），因此普攻沿用基类逻辑
        # 如果基类普攻是物理伤害，则此处无需特殊处理
        return super().calculate_normal_hit(enemy, target_count)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 陷阱师的攻击间隔通常不直接影响陷阱触发频率，但根据规则，瞬发伤害技能的DPS需要除以实际攻击间隔
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (取势)：被动效果：棋子触发时使目标敌人停顿且每秒受到相当于望攻击力的135%的法术伤害，持续6.5秒
            atk_multiplier = 1.35
            duration = 6.5
            
            # 计算每秒的伤害
            dps_per_sec = self._calc_trap_damage(atk_multiplier, enemy)
            
            # 总伤害为持续伤害的总和
            total_damage = dps_per_sec * duration
            
            # 对于持续伤害技能，dps应为每秒伤害
            return {"total_damage": total_damage, "dps": dps_per_sec}
            
        elif skill_index == 1:
            # 技能 2 (连星)：被动效果：棋子触发时，对连线方向上两侧3格范围内的敌人造成相当于攻击力的580%的法术伤害
            atk_multiplier = 5.80
            
            # 瞬发伤害，计算单次触发的伤害
            total_damage = self._calc_trap_damage(atk_multiplier, enemy)
            
            # 按照瞬发伤害技能的DPS计算规则
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (天下劫)：被动效果：棋子的触发和伤害范围扩大，造成相当于攻击力380%的法术伤害
            atk_multiplier = 3.80
            
            # 瞬发伤害，计算单次触发的伤害
            total_damage = self._calc_trap_damage(atk_multiplier, enemy)
            
            # 按照瞬发伤害技能的DPS计算规则
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)