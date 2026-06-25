"""
伤害公式计算器
实现《明日方舟》伤害计算.md 中定义的五种伤害类型：

  物理伤害: DMG_p  = max(0.05A, A - [(1-Ip) × max(0, D - Iv)])
  法术伤害: DMG_a  = max(0.05A, 0.01A × max(0, 100 - (1-Ip) × max(0, D - Iv)))
  元素伤害: DMG_e  = max(0.05A, 0.01A × max(0, 100 - D))
  真实伤害: DMG_pu = A
  治疗量  : DMG_h  = A

计算基准（PRD §5.1）：
  物理防御 DEF = 1000
  法术抗性 RES = 20（用户确认值）
"""

from .attribute import STANDARD_DEF, STANDARD_RES


def calc_physical_damage(
    base_damage: float,
    target_def: float = STANDARD_DEF,
    penetration_pct: float = 0.0,
    penetration_fixed: float = 0.0,
) -> float:
    """
    物理伤害公式：
        DMG_p = max(0.05A, A - [(1 - Ip) × max(0, D - Iv)])

    Args:
        base_damage:        基本伤害值 A（攻击力 × 攻击力倍率）
        target_def:         目标防御力 D，默认使用标准基准
        penetration_pct:    物理穿透（百分比）Ip，范围 [0, 1]
        penetration_fixed:  物理穿透（固定值）Iv

    Returns:
        最终物理伤害值
    """
    # 有效防御 = (1 - 穿透%) × max(0, 防御 - 固定穿透)
    effective_def = (1.0 - penetration_pct) * max(0.0, target_def - penetration_fixed)
    damage = base_damage - effective_def
    # 物理伤害最低为基本伤害的 5%
    return max(0.05 * base_damage, damage)


def calc_magic_damage(
    base_damage: float,
    target_res: float = STANDARD_RES,
    penetration_pct: float = 0.0,
    penetration_fixed: float = 0.0,
) -> float:
    """
    法术伤害公式：
        DMG_a = max(0.05A, 0.01A × max(0, 100 - (1 - Ip) × max(0, D - Iv)))

    Args:
        base_damage:        基本伤害值 A
        target_res:         目标法术抗性 D（0~100），默认使用标准基准
        penetration_pct:    法术穿透（百分比）Ip，范围 [0, 1]
        penetration_fixed:  法术穿透（固定值）Iv

    Returns:
        最终法术伤害值
    """
    effective_res = (1.0 - penetration_pct) * max(0.0, target_res - penetration_fixed)
    resist_factor = max(0.0, 100.0 - effective_res)
    damage = 0.01 * base_damage * resist_factor
    # 法术伤害最低为基本伤害的 5%
    return max(0.05 * base_damage, damage)


def calc_element_damage(
    base_damage: float,
    target_element_res: float = 0.0,
) -> float:
    """
    元素伤害公式：
        DMG_e = max(0.05A, 0.01A × max(0, 100 - D))

    元素伤害无穿透参数，抗性默认为 0（大多数敌人）。

    Args:
        base_damage:        基本伤害值 A
        target_element_res: 目标元素抗性 D

    Returns:
        最终元素伤害值
    """
    resist_factor = max(0.0, 100.0 - target_element_res)
    damage = 0.01 * base_damage * resist_factor
    return max(0.05 * base_damage, damage)


def calc_true_damage(base_damage: float) -> float:
    """
    真实伤害公式：
        DMG_pu = A（无任何减免）
    """
    return base_damage


def calc_heal(base_damage: float) -> float:
    """
    治疗量公式：
        DMG_h = A（无任何减免）
    """
    return base_damage


def calc_damage_by_type(
    damage_type: str,
    base_damage: float,
    target_def: float = STANDARD_DEF,
    target_res: float = STANDARD_RES,
    target_element_res: float = 0.0,
    penetration_pct: float = 0.0,
    penetration_fixed: float = 0.0,
) -> float:
    """
    统一入口：根据伤害类型分发到对应公式。

    Args:
        damage_type:      伤害类型字符串：
                          "physical" | "magic" | "element" | "true" | "heal"
        base_damage:      基本伤害值 A
        target_def:       目标防御力（物理伤害使用）
        target_res:       目标法术抗性（法术伤害使用）
        target_element_res: 目标元素抗性（元素伤害使用）
        penetration_pct:  穿透（百分比）
        penetration_fixed: 穿透（固定值）

    Returns:
        最终伤害或治疗量

    Raises:
        ValueError: 未知的伤害类型
    """
    match damage_type:
        case "physical":
            return calc_physical_damage(
                base_damage, target_def, penetration_pct, penetration_fixed
            )
        case "magic":
            return calc_magic_damage(
                base_damage, target_res, penetration_pct, penetration_fixed
            )
        case "element":
            return calc_element_damage(base_damage, target_element_res)
        case "true":
            return calc_true_damage(base_damage)
        case "heal":
            return calc_heal(base_damage)
        case _:
            raise ValueError(f"未知的伤害类型：{damage_type!r}，"
                             "应为 'physical'/'magic'/'element'/'true'/'heal' 之一")
