"""
DPS / HPS / 总伤计算器
整合属性计算器和伤害公式，输出 PRD §5.2 定义的两类场景数值：

  挂机榜 (auto)：
    - 永续/被动技能 → 持续 DPS/HPS
    - 自动释放技能 → 全周期平均 DPS/HPS（含技力回转时间）

  决战榜 (manual)：
    - 技能持续期间的 总伤害/总治疗量
    - 技能持续期间的 平均 DPS/HPS

攻速公式（伤害计算.md §攻速公式）：
    实际攻击间隔 T = T0 / (clamp(S, 10, 600) / 100)
    每秒攻击次数 = 1 / T
"""

from .attribute import STANDARD_DEF, STANDARD_RES, build_atk_calculator
from .damage import calc_damage_by_type
from .models import CharacterData, SkillData, SkillParams, CalculationResult


def _clamp(value: float, lo: float, hi: float) -> float:
    """区间限定函数：将 value 限定在 [lo, hi] 内"""
    return max(lo, min(hi, value))


def calc_attack_interval(
    base_atk_time: float,
    attack_speed: int = 100,
    attack_time_reduction: float = 0.0,
) -> float:
    """
    计算实际攻击间隔（秒）。

    公式：T = (T0 + reduction) / (clamp(S, 10, 600) / 100)
    其中 reduction 为技能对攻击间隔的直接加减（正数延长，负数缩短）

    Args:
        base_atk_time:        基础攻击间隔 T0（秒）
        attack_speed:         攻击速度 S（默认 100）
        attack_time_reduction: 技能对攻击间隔的修正值（秒）
                              正数=延长（如"+0.3"），负数=缩短

    Returns:
        实际攻击间隔（秒）
    """
    effective_time = base_atk_time + attack_time_reduction
    speed_factor = _clamp(attack_speed, 10, 600) / 100.0
    return effective_time / speed_factor


def calc_attacks_per_second(attack_interval: float) -> float:
    """每秒攻击次数 = 1 / 实际攻击间隔"""
    if attack_interval <= 0:
        return 0.0
    return 1.0 / attack_interval


def _calc_base_atk(char: CharacterData, params: SkillParams) -> float:
    """
    计算技能激活后的最终攻击力（已经过四修饰器公式处理）。

    Returns:
        最终攻击力值
    """
    calc = build_atk_calculator(char.base_atk, params)
    return calc.calculate(attr_min=0.0)


def _calc_single_hit_damage(
    final_atk: float,
    params: SkillParams,
    target_def: float = STANDARD_DEF,
    target_res: float = STANDARD_RES,
) -> float:
    """
    计算单次打击伤害（攻击力 × 倍率后套入伤害公式）。

    Returns:
        单次打击伤害值
    """
    # 基本伤害 = 最终攻击力（倍率已在属性计算器中处理）
    return calc_damage_by_type(
        damage_type=params.damage_type,
        base_damage=final_atk,
        target_def=target_def,
        target_res=target_res,
        penetration_pct=params.defence_penetration if params.damage_type == "physical"
                        else params.res_penetration,
        penetration_fixed=params.defence_penetration_fixed if params.damage_type == "physical"
                          else params.res_penetration_fixed,
    )


