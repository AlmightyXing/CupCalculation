from backend.function.logic.professions import ArtsFighter
from backend.function.logic.formulas import calculate_arts_damage

class Yd30赤刃明霄陈(ArtsFighter):
    """
    干员：赤刃明霄陈
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：形意洞照
        # 攻击力+13%
        self.final_base_atk *= (1 + 0.13)
        # 攻击速度+13
        self.attack_speed += 13
        # 造成的物理和法术伤害变为弱点伤害 (对于法术伤害，通常指无视一定数值的法术抗性)
        # 假设弱点伤害为无视15点法术抗性，这是一个常见的游戏内数值。
        self.ignore_res_value = 15 
        
        # 天赋 2：寒暑觉知 (未受到伤害时，每7秒随机治疗自身一定生命值，并闪避下次物理与法术攻击)
        # 该天赋不直接增加伤害，因此不纳入伤害计算。
        
    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望法术伤害（考虑形意洞照天赋的弱点伤害）
        """
        # 弱点伤害：无视固定数值的法术抗性
        return calculate_arts_damage(atk_val, enemy.current_res, res_ignore_value=self.ignore_res_value)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 赤刃明霄陈的普攻造成法术伤害
        return self._calc_arts_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        # 获取当前技能数据
        skill_data = self.raw_data["skills"][skill_index]
        duration = skill_data.get("duration") # Duration for timed skills
        
        if skill_index == 0:
            # 技能 1 (赤霄·奔夜)：持续18秒
            # 攻击力+120%，攻击变为二连击
            skill_atk_multiplier = 1 + 1.20
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 单次普攻伤害（二连击）
            single_hit_damage = self._calc_arts_hit(enhanced_atk, enemy) * 2
            
            # 技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval
            
            total_damage = num_attacks * single_hit_damage
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (赤霄·绝影-驰)：持续6秒 (爆发技能)
            # 对周围最近的1名敌人发动10次斩击，每次造成攻击力480%的法术伤害
            # "敌人被击倒时转移至目标周围最近的其他敌人并使剩余攻击次数+1" - 这是一个条件触发的额外效果，
            # 在没有具体概率或敌人生命值信息的情况下，按基础10次斩击计算。
            # "接下来攻击力+300%，获得60%物理和法术闪避" - 这是爆发后的后续增益，不计入本次爆发伤害。
            
            burst_atk_multiplier = 4.80
            burst_atk_value = self.final_base_atk * burst_atk_multiplier
            
            single_slash_damage = self._calc_arts_hit(burst_atk_value, enemy)
            
            total_damage = single_slash_damage * 10
            
            # 爆发技能的DPS按总伤除以技能持续时间
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (赤霄·天喟)：持续20秒
            # 技能开启时向前释放一道可转向的剑气，对穿过的敌人造成相当于其当前生命值6%的法术伤害
            # （至少造成自身攻击力580%的法术伤害）
            # 对于期望伤害计算，取保底伤害值。
            initial_burst_atk_multiplier = 5.80
            initial_burst_atk_value = self.final_base_atk * initial_burst_atk_multiplier
            initial_burst_damage = self._calc_arts_hit(initial_burst_atk_value, enemy)
            
            # 攻击范围扩大，每次攻击对最多4名地面敌人造成3次攻击力210%的法术伤害
            # 注意：严禁在代码中乘以任何目标数。这里只计算对单个目标的伤害。
            # 每次攻击造成3次伤害
            sustained_atk_multiplier = 2.10
            sustained_atk_value = self.final_base_atk * sustained_atk_multiplier
            
            single_sustained_hit_damage = self._calc_arts_hit(sustained_atk_value, enemy) * 3
            
            # 技能持续期间的攻击次数
            num_attacks = duration / actual_atk_interval
            
            damage_from_sustained_attacks = num_attacks * single_sustained_hit_damage
            
            total_damage = initial_burst_damage + damage_from_sustained_attacks
            dps = total_damage / duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)