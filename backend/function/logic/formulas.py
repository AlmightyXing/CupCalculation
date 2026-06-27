# backend/function/logic/formulas.py

def calculate_physical_damage(atk: float, enemy_def: float, def_ignore_ratio: float = 0.0, def_ignore_flat: float = 0.0) -> float:
    """
    计算单次物理伤害（含抛光线判断，保底伤害为攻击力的 5%）
    """
    # 敌人实际防御
    actual_def = max(0, enemy_def * (1.0 - def_ignore_ratio) - def_ignore_flat)
    
    damage = atk - actual_def
    min_damage = atk * 0.05
    
    return max(damage, min_damage)

def calculate_arts_damage(atk: float, enemy_res: float, res_ignore_flat: float = 0.0) -> float:
    """
    计算单次法术伤害（法抗减伤，保底伤害为攻击力的 5%）
    """
    actual_res = max(0, enemy_res - res_ignore_flat)
    actual_res = min(actual_res, 100) # 法抗最高100对应100%减伤（不考虑特殊情况）
    
    damage_multiplier = max(1.0 - actual_res / 100.0, 0.0)
    damage = atk * damage_multiplier
    min_damage = atk * 0.05
    
    return max(damage, min_damage)
