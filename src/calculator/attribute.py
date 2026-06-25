"""
属性计算器
实现《明日方舟》伤害计算.md 中定义的完整属性修饰器公式：

    A_f = F_t × [(A + D_p) × (1 + D_t) + F_p]

修饰器四种类型：
  - ADDITION      直接加算 (D_p)：基础数值直接相加
  - MULTIPLIER    直接乘算 (D_t)：对直接加算后的结果乘算（相加后整体 ×(1+D_t)）
  - FINAL_ADDITION 最终加算 (F_p)：对前两步结果再加算（鼓舞效果）
  - FINAL_SCALER  最终乘算 (F_t)：最低优先度，对所有步骤结果乘算（相乘）

注意：最终乘算各项之间互相相乘（不同于其余三种相加叠加）。
修正规则：当任意修饰器数值 < 0 时，自动补正为「原值 + 1」。
"""

from dataclasses import dataclass, field
from typing import List


# ── 计算环境基准（PRD §5.1）────────────────────────────────
STANDARD_DEF = 1000   # 标准物理防御
STANDARD_RES = 20     # 标准法术抗性（用户确认为 20）


@dataclass
class AttributeModifier:
    """单个属性修饰器"""
    modifier_type: str   # "ADDITION" | "MULTIPLIER" | "FINAL_ADDITION" | "FINAL_SCALER"
    value: float         # 修饰器数值（如 +200% 写作 2.0）
    source: str = ""     # 来源描述，方便调试（如"技能名称"、"天赋名称"）


class AttributeCalculator:
    """
    属性计算器
    收集所有修饰器后，按公式计算最终属性值。

    使用方式：
        calc = AttributeCalculator(base_value=876)
        calc.add_modifier("MULTIPLIER", 2.0, source="真银斩")
        calc.add_modifier("FINAL_SCALER", 0.3, source="银灰防御-70%补正后")
        result = calc.calculate()
    """

    def __init__(self, base_value: float):
        """
        Args:
            base_value: 原始属性值（精二满级 + 信赖已计入）
        """
        self.base_value = base_value
        self._modifiers: List[AttributeModifier] = []

    def add_modifier(self, modifier_type: str, value: float, source: str = "") -> None:
        """添加一个属性修饰器"""
        self._modifiers.append(AttributeModifier(modifier_type, value, source))

    def _apply_correction(self, value: float) -> float:
        """
        修正规则：当任意修饰器数值 < 0 时，补正为原值 + 1
        例：-70% 防御修饰 → -0.7 → 补正为 0.3（即 -0.7 + 1）
        """
        return value + 1.0 if value < 0 else value

    def calculate(self, attr_min: float = 0.0, attr_max: float = float("inf")) -> float:
        """
        按四修饰器公式计算最终属性值并应用属性上下限。

        Returns:
            最终属性值（浮点数）
        """
        A = self.base_value

        # 1. 直接加算：D_p = sum(p_i)
        D_p = sum(
            m.value for m in self._modifiers if m.modifier_type == "ADDITION"
        )

        # 2. 直接乘算：D_t = sum(t_i)（叠加相加，非相乘）
        D_t = sum(
            m.value for m in self._modifiers if m.modifier_type == "MULTIPLIER"
        )

        # 3. 最终加算：F_p = sum(p_i)
        F_p = sum(
            m.value for m in self._modifiers if m.modifier_type == "FINAL_ADDITION"
        )

        # 4. 最终乘算：F_t = t_1 × t_2 × ... × t_n（叠加相乘）
        #    各项在收集时如果 < 0 需要先补正
        final_scalers = [
            self._apply_correction(m.value)
            for m in self._modifiers
            if m.modifier_type == "FINAL_SCALER"
        ]
        F_t = 1.0
        for fs in final_scalers:
            F_t *= fs

        # 直接乘算的 (1 + D_t) 若 < 0 则补正为 0
        multiplier_factor = max(0.0, 1.0 + D_t)

        # 属性公式：A_f = F_t × [(A + D_p) × (1 + D_t) + F_p]
        A_f = F_t * ((A + D_p) * multiplier_factor + F_p)

        # 应用属性上下限
        A_f = max(attr_min, min(attr_max, A_f))

        return A_f

    def get_modifiers_summary(self) -> dict:
        """返回所有修饰器的汇总，方便调试和数据透明化展示"""
        return {
            "base_value": self.base_value,
            "ADDITION": [m.value for m in self._modifiers if m.modifier_type == "ADDITION"],
            "MULTIPLIER": [m.value for m in self._modifiers if m.modifier_type == "MULTIPLIER"],
            "FINAL_ADDITION": [m.value for m in self._modifiers if m.modifier_type == "FINAL_ADDITION"],
            "FINAL_SCALER": [m.value for m in self._modifiers if m.modifier_type == "FINAL_SCALER"],
        }


def build_atk_calculator(
    base_atk: float,
    params: "SkillParams",  # type: ignore[name-defined]  # 避免循环导入
) -> AttributeCalculator:
    """
    根据技能参数构建攻击力计算器（快捷函数）
    对应 damage_sample.json 中的四个 ATK 修饰器字段
    """
    calc = AttributeCalculator(base_value=base_atk)

    if params.ADDITION_ATK != 0:
        calc.add_modifier("ADDITION", params.ADDITION_ATK, source="ADDITION_ATK")
    if params.MULTIPLIER_ATK != 0:
        calc.add_modifier("MULTIPLIER", params.MULTIPLIER_ATK, source="MULTIPLIER_ATK")
    if params.FINAL_ADDITION_ATK != 0:
        calc.add_modifier("FINAL_ADDITION", params.FINAL_ADDITION_ATK, source="FINAL_ADDITION_ATK")
    # FINAL_SCALER_ATK 默认值 1.0 表示无修正，不需要额外添加
    if params.FINAL_SCALER_ATK != 1.0:
        calc.add_modifier("FINAL_SCALER", params.FINAL_SCALER_ATK, source="FINAL_SCALER_ATK")

    return calc
