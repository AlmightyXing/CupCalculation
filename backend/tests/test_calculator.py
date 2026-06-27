"""
核心计算引擎单元测试

测试用例基于：
  - 伤害计算.md 例1：真银斩（银灰技能）
  - character_sample.json：玛恩纳

运行：
    python -m pytest tests/ -v
"""

import pytest
from src.calculator.attribute import AttributeCalculator, build_atk_calculator, STANDARD_DEF, STANDARD_RES
from src.calculator.damage import (
    calc_physical_damage, calc_magic_damage, calc_element_damage,
    calc_true_damage, calc_heal, calc_damage_by_type
)
from src.calculator.dps import calc_attack_interval, calc_attacks_per_second, calc_manual_stats
from src.calculator.cup_rating import assign_cup_tier, calculate_cup_ratings, SUBRANK_WEIGHTS
from src.calculator.models import SkillParams, CharacterData, SkillData, CalculationResult


# ── 属性计算器测试 ──────────────────────────────────────────


class TestAttributeCalculator:
    def test_no_modifier_returns_base(self):
        """无修饰器时，最终值等于基础值"""
        calc = AttributeCalculator(1000.0)
        assert calc.calculate() == 1000.0

    def test_addition_modifier(self):
        """直接加算：1000 + 200 = 1200"""
        calc = AttributeCalculator(1000.0)
        calc.add_modifier("ADDITION", 200.0)
        assert calc.calculate() == 1200.0

    def test_multiplier_modifier(self):
        """直接乘算：1000 × (1 + 2.0) = 3000（+200%）"""
        calc = AttributeCalculator(1000.0)
        calc.add_modifier("MULTIPLIER", 2.0)
        assert calc.calculate() == 3000.0

    def test_final_scaler_modifier(self):
        """最终乘算：1000 × 0.3 = 300（防御-70%补正后的0.3）"""
        calc = AttributeCalculator(1000.0)
        # -70% 防御修饰 → 需要先补正为 -0.7 + 1 = 0.3，但 FINAL_SCALER 直接填补正后的值
        calc.add_modifier("FINAL_SCALER", 0.3)
        assert calc.calculate() == 300.0

    def test_negative_multiplier_correction(self):
        """直接乘算 < 0 时，(1 + D_t) 补正为 0，结果为最终加算部分"""
        calc = AttributeCalculator(1000.0)
        calc.add_modifier("MULTIPLIER", -1.5)  # 1 + (-1.5) = -0.5 < 0 → 补正为 0
        calc.add_modifier("FINAL_ADDITION", 500.0)
        # A_f = 1.0 × [(1000 + 0) × 0 + 500] = 500
        assert calc.calculate() == 500.0

    def test_full_formula_silver_ash_atk(self):
        """
        真银斩 例1：银灰攻击力计算
        - +200% 攻击力（直接乘算）：MULTIPLIER_ATK = 2.0
        - 假设银灰精二满级攻击力 = 791
        - 最终攻击力 = 791 × (1 + 2.0) = 791 × 3.0 = 2373
        注意：+200% 是直接乘算，不是 FINAL_SCALER
        """
        calc = AttributeCalculator(791.0)
        calc.add_modifier("MULTIPLIER", 2.0, source="真银斩攻击力+200%（直接乘算）")
        result = calc.calculate()
        assert result == pytest.approx(2373.0, rel=1e-3)

    def test_full_formula_combined(self):
        """
        综合测试：A=1000, ADDITION=100, MULTIPLIER=0.5, FINAL_SCALER=2.0
        = 2.0 × [(1000+100) × (1+0.5)] = 2.0 × [1100 × 1.5] = 2.0 × 1650 = 3300
        """
        calc = AttributeCalculator(1000.0)
        calc.add_modifier("ADDITION", 100.0)
        calc.add_modifier("MULTIPLIER", 0.5)
        calc.add_modifier("FINAL_SCALER", 2.0)
        assert calc.calculate() == pytest.approx(3300.0, rel=1e-3)


# ── 伤害公式测试 ────────────────────────────────────────────