def calc_auto_dps(
    char: CharacterData,
    params: SkillParams,
    charge_time: float = 0.0,
    target_def: float = STANDARD_DEF,
    target_res: float = STANDARD_RES,
) -> float:
    """
    挂机榜 DPS/HPS 计算。

    对于永续/被动技能（charge_time=0）：
        DPS = 单次打击伤害 × 每次攻击打击数 × 每秒攻击次数

    对于自动释放技能（charge_time>0）：
        DPS = 技能期间总伤 / (技能时长 + 充能时间)
        即全周期平均 DPS

    Args:
        char:         干员数据
        params:       技能结构化参数
        charge_time:  充能时间（秒），0 表示永续技能
        target_def:   目标防御力
        target_res:   目标法术抗性

    Returns:
        DPS 或 HPS 数值
    """
    final_atk = _calc_base_atk(char, params)
    single_hit_dmg = _calc_single_hit_damage(final_atk, params, target_def, target_res)

    # 技能激活时的攻速
    effective_speed = char.attack_speed + params.attck_speed_addition
    interval = calc_attack_interval(char.atk_time, effective_speed, params.attack_time_reduction)
    aps = calc_attacks_per_second(interval)  # 每秒攻击次数

    # 每秒输出 = 单次伤害 × 连击数 × 攻速
    dps_per_second = single_hit_dmg * params.hits * aps

    if charge_time <= 0:
        # 永续技能：直接返回持续 DPS
        return dps_per_second
    else:
        # 自动释放技能：全周期平均 DPS
        # 技能持续时间内的总伤害（假设技能期间攻击无损失）
        skill_duration = params.attack_time_reduction  # 此处 charge_time 由外部传入
        # 若 skill_duration 为 0，仅使用传入的 charge_time 做分母
        total_cycle = (skill_duration if skill_duration > 0 else 0) + charge_time
        if total_cycle <= 0:
            return dps_per_second
        skill_total_dmg = dps_per_second * (total_cycle - charge_time) if skill_duration > 0 else 0
        return skill_total_dmg / total_cycle


def calc_manual_stats(
    char: CharacterData,
    params: SkillParams,
    duration: float,
    target_def: float = STANDARD_DEF,
    target_res: float = STANDARD_RES,
) -> tuple[float, float]:
    """
    决战榜计算：返回 (总伤/总治疗, 期间平均DPS/HPS)。

    Args:
        char:      干员数据
        params:    技能结构化参数
        duration:  技能持续时间（秒）
        target_def: 目标防御力
        target_res: 目标法术抗性

    Returns:
        (total_damage, avg_dps) — 元组
    """
    final_atk = _calc_base_atk(char, params)
    single_hit_dmg = _calc_single_hit_damage(final_atk, params, target_def, target_res)

    effective_speed = char.attack_speed + params.attck_speed_addition
    interval = calc_attack_interval(char.atk_time, effective_speed, params.attack_time_reduction)
    aps = calc_attacks_per_second(interval)

    # 技能期间的总伤害 = 单次伤害 × 连击数 × 攻速 × 持续时间
    total_damage = single_hit_dmg * params.hits * aps * duration
    avg_dps = total_damage / duration if duration > 0 else 0.0

    return total_damage, avg_dps


def calculate_operator_stats(
    char: CharacterData,
    target_def: float = STANDARD_DEF,
    target_res: float = STANDARD_RES,
) -> list[CalculationResult]:
    """
    计算干员所有技能的完整数值，返回 CalculationResult 列表。

    仅处理已经过 LLM 解析、skill_params 不为 None 的技能。
    """
    results = []

    for skill in char.skills:
        if skill.skill_params is None:
            # 跳过尚未被 LLM 解析的技能
            continue

        params = skill.skill_params
        result = CalculationResult(
            character_id=char.character_id,
            character_name=char.name,
            skill_id=skill.skill_id,
            skill_name=skill.skill_name,
            skill_type=skill.skill_type,
        )

        if skill.skill_type == "auto":
            # 挂机榜
            dps = calc_auto_dps(char, params, charge_time=0, target_def=target_def, target_res=target_res)
            if params.damage_type == "heal":
                result.auto_hps = dps
            else:
                result.auto_dps = dps

        elif skill.skill_type == "manual":
            # 决战榜
            duration = skill.duration or 0.0
            total, avg = calc_manual_stats(char, params, duration, target_def, target_res)
            if params.damage_type == "heal":
                result.manual_hps = avg
                result.manual_heal_total = total
            else:
                result.manual_dps = avg
                result.manual_damage_total = total

        results.append(result)

    return results
