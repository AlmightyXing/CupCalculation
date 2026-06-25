"""
杯级评定算法
实现 PRD §5.3 的非线性加权评分算法：

  1. 基础分：根据干员在各子榜单的百分比排名换算
  2. 巅峰加权（Peak Bonus）：进入全干员前 10 名享受 300% 乘数
  3. 杯级阶梯：按综合排名百分比划分五档

子榜单权重定义：
  - 挂机 DPS / HPS：各 1.0（基础单项权重）
  - 决战 DPS / HPS：各 1.0
  - 决战总伤 / 总治疗：各 1.0（PRD v1.1 新增）
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .models import CalculationResult, RankedOperator


# ── 杯级阶梯定义（PRD §5.3）───────────────────────────────
CUP_TIERS = [
    (0.10, "超大杯·上"),
    (0.20, "超大杯·中"),
    (0.30, "超大杯·下"),
    (0.50, "大杯"),
    (1.01, "中杯"),
]

# ── 评分参数 ──────────────────────────────────────────────
PEAK_BONUS_MULTIPLIER = 3.0    # 巅峰加权乘数：进入前 10 享受 300%
PEAK_BONUS_THRESHOLD = 10      # 巅峰加权触发名次阈值

# 各子榜单权重（可在此调整）
SUBRANK_WEIGHTS: Dict[str, float] = {
    "auto_dps":            1.0,
    "auto_hps":            1.0,
    "manual_dps":          1.0,
    "manual_hps":          1.0,
    "manual_damage_total": 1.0,
    "manual_heal_total":   1.0,
}


@dataclass
class SubrankScore:
    """干员在单个子榜单上的得分信息"""
    field_name: str       # 子榜单字段名，如 "auto_dps"
    raw_value: float      # 原始数值
    rank: int             # 排名（1-based）
    total: int            # 参与排名的总干员数
    percentile: float     # 百分比排名（0~1，越小越好）
    base_score: float     # 百分比排名换算的基础分（0~100）
    peak_bonus: bool      # 是否触发巅峰加权
    weighted_score: float # 最终加权得分


def _percentile_to_score(percentile: float) -> float:
    """
    百分比排名 → 基础分换算（线性，顶名=100，末名≈0）。
    percentile 越小（排名越靠前）得分越高。
    """
    return (1.0 - percentile) * 100.0


def rank_sublist(
    results: List[CalculationResult],
    field: str,
) -> Dict[str, SubrankScore]:
    """
    对所有干员在指定子榜单字段排名，返回 {character_id: SubrankScore}。

    只统计该字段有值（非 None、非 0）的干员。
    """
    # 提取有效数据：(character_id, value)
    valid_entries = [
        (r.character_id, getattr(r, field))
        for r in results
        if getattr(r, field) is not None and getattr(r, field) > 0
    ]

    if not valid_entries:
        return {}

    # 降序排列（数值越大，排名越靠前）
    sorted_entries = sorted(valid_entries, key=lambda x: x[1], reverse=True)
    total = len(sorted_entries)

    scores: Dict[str, SubrankScore] = {}
    for rank_idx, (char_id, value) in enumerate(sorted_entries, start=1):
        percentile = (rank_idx - 1) / total  # 0 = 第一名
        base_score = _percentile_to_score(percentile)
        peak_bonus = rank_idx <= PEAK_BONUS_THRESHOLD

        # 巅峰加权：进入前 10 名时基础分 × 300%
        weighted = base_score * PEAK_BONUS_MULTIPLIER if peak_bonus else base_score
        weighted *= SUBRANK_WEIGHTS.get(field, 1.0)

        scores[char_id] = SubrankScore(
            field_name=field,
            raw_value=value,
            rank=rank_idx,
            total=total,
            percentile=percentile,
            base_score=base_score,
            peak_bonus=peak_bonus,
            weighted_score=weighted,
        )

    return scores


def assign_cup_tier(percentile: float) -> str:
    """
    根据干员综合总分的百分比排名分配杯级标签。

    Args:
        percentile: 综合排名百分比（0~1，0 为第一名）

    Returns:
        杯级标签字符串
    """
    for threshold, label in CUP_TIERS:
        if percentile < threshold:
            return label
    return "中杯"


def calculate_cup_ratings(
    all_results: List[CalculationResult],
) -> List[RankedOperator]:
    """
    对所有干员的计算结果进行综合评分和杯级评定。

    算法步骤：
      1. 对每个子榜单独立排名
      2. 汇总每个干员在所有子榜单的加权得分
      3. 对综合总分排名，按百分比分配杯级

    Args:
        all_results: 所有干员所有技能的 CalculationResult 列表

    Returns:
        按综合排名排序的 RankedOperator 列表
    """
    # ── Step 1：将多技能结果聚合为每干员的最优值 ─────────────
    # 对于同一干员的多个技能，取各字段的最大值参与排名
    best_by_char: Dict[str, Dict[str, float]] = {}
    char_meta: Dict[str, tuple] = {}  # character_id → (name, nickname)

    for r in all_results:
        cid = r.character_id
        if cid not in best_by_char:
            best_by_char[cid] = {}
            char_meta[cid] = (r.character_name, [])  # nickname 留给外部填充

        for field in SUBRANK_WEIGHTS:
            val = getattr(r, field)
            if val is not None and val > 0:
                best_by_char[cid][field] = max(
                    best_by_char[cid].get(field, 0.0), val
                )

    # 构建平展后的伪 CalculationResult 列表（每干员一条）
    flat_results: List[CalculationResult] = []
    for cid, fields in best_by_char.items():
        name, nickname = char_meta[cid]
        cr = CalculationResult(
            character_id=cid,
            character_name=name,
            skill_id=-1,
            skill_name="(best)",
            skill_type="",
        )
        for field, val in fields.items():
            setattr(cr, field, val)
        flat_results.append(cr)

    # ── Step 2：各子榜单独立排名 ──────────────────────────────
    subrank_maps: Dict[str, Dict[str, SubrankScore]] = {}
    for field in SUBRANK_WEIGHTS:
        subrank_maps[field] = rank_sublist(flat_results, field)

    # ── Step 3：汇总每干员综合得分 ────────────────────────────
    total_scores: Dict[str, float] = {}
    subranks_by_char: Dict[str, Dict[str, SubrankScore]] = {}

    for cid in best_by_char:
        score = 0.0
        subranks_by_char[cid] = {}
        for field, subrank_map in subrank_maps.items():
            if cid in subrank_map:
                score += subrank_map[cid].weighted_score
                subranks_by_char[cid][field] = subrank_map[cid]
        total_scores[cid] = score

    # ── Step 4：综合总分排名 → 杯级评定 ──────────────────────
    sorted_chars = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    total_operators = len(sorted_chars)

    ranked_operators: List[RankedOperator] = []
    for overall_rank, (cid, _score) in enumerate(sorted_chars, start=1):
        percentile = (overall_rank - 1) / total_operators
        cup_level = assign_cup_tier(percentile)
        name, nickname = char_meta[cid]

        ro = RankedOperator(
            character_id=cid,
            name=name,
            nickname=nickname,
            cup_level=cup_level,
            rank=overall_rank,
        )

        # 填充各子榜单排名和数值
        for field, sr in subranks_by_char[cid].items():
            match field:
                case "auto_dps":
                    ro.auto_dps = int(sr.raw_value)
                    ro.auto_dps_rank = sr.rank
                case "auto_hps":
                    ro.auto_hps = int(sr.raw_value)
                    ro.auto_hps_rank = sr.rank
                case "manual_dps":
                    ro.manual_dps = int(sr.raw_value)
                    ro.manual_dps_rank = sr.rank
                case "manual_hps":
                    ro.manual_hps = int(sr.raw_value)
                    ro.manual_hps_rank = sr.rank
                case "manual_damage_total":
                    ro.manual_damage_total = int(sr.raw_value)
                    ro.manual_damage_total_rank = sr.rank
                case "manual_heal_total":
                    ro.manual_heal_total = int(sr.raw_value)
                    ro.manual_heal_total_rank = sr.rank

        ranked_operators.append(ro)

    return ranked_operators