class TestDamageFormulas:
    def test_physical_standard_baseline(self):
        """标准基准（DEF=1000）下物理伤害：2000 - 1000 = 1000"""
        dmg = calc_physical_damage(base_damage=2000.0, target_def=1000.0)
        assert dmg == pytest.approx(1000.0, rel=1e-3)

    def test_physical_minimum_5pct(self):
        """物理伤害最低为基本伤害的 5%"""
        dmg = calc_physical_damage(base_damage=100.0, target_def=10000.0)
        assert dmg == pytest.approx(5.0, rel=1e-3)

    def test_physical_penetration_pct(self):
        """50% 物理穿透：有效防御 = 1000 × 0.5 = 500，伤害 = 2000 - 500 = 1500"""
        dmg = calc_physical_damage(base_damage=2000.0, target_def=1000.0, penetration_pct=0.5)
        assert dmg == pytest.approx(1500.0, rel=1e-3)

    def test_physical_penetration_fixed(self):
        """固定物理穿透 200：有效防御 = 1000 - 200 = 800，伤害 = 2000 - 800 = 1200"""
        dmg = calc_physical_damage(base_damage=2000.0, target_def=1000.0, penetration_fixed=200.0)
        assert dmg == pytest.approx(1200.0, rel=1e-3)

    def test_magic_standard_baseline(self):
        """标准基准（RES=20）下法术伤害：0.01×A×(100-20) = 0.01×2000×80 = 1600"""
        dmg = calc_magic_damage(base_damage=2000.0, target_res=20.0)
        assert dmg == pytest.approx(1600.0, rel=1e-3)

    def test_magic_minimum_5pct(self):
        """法术伤害最低为基本伤害的 5%（极高法抗时）"""
        dmg = calc_magic_damage(base_damage=1000.0, target_res=100.0)
        assert dmg == pytest.approx(50.0, rel=1e-3)

    def test_true_damage_no_reduction(self):
        """真实伤害无减免，等于基本伤害"""
        assert calc_true_damage(1234.5) == 1234.5

    def test_heal_no_reduction(self):
        """治疗量无减免，等于基本伤害"""
        assert calc_heal(888.0) == 888.0

    def test_dispatch_unknown_type_raises(self):
        """未知伤害类型应抛出 ValueError"""
        with pytest.raises(ValueError, match="未知的伤害类型"):
            calc_damage_by_type("unknown", 1000.0)


# ── 攻速公式测试 ────────────────────────────────────────────


class TestAttackSpeed:
    def test_default_speed(self):
        """默认攻速 100，间隔不变：1.2 / (100/100) = 1.2s"""
        t = calc_attack_interval(base_atk_time=1.2, attack_speed=100)
        assert t == pytest.approx(1.2, rel=1e-3)

    def test_attack_time_extension(self):
        """技能攻击间隔延长 +0.3：(1.2+0.3) / 1.0 = 1.5s"""
        t = calc_attack_interval(base_atk_time=1.2, attack_speed=100, attack_time_reduction=0.3)
        assert t == pytest.approx(1.5, rel=1e-3)

    def test_speed_clamp_max(self):
        """攻速 clamp 上限 600：T = 1.2 / (600/100) = 0.2s"""
        t = calc_attack_interval(base_atk_time=1.2, attack_speed=9999)
        assert t == pytest.approx(1.2 / 6.0, rel=1e-3)

    def test_speed_clamp_min(self):
        """攻速 clamp 下限 10：T = 1.2 / (10/100) = 12.0s"""
        t = calc_attack_interval(base_atk_time=1.2, attack_speed=1)
        assert t == pytest.approx(12.0, rel=1e-3)

    def test_aps_from_interval(self):
        """攻速 = 1 / 间隔"""
        assert calc_attacks_per_second(1.5) == pytest.approx(1 / 1.5, rel=1e-3)


# ── 杯级评定测试 ────────────────────────────────────────────


class TestCupRating:
    def test_cup_tiers(self):
        """杯级阶梯划分验证"""
        assert assign_cup_tier(0.05) == "超大杯·上"
        assert assign_cup_tier(0.15) == "超大杯·中"
        assert assign_cup_tier(0.25) == "超大杯·下"
        assert assign_cup_tier(0.40) == "大杯"
        assert assign_cup_tier(0.60) == "中杯"
        assert assign_cup_tier(0.99) == "中杯"

    def test_single_operator_gets_top_tier(self):
        """只有一个干员时，排名第一，杯级为超大杯·上"""
        results = [
            CalculationResult(
                character_id="char_001_test",
                character_name="测试干员",
                skill_id=0,
                skill_name="测试技能",
                skill_type="manual",
                manual_dps=5000.0,
                manual_damage_total=100000.0,
            )
        ]
        ranked = calculate_cup_ratings(results)
        assert len(ranked) == 1
        assert ranked[0].cup_level == "超大杯·上"
        assert ranked[0].rank == 1

    def test_ranking_order_by_score(self):
        """高 DPS 干员应排在低 DPS 干员前面"""
        results = [
            CalculationResult("char_low", "低DPS干员", 0, "技能", "manual", manual_dps=1000.0),
            CalculationResult("char_high", "高DPS干员", 0, "技能", "manual", manual_dps=5000.0),
        ]
        ranked = calculate_cup_ratings(results)
        assert ranked[0].character_id == "char_high"
        assert ranked[1].character_id == "char_low"

    def test_peak_bonus_triggers_for_top10(self):
        """
        巅峰加权测试：模拟 12 个干员，前 10 名享受 300% 乘数
        第 1 名的综合分应显著高于第 11 名
        """
        results = []
        # 创建 12 个干员，DPS 依次递减
        for i in range(12):
            results.append(CalculationResult(
                character_id=f"char_{i:03d}",
                character_name=f"干员{i:03d}",
                skill_id=0,
                skill_name="技能",
                skill_type="manual",
                manual_dps=float(12 - i) * 1000,
            ))
        ranked = calculate_cup_ratings(results)
        # 第 1 名（有巅峰加权）排名应在最前
        assert ranked[0].character_id == "char_000"
        # 总共 12 个干员
        assert len(ranked) == 12


# ── 端到端集成测试（使用玛恩纳示例数据）─────────────────────


class TestIntegration:
    """
    集成测试：手动构造玛恩纳数据（无需 LLM）
    用技能2"未照耀的荣光"验证：
      - 攻击力提升至 180%（FINAL_SCALER_ATK=1.8）
      - 攻击5个目标（hits=5，但榜单仅计单目标）
      - 物理伤害，持续 28 秒
    """

    def _make_mlynar(self) -> CharacterData:
        """构造精二满级玛恩纳（含信赖）"""
        params = SkillParams(
            FINAL_SCALER_ATK=1.8,
            hits=1,            # 榜单按单目标计算
            damage_type="physical",
            attck_speed_addition=0,
            attack_time_reduction=0.0,
        )
        skill = SkillData(
            skill_id=2,
            skill_name="未照耀的荣光",
            skill_type="manual",
            duration=28.0,
            description="(测试用，已手动填充 skill_params)",
            skill_params=params,
        )
        return CharacterData(
            character_id="char_325_mlynar",
            name="玛恩纳",
            nickname=["老玛", "叔叔"],
            base_atk=355 + 30,  # base_atk + confidence_atk = 385
            base_hp=3906 + 360,
            base_def=502,
            base_res=15,
            atk_time=1.2,
            skills=[skill],
        )

    def test_mlynar_final_atk(self):
        """
        玛恩纳攻击力验证：
        FINAL_SCALER_ATK=1.8 → 最终攻击力 = 385 × 1.8 = 693
        """
        char = self._make_mlynar()
        params = char.skills[0].skill_params
        calc = build_atk_calculator(char.base_atk, params)
        final_atk = calc.calculate()
        assert final_atk == pytest.approx(693.0, rel=1e-3)

    def test_mlynar_physical_damage_at_standard(self):
        """
        玛恩纳对标准基准（DEF=1000）的物理伤害：
        max(0.05×693, 693 - 1000) = max(34.65, -307) = 34.65（5%下限）
        """
        final_atk = 693.0
        dmg = calc_physical_damage(base_damage=final_atk, target_def=STANDARD_DEF)
        assert dmg == pytest.approx(34.65, rel=1e-3)

    def test_mlynar_manual_total_damage(self):
        """
        玛恩纳决战总伤验证：
        - 攻击间隔 1.2s，攻速 100 → APS = 1/1.2 ≈ 0.833
        - 单次伤害 34.65
        - 总伤 = 34.65 × 1 × (1/1.2) × 28 ≈ 808.5
        """
        char = self._make_mlynar()
        results = [r for r in __import__("src.calculator.dps", fromlist=["calculate_operator_stats"]).calculate_operator_stats(char)]
        assert len(results) == 1
        total = results[0].manual_damage_total
        expected = 34.65 * (1 / 1.2) * 28
        assert total == pytest.approx(expected, rel=0.01)
