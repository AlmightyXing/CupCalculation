from typing import Dict, Any, List
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

class Operator:
    """
    所有干员的基础抽象类。
    """
    def __init__(self, data: Dict[str, Any]):
        self.character_id = data.get("character_id", "")
        self.name = data.get("name", "")
        self.profession = data.get("character_type", "")
        
        # 基础面板
        self.base_atk = data.get("base_atk", 0)
        self.base_def = data.get("base_def", 0)
        self.base_hp = data.get("base_hp", 0)
        self.base_res = data.get("base_res", 0.0)
        
        # 默认伤害类型 (physical 或 arts)，默认物理
        self.damage_type = "physical"
        
        # 由职业父类或具体子类设定的属性
        self.attack_speed = 100
        self.attack_interval = 1.0
        self.block_count = 1
        self.redeploy_time = 70
        
        # 其他存储技能、天赋的信息
        self.skills = data.get("skills", [])
        self.raw_data = data
        
    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        """
        模板方法：计算单次普攻命中时的总期望伤害。
        子类如果拥有独特的普攻特效（例如破甲概率，或者连击），可在此覆写。
        默认返回基础的物理或法术伤害，不计算乘区加成（子类自己维护 final_atk）。
        这里默认使用基础 base_atk，真实情况应由子类重写传入其结算完天赋后的 atk。
        """
        atk_val = self.base_atk
        if self.damage_type == "physical":
            return calculate_physical_damage(atk_val, enemy.current_def) * target_count
        else:
            return calculate_arts_damage(atk_val, enemy.current_res) * target_count

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> Dict[str, float]:
        """
        模板方法：由子类必须覆写，返回对应技能（skill_index）单次施放的总伤和DPS。
        返回格式: {"total_damage": float, "dps": float}
        """
        return {"total_damage": 0.0, "dps": 0.0}

    def calculate_dps(self, enemy, skill_index: int = -1, target_count: int = 1) -> Dict[str, float]:
        """
        全局统一的主接口。集中实现周期回转与DPS结算算法。
        """
        # 强制 target_count 为 1
        target_count = 1
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == -1:
            total_damage = self.calculate_normal_hit(enemy, target_count)
            dps = total_damage / actual_atk_interval if actual_atk_interval > 0 else 0
            return {"dps": dps, "total_damage": total_damage}
            
        # 调用子类提供的技能总伤逻辑
        skill_res = self.calculate_skill_damage(enemy, skill_index, target_count)
        skill_dmg = skill_res.get("total_damage", 0.0)
        skill_dps = skill_res.get("dps", 0.0)
        
        # --- 全局周期 DPS 演算逻辑 ---
        if skill_index >= len(self.skills):
            return {"total_damage": skill_dmg, "dps": skill_dps}
            
        skill_info = self.skills[skill_index]
        skill_type = skill_info.get("skill_type", "manual")
        duration = skill_info.get("duration", 0)
        if duration is None:
            duration = 0
            
        consume_sp = skill_info.get("consume_sp")
        
        # Manual 技能只计算释放期间
        if skill_type == "manual":
            return {
                "total_damage": skill_dmg,
                "dps": skill_dps
            }
            
        # Auto 技能处理
        if skill_type == "auto":
            # 如果没有消耗SP或者无限持续时间，按永续处理
            if consume_sp is None or duration <= 0:
                return {
                    "total_damage": skill_dmg,
                    "dps": skill_dps
                }
                
            is_atk_sp = skill_info.get("attack_supplement", False)
            is_auto_sp = skill_info.get("auto_supplement", False)
            
            normal_hit_dmg = self.calculate_normal_hit(enemy, target_count)
            
            if is_atk_sp:
                charge_time = consume_sp * actual_atk_interval
                normal_attacks_dmg = consume_sp * normal_hit_dmg
            elif is_auto_sp:
                charge_time = consume_sp
                num_attacks = charge_time / actual_atk_interval
                normal_attacks_dmg = num_attacks * normal_hit_dmg
            else:
                charge_time = 0
                normal_attacks_dmg = 0
                
            cycle_time = charge_time + duration
            cycle_dmg = normal_attacks_dmg + skill_dmg
            cycle_dps = cycle_dmg / cycle_time if cycle_time > 0 else 0
            
            return {
                "total_damage": skill_dmg,
                "cycle_total_damage": cycle_dmg,
                "cycle_time": cycle_time,
                "cycle_dps": cycle_dps,
                "dps": skill_dps
            }
            
        return {"total_damage": skill_dmg, "dps": skill_dps}

    def __str__(self):
        return f"[{self.profession}] {self.name} (ATK: {self.base_atk})"
