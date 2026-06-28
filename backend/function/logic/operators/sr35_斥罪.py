from backend.function.logic.professions import Defender
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Sr35斥罪(Defender):
    """
    干员：斥罪
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：律法卫士 (部署后立即获得相当于生命上限50%的屏障，每击倒一名敌人时获得相当于生命上限10%的屏障（最多不超过生命上限300%）)
        # 这个天赋主要影响生存和屏障获取，不直接影响攻击伤害数值。
        # 技能2会提升此天赋的屏障获取效果，但屏障本身不直接增加伤害。
        
        # 天赋 2：荆棘环身 (拥有来源于自身的屏障时，每次受到攻击对目标造成相当于斥罪攻击力50%的法术伤害)
        # 这是反伤天赋，属于被动伤害，不计入主动攻击的total_damage和dps。
        # 因此，在此次任务的 calculate_normal_hit 和 calculate_skill_damage 方法中不体现。
        pass
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 斥罪的普攻是物理伤害，没有特殊天赋加成普攻伤害。
        return calculate_physical_damage(self.final_base_atk, enemy.current_def)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (一锤定音)：
            # "下次攻击额外造成相当于攻击力200%的法术伤害；蓄力额外效果：攻击时攻击力提升至200%并使目标晕眩5秒"
            # 按照最高伤害计算，即蓄力效果。
            # 蓄力时：攻击时攻击力提升至200% (物理部分) + 额外造成相当于攻击力200%的法术伤害
            
            # 强化后的物理攻击力 (基础攻击力 * 200%)
            enhanced_physical_atk = self.final_base_atk * 2.0
            # 额外法术伤害的攻击力 (基础攻击力 * 200%)
            extra_arts_atk = self.final_base_atk * 2.0
            
            # 计算物理伤害
            physical_dmg = calculate_physical_damage(enhanced_physical_atk, enemy.current_def)
            # 计算法术伤害
            arts_dmg = calculate_arts_damage(extra_arts_atk, enemy.current_res)
            
            # 总伤害为物理伤害与法术伤害之和
            total_damage = physical_dmg + arts_dmg
            
            # 瞬发伤害技能，DPS为总伤除以普攻间隔
            return {"total_damage": total_damage, "dps": total_damage / actual_atk_interval}
            
        elif skill_index == 1:
            # 技能 2 (坚心苦修)：
            # "停止攻击，获得60%的庇护，每秒对周围所有地面敌人造成相当于攻击力140%的法术伤害，技能期间第一天赋的屏障获取效果提升100%"
            # 持续时间 duration = 20秒 (从JSON数据获取)
            # 每秒造成相当于攻击力140%的法术伤害
            
            skill_duration = 20 
            
            # 每秒法术伤害的攻击力 (基础攻击力 * 140%)
            dps_atk_val = self.final_base_atk * 1.4
            
            # 计算每秒造成的法术伤害
            damage_per_second = calculate_arts_damage(dps_atk_val, enemy.current_res)
            
            # 技能总伤害为每秒伤害乘以持续时间
            total_damage = damage_per_second * skill_duration
            
            # 技能期间停止普攻，但持续造成伤害，DPS即为每秒伤害
            return {"total_damage": total_damage, "dps": damage_per_second}
            
        elif skill_index == 2:
            # 技能 3 (披荆斩棘)：
            # "立即获得相当于生命上限130%的屏障，攻击间隔增大(+0.9)，攻击力+400%，自身更容易受到敌人攻击"
            # 持续时间 duration = 30秒 (从JSON数据获取)
            # 攻击间隔增大(+0.9)
            # 攻击力+400%
            
            skill_duration = 30
            
            # 攻击力加成：+400% 意味着最终攻击力是基础的 (1 + 4.0) 倍
            skill_atk_multiplier = 1 + 4.0 
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 攻击间隔增大：在基础攻击间隔上增加0.9
            # self.attack_interval 是干员的基础攻击间隔
            skill_base_atk_interval = self.attack_interval + 0.9
            # 技能期间的实际攻击间隔 = (基础攻击间隔 + 增大值) * 100 / 攻击速度
            skill_actual_atk_interval = skill_base_atk_interval * 100 / self.attack_speed
            
            # 计算单次普攻伤害 (物理伤害)
            single_hit_damage = calculate_physical_damage(enhanced_atk, enemy.current_def)
            
            # 计算技能持续期间的攻击次数
            hits_during_skill = skill_duration / skill_actual_atk_interval
            
            # 技能总伤害为攻击次数乘以单次普攻伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # 增益类技能，DPS为强化后的单次普攻伤害除以技能期间的实际攻击间隔
            return {"total_damage": total_damage, "dps": single_hit_damage / skill_actual_atk_interval}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)