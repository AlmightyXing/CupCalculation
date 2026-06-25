"""
计算流水线入口脚本

使用方式：
    # 完整流水线（LLM 解析 + 计算 + 评级）：
    python pipeline.py --input data/processed --output data/output/result.json

    # 仅重新计算（跳过 LLM，使用已有缓存）：
    python pipeline.py --input data/processed --output data/output/result.json --skip-llm

    # 测试单个干员：
    python pipeline.py --single character_sample.json
"""

import argparse
import json
from pathlib import Path

from src.calculator.dps import calculate_operator_stats
from src.calculator.cup_rating import calculate_cup_ratings
from src.parser.data_loader import load_character, load_all_characters


def run_pipeline(
    input_dir: Path,
    output_file: Path,
    skip_llm: bool = False,
) -> None:
    """
    完整流水线：加载所有干员 → LLM 解析 → 计算 → 评级 → 输出 JSON
    """
    print(f"\n{'='*50}")
    print(f"  杯级计算器流水线")
    print(f"{'='*50}")
    print(f"  输入目录：{input_dir}")
    print(f"  输出文件：{output_file}")
    print(f"  跳过 LLM：{skip_llm}")
    print(f"{'='*50}\n")

    # Step 1：加载所有干员
    print("【Step 1】加载干员数据...")
    chars = load_all_characters(input_dir)
    print(f"  共加载 {len(chars)} 位干员\n")

    if not chars:
        print("✗ 未找到干员 JSON 文件，请将干员数据放入 data/processed/ 目录")
        return

    # Step 2：LLM 解析（可跳过）
    if not skip_llm:
        print("【Step 2】LLM 技能解析（DeepSeek API）...")
        from src.parser.llm_parser import parse_character_skills
        processed_dir = input_dir / "llm_cache"
        for char in chars:
            print(f"  处理干员：{char.name}")
            parse_character_skills(char, processed_dir)
        print()
    else:
        print("【Step 2】跳过 LLM 解析（使用已有 skill_params）\n")

    # Step 3：计算所有干员数值
    print("【Step 3】计算 DPS / HPS / 总伤...")
    all_results = []
    for char in chars:
        results = calculate_operator_stats(char)
        all_results.extend(results)
        parsed_count = sum(1 for r in results if r.auto_dps or r.manual_dps or r.auto_hps or r.manual_hps)
        print(f"  {char.name}：{parsed_count}/{len(char.skills)} 个技能已计算")
    print()

    # Step 4：杯级评定
    print("【Step 4】综合评分与杯级评定...")
    ranked = calculate_cup_ratings(all_results)
    print(f"  共评定 {len(ranked)} 位干员\n")

    # Step 5：输出结果
    print("【Step 5】输出结果...")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_data = []
    for ro in ranked:
        output_data.append({
            "character_id": ro.character_id,
            "name": ro.name,
            "nickname": ro.nickname,
            "cup_level": ro.cup_level,
            "rank": ro.rank,
            "auto_dps": ro.auto_dps,
            "auto_dps_rank": ro.auto_dps_rank,
            "auto_hps": ro.auto_hps,
            "auto_hps_rank": ro.auto_hps_rank,
            "manual_dps": ro.manual_dps,
            "manual_dps_rank": ro.manual_dps_rank,
            "manual_hps": ro.manual_hps,
            "manual_hps_rank": ro.manual_hps_rank,
            "manual_damage_total": ro.manual_damage_total,
            "manual_damage_total_rank": ro.manual_damage_total_rank,
            "manual_heal_total": ro.manual_heal_total,
            "manual_heal_total_rank": ro.manual_heal_total_rank,
        })

    output_file.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✓ 结果已保存到 {output_file}\n")

    # 打印简报
    print("【综合排行榜（前20名）】")
    print(f"{'排名':>4}  {'杯级':<10}  {'干员名称':<12}  {'挂机DPS':>8}  {'决战总伤':>10}")
    print("-" * 56)
    for ro in ranked[:20]:
        print(
            f"{ro.rank:>4}  {ro.cup_level:<10}  {ro.name:<12}  "
            f"{ro.auto_dps or '-':>8}  {ro.manual_damage_total or '-':>10}"
        )


def run_single(json_path: Path) -> None:
    """测试模式：计算单个干员并打印详细结果"""
    print(f"\n测试单干员：{json_path}\n")
    char = load_character(json_path)

    print(f"干员：{char.name}（{char.character_type}）")
    print(f"  攻击力：{char.base_atk}  攻速：{char.attack_speed}  攻击间隔：{char.atk_time}s")
    print(f"  技能数量：{len(char.skills)}")

    results = calculate_operator_stats(char)
    if not results:
        print("\n  ⚠ 无已解析的技能（skill_params 为空），请先运行 LLM 解析")
        return

    print("\n计算结果：")
    for r in results:
        print(f"\n  [{r.skill_name}] ({r.skill_type})")
        if r.auto_dps:
            print(f"    挂机 DPS : {r.auto_dps:.1f}")
        if r.auto_hps:
            print(f"    挂机 HPS : {r.auto_hps:.1f}")
        if r.manual_dps:
            print(f"    决战 DPS : {r.manual_dps:.1f}")
        if r.manual_damage_total:
            print(f"    决战总伤 : {r.manual_damage_total:.0f}")
        if r.manual_hps:
            print(f"    决战 HPS : {r.manual_hps:.1f}")
        if r.manual_heal_total:
            print(f"    决战总治 : {r.manual_heal_total:.0f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="杯级计算器流水线")
    parser.add_argument("--input", type=Path, default=Path("data/processed"),
                        help="干员 JSON 输入目录")
    parser.add_argument("--output", type=Path, default=Path("data/output/result.json"),
                        help="输出结果 JSON 路径")
    parser.add_argument("--skip-llm", action="store_true",
                        help="跳过 LLM 解析（使用已有 skill_params）")
    parser.add_argument("--single", type=Path, default=None,
                        help="测试单个干员 JSON 文件路径")

    args = parser.parse_args()

    if args.single:
        run_single(args.single)
    else:
        run_pipeline(args.input, args.output, skip_llm=args.skip_llm)
