from backend.function.logic.professions import Reaper
from backend.function.logic.formulas import calculate_physical_damage

class Lt40圣约送葬人(Reaper):
    """
    干员：圣约送葬人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        # 初始化天赋属性，这些属性将在 apply_talents 中确认或在计算中使用
        # 天赋 1: 受选之人 (攻击时有20%几率额外攻击一次，技能期间每消耗1颗弹药这个几率提升5%，技能结束时重置)
        self.talent1_base_extra_hit_chance = 0.2
        self.talent1_per_ammo_extra_hit_increase = 0.05
        
        # 天赋 2: 铳弹共感 (每有一个【拉特兰】干员在场，自身的弹药类技能弹药上限+1（最多4层）)
        # 根据规则，可叠加层数的天赋按最大层数计算，因此假设有4个拉特兰干员在场。
        self.talent2_ammo_bonus = 4 
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋的数值已在 __init__ 中初始化并存储为实例属性，供后续计算使用。
        # 此处无需额外的属性修改逻辑。
        pass

    def _get_extra_hit_multiplier(self, ammo_count: int = 0) -> float:
        """
        根据天赋1 (受选之人) 计算平均额外攻击次数乘数。
        ammo_count = 0 表示普攻。
        对于技能，ammo_count 是技能期间总共发射的弹药数。
        额外攻击几率随弹药消耗线性提升，我们计算所有攻击的平均几率。
        """
        if ammo_count <= 1:
            # 对于普攻 (ammo_count=0) 或技能的第一发攻击 (ammo_count=1)，
            # 只有基础几率生效，因为尚未消耗弹药来提升几率。
            avg_extra_hit_chance = self.talent1_base_extra_hit_chance
        else:
            # 对于 N 发弹药 (ammo_count = N)，第 k 发攻击 (1-indexed) 的额外攻击几率为:
            # base_chance + (k-1) * per_ammo_increase。
            # N 发攻击的平均额外攻击几率为:
            # base_chance + (N-1)/2 * per_ammo_increase
            avg_extra_hit_chance = self.talent1_base_extra_hit_chance + \
                                   ((ammo_count - 1) / 2) * self.talent1_per_ammo_extra_hit_increase
        
        return 1 + avg_extra_hit_chance

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 应用天赋1的普攻额外攻击几率 (0弹药消耗)
        extra_hit_multiplier = self._get_extra_hit_multiplier(ammo_count=0)
        
        # 收割者职业特性自带群体伤害，由基类处理，此处无需乘以目标数。
        # 普攻无特殊无视防御或法术伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def) * extra_hit_multiplier

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 基础攻击间隔，用于计算DPS (未考虑技能自身对攻速的修改)
        base_actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        total_damage = 0.0
        dps = 0.0
        
        if skill_index == 0:
            # 技能 1 (遗嘱执行)：攻击力+50%，攻击时无视目标400的防御力，攻击装有8发弹药
            # 弹药数 = 技能基础弹药 + 天赋2额外弹药
            skill_ammo = 8 + self.talent2_ammo_bonus # 8 + 4 = 12 发
            
            # 天赋1额外攻击次数乘数
            extra_hit_multiplier = self._get_extra_hit_multiplier(ammo_count=skill_ammo)
            
            # 技能攻击力倍率
            skill_atk_multiplier = 1.50
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 单次攻击伤害 (带固定值无视防御)
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def, def_ignore_flat=400)
            
            total_damage = single_hit_damage * skill_ammo * extra_hit_multiplier
            dps = (single_hit_damage * extra_hit_multiplier) / base_actual_atk_interval
            
        elif skill_index == 1:
            # 技能 2 (近身铳斗)：攻击力+80%，防御力+80%，阻挡数+1，攻击装有12发弹药
            # 弹药数 = 技能基础弹药 + 天赋2额外弹药
            skill_ammo = 12 + self.talent2_ammo_bonus # 12 + 4 = 16 发
            
            # 天赋1额外攻击次数乘数
            extra_hit_multiplier = self._get_extra_hit_multiplier(ammo_count=skill_ammo)
            
            # 技能攻击力倍率
            skill_atk_multiplier = 1.80
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 单次攻击伤害 (无特殊无视防御)
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            total_damage = single_hit_damage * skill_ammo * extra_hit_multiplier
            dps = (single_hit_damage * extra_hit_multiplier) / base_actual_atk_interval
            
        elif skill_index == 2:
            # 技能 3 (圣约决裁)：攻击间隔略微增大(+0.5)，攻击范围扩大，攻击力+180%，每消耗1颗弹药攻击力额外+6%（最多30层），
            # 技能结束时，对技能期间攻击过的目标造成相当于攻击力250%的物理伤害，攻击装有16发弹药
            
            # 弹药数 = 技能基础弹药 + 天赋2额外弹药
            skill_ammo = 16 + self.talent2_ammo_bonus # 16 + 4 = 20 发
            
            # 技能3有攻击间隔增大效果
            skill_actual_atk_interval = (self.attack_interval + 0.5) * 100 / self.attack_speed
            
            # 天赋1额外攻击次数乘数
            extra_hit_multiplier = self._get_extra_hit_multiplier(ammo_count=skill_ammo)
            
            # 技能持续攻击力计算: 基础+180% + (每消耗1颗弹药额外+6%，最多30层)
            # 初始攻击力倍率: 1 + 1.80 = 2.8
            # 对于 N 发弹药，第 k 发攻击 (1-indexed) 的额外攻击力加成是 min(k-1, 30) * 0.06。
            # 由于 skill_ammo (20) 小于 30，所以 min(k-1, 30) 简化为 k-1。
            # 持续攻击的平均攻击力倍率:
            # 初始倍率 + (N-1)/2 * 0.06
            avg_skill_atk_multiplier_bonus = ((skill_ammo - 1) / 2) * 0.06 # (20-1)/2 * 0.06 = 9.5 * 0.06 = 0.57
            avg_skill_atk_multiplier = (1 + 1.80) + avg_skill_atk_multiplier_bonus # 2.8 + 0.57 = 3.37
            
            enhanced_atk_avg = self.final_base_atk * avg_skill_atk_multiplier
            
            # 持续攻击伤害
            single_hit_damage_avg = calculate_physical_damage(enhanced_atk_avg, enemy.current_def)
            continuous_damage = single_hit_damage_avg * skill_ammo * extra_hit_multiplier
            
            # 技能结束时的爆发伤害: 相当于攻击力250%的物理伤害。
            # 爆发伤害应使用技能结束时 (即所有弹药消耗完毕后) 的最终攻击力。
            # 最终攻击力倍率: (1 + 1.80) + min(skill_ammo - 1, 30) * 0.06
            # 由于 skill_ammo (20) 小于 30，所以 min(skill_ammo - 1, 30) 简化为 skill_ammo - 1。
            final_skill_atk_multiplier_bonus = (skill_ammo - 1) * 0.06 # 19 * 0.06 = 1.14
            final_skill_atk_multiplier = (1 + 1.80) + final_skill_atk_multiplier_bonus # 2.8 + 1.14 = 3.94
            
            final_burst_atk_value = self.final_base_atk * final_skill_atk_multiplier * 2.50
            final_burst_damage = calculate_physical_damage(final_burst_atk_value, enemy.current_def)
            
            total_damage = continuous_damage + final_burst_damage
            
            # 技能3的DPS计算
            # 技能总持续时间 = 弹药数 * 技能实际攻击间隔
            skill_duration = skill_ammo * skill_actual_atk_interval
            if skill_duration > 0:
                dps = total_damage / skill_duration
            else:
                dps = 0.0 # 理论上弹药技能不会出现0持续时间
            
        return {"total_damage": total_damage, "dps": dps}