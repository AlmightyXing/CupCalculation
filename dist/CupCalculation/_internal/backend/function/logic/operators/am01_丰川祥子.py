from backend.function.logic.professions import Lord
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Am01丰川祥子(Lord):
    """
    干员：丰川祥子
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：颂乐音符 (每存在一个音符，Ave Mujica成员无视敌人3%的防御力和2%法术抗性（最多叠加至10层）)
        # 根据规则，天赋对提高伤害有帮助的均纳入考虑，可叠加层数的按最大层数叠加。
        # 因此，丰川祥子自身享受10层叠加效果。
        self.talent_def_ignore_ratio = 0.03 * 10  # 0.3 (无视30%防御力)
        self.talent_res_ignore_ratio = 0.02 * 10  # 0.2 (无视20%法术抗性)
        
        # 天赋 2：毋畏遗忘 (攻击范围内干员攻击速度+12)
        # 丰川祥子自身攻击速度+12
        self.attack_speed += 12

    def _get_effective_atk_for_lord(self, base_atk: float, is_ranged: bool = True) -> float:
        """
        获取考虑领主职业特性后的实际攻击力。
        领主特性：远程攻击时攻击力降低至80%。
        丰川祥子的所有攻击（普攻和技能）均视为远程攻击。
        """
        if is_ranged:
            return base_atk * 0.8
        return base_atk

    def _calc_physical_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次物理命中时的期望伤害（考虑颂乐音符天赋的无视防御）
        """
        return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.talent_def_ignore_ratio)

    def _calc_arts_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次法术命中时的期望伤害（考虑颂乐音符天赋的无视法抗）
        """
        return calculate_arts_damage(atk_val, enemy.current_res, res_ignore_ratio=self.talent_res_ignore_ratio)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 领主职业特性：远程攻击，攻击力降低至80%
        # 丰川祥子的普攻为物理伤害
        effective_base_atk = self._get_effective_atk_for_lord(self.final_base_atk, is_ranged=True)
        return self._calc_physical_hit(effective_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 计算基础攻击间隔，用于没有额外攻速加成的技能
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (新月的苏醒)：
            # "依次演奏出造成攻击力100%/92%/75%/58%/42%/33%/17%/5%法术伤害的8个音符。"
            # 瞬发技能，总倍率 = 100+92+75+58+42+33+17+5 = 422%
            # 伤害类型：法术伤害
            
            # 技能描述没有提到攻击力加成，所以使用基础攻击力（考虑领主远程特性）
            effective_atk_for_skill = self._get_effective_atk_for_lord(self.final_base_atk, is_ranged=True)
            
            total_multiplier = (100 + 92 + 75 + 58 + 42 + 33 + 17 + 5) / 100.0  # 4.22
            atk_val = effective_atk_for_skill * total_multiplier
            
            total_damage = self._calc_arts_hit(atk_val, enemy)
            # 瞬发伤害技能的DPS计算方式
            return {"total_damage": total_damage, "dps": total_damage / base_actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (满月的舞会)：
            # "可以切换钢琴（初始）或风琴音色演奏：
            # 钢琴：攻击力+110%，音符飞行速度加快，命中目标后穿过敌人造成物理伤害；
            # 风琴：攻击速度+140，音符造成法术伤害且飞行速度减缓。
            # Fever期间变为当前音色的二连击"
            # 永续技能 (duration=null)，主要计算DPS。
            # 根据规则，天赋对提高伤害有帮助的均纳入考虑，这里选择钢琴模式并考虑Fever期间的二连击，以最大化伤害。
            
            # 1. 计算强化后的攻击力 (考虑领主远程特性和技能攻击力加成)
            effective_base_atk = self._get_effective_atk_for_lord(self.final_base_atk, is_ranged=True)
            
            # 钢琴模式攻击力加成：110%
            skill_atk_multiplier = 1 + 1.10  # 2.10
            enhanced_atk = effective_base_atk * skill_atk_multiplier
            
            # 2. 计算单次攻击循环的总伤害 (Fever期间二连击)
            # 钢琴模式伤害类型：物理伤害
            single_hit_damage = self._calc_physical_hit(enhanced_atk, enemy)
            total_damage_per_attack_cycle = single_hit_damage * 2  # Fever期间二连击
            
            # 3. 计算DPS
            # 技能没有改变攻击间隔，使用基础攻击间隔
            dps = total_damage_per_attack_cycle / base_actual_atk_interval
            
            # 永续技能，total_damage为0
            return {"total_damage": 0, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (残月的余响)：
            # "攻击范围扩大，攻击同时使用钢琴和风琴音色演奏，各自演奏2个造成相当于攻击力220%物理和法术伤害的音符，
            # 且分别追踪法术抗性和防御力最高的敌人。Fever期间Ave Mujica成员受到致命伤害时不撤退，Fever结束后退场"
            # 持续时间：25秒
            
            duration = 25
            
            # 1. 计算强化后的攻击力 (技能没有直接攻击力加成，但有倍率)
            effective_base_atk = self._get_effective_atk_for_lord(self.final_base_atk, is_ranged=True)
            
            # 2. 计算单次攻击循环的总伤害
            # 钢琴部分：2个物理伤害音符，每个220%攻击力
            piano_atk_val = effective_base_atk * 2.20
            piano_damage_per_hit = self._calc_physical_hit(piano_atk_val, enemy)
            total_piano_damage_per_cycle = piano_damage_per_hit * 2
            
            # 风琴部分：2个法术伤害音符，每个220%攻击力
            organ_atk_val = effective_base_atk * 2.20
            organ_damage_per_hit = self._calc_arts_hit(organ_atk_val, enemy)
            total_organ_damage_per_cycle = organ_damage_per_hit * 2
            
            # 单次攻击循环的总伤害 = 钢琴部分伤害 + 风琴部分伤害
            total_damage_per_attack_cycle = total_piano_damage_per_cycle + total_organ_damage_per_cycle
            
            # 3. 计算DPS
            # 技能没有改变攻击间隔，使用基础攻击间隔
            dps = total_damage_per_attack_cycle / base_actual_atk_interval
            
            # 4. 计算总伤害
            total_damage = dps * duration
            
            return {"total_damage": total_damage, "dps": dps}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)