from backend.function.logic.professions import Brawler
from backend.function.logic.formulas import calculate_physical_damage

class Nm04重岳(Brawler):
    """
    干员：重岳
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：止戈 (对目标普通攻击时，有23%的概率使重岳2.5秒内对其造成的伤害提升65%)
        self.prob_talent1 = 0.23
        self.dmg_boost_talent1 = 0.65
        
        # 天赋 2：万象为宾 (若重岳释放一次技能击倒不少于一个敌人，则回复3点技力)
        # 此天赋不直接影响伤害数值，故不在此处计算。
        
    def _calc_hit(self, atk_val: float, enemy, talent1_guaranteed: bool = False) -> float:
        """
        计算单次命中时的期望物理伤害（考虑止戈天赋的概率伤害提升）
        :param atk_val: 本次攻击的攻击力数值
        :param enemy: 敌人对象
        :param talent1_guaranteed: 是否100%触发第一天赋的伤害提升
        """
        base_dmg = calculate_physical_damage(atk_val, enemy.current_def)
        
        if talent1_guaranteed:
            # 100%触发天赋1时，直接应用伤害提升
            return base_dmg * (1 + self.dmg_boost_talent1)
        else:
            # 否则，按概率计算期望伤害
            return base_dmg * (1 + self.prob_talent1 * self.dmg_boost_talent1)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻直接调用 _calc_hit，不保证天赋1触发
        # Brawler 父类没有特殊的普攻逻辑，所以直接计算单次伤害即可
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (冲盈)：
            # 对目标造成相当于攻击力400%的物理伤害；
            # 技能达到最大充能层数时消耗所有充能，造成对应次数的伤害 可充能3次
            # 按照最大充能层数计算，即3次400%攻击力伤害
            atk_val = self.final_base_atk * 4.0
            total_damage = self._calc_hit(atk_val, enemy) * 3
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (拂尘)：
            # 1. 对周围至多4个敌人造成相当于攻击力450%的物理伤害
            # 2. 之后使周围所有浮空敌人结束浮空状态，对其100%触发第一天赋并造成相当于攻击力650%的物理伤害
            # 技能描述为瞬发伤害，且有duration，但通常此类技能的duration是其他效果，伤害按爆发计算。
            
            # 第一段伤害：450%攻击力，天赋1按概率触发
            dmg_instance1 = self._calc_hit(self.final_base_atk * 4.5, enemy)
            
            # 第二段伤害：650%攻击力，且100%触发第一天赋
            dmg_instance2 = self._calc_hit(self.final_base_atk * 6.5, enemy, talent1_guaranteed=True)
            
            total_damage = dmg_instance1 + dmg_instance2
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 2:
            # 技能 3 (我无)：
            # 1. 对目标及其周围造成相当于攻击力380%的物理伤害
            # 2. 累计使用五次技能后：重岳攻击的范围扩大且攻击变为二连击，技能变为自动释放且造成额外一次伤害
            # 持续时间为null，且有“累计使用五次技能后”的描述，应按永续技能且最大层数（强化后）计算。
            # 永续技能 total_damage = 0，重点是返回正确的 dps。
            
            # 强化后：
            # "技能变为自动释放且造成额外一次伤害" -> 每次攻击造成 (380% + 额外一次380%) = 760% 攻击力伤害
            # "攻击变为二连击" -> 最终伤害再乘以2
            
            # 计算单次“技能攻击”的伤害（包含额外一次伤害）
            skill_base_atk_multiplier = 3.8 * 2 # 380% + 额外一次380%
            damage_per_skill_hit = self._calc_hit(self.final_base_atk * skill_base_atk_multiplier, enemy)
            
            # 考虑“二连击”特性
            final_dps_damage = damage_per_skill_hit * 2
            
            return {"total_damage": 0, "dps": final_dps_damage / actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
