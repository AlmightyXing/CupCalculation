"""
干员与技能数据模型定义
对应 character_sample.json 和 damage_sample.json 的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TalentData:
    """天赋数据"""
    talent_id: int
    talent_name: str
    talent_decription: str  # 注意：保持与 JSON 中的拼写一致


@dataclass
class SkillData:
    """
    技能原始描述数据（来自 character_sample.json）
    由 LLM 解析器填充 skill_params 字段
    """
    skill_id: int
    skill_name: str
    # "auto"（挂机/自动）或 "manual"（决战/手动）
    skill_type: str
    # 技能持续时间（秒），挂机技能可为 None
    duration: Optional[float]
    description: str
    # LLM 解析后填充的结构化参数
    skill_params: Optional["SkillParams"] = None


@dataclass
class SkillParams:
    """
    技能结构化参数（对应 damage_sample.json）
    由 LLM 解析器从技能文字描述中提取
    """
    # ── 攻击力修饰器 ──────────────────────────────────
    # 直接加算：基础攻击力 + 此值
    ADDITION_ATK: float = 0.0
    # 直接乘算：(基础 + ADDITION) × (1 + 此值)
    MULTIPLIER_ATK: float = 0.0
    # 最终加算：前两步结果 + 此值（鼓舞效果）
    FINAL_ADDITION_ATK: float = 0.0
    # 最终乘算：所有步骤结果 × 此值（初始值 1.0 表示无修正）
    # 注意：PRD §5.4 示例"攻击力提升至 260%"对应 FINAL_SCALER_ATK = 2.6
    # 真银斩"+200%"是直接乘算，对应 MULTIPLIER_ATK = 2.0（最终攻击力 = 原ATK × (1+2.0) = 3.0×ATK）
    FINAL_SCALER_ATK: float = 1.0

    # ── 攻击次数 ──────────────────────────────────────
    # 单次攻击动作的打击数（如二连击为 2）
    hits: int = 1

    # ── 伤害类型 ──────────────────────────────────────
    # "physical" | "magic" | "element" | "true" | "heal"
    damage_type: str = "physical"

    # ── 攻速修饰 ──────────────────────────────────────
    # 攻击速度加算（直接相加到基础攻速100）
    attck_speed_addition: int = 0
    # 攻击间隔减少值（秒，正数表示延长，负数表示缩短）
    attack_time_reduction: float = 0.0

    # ── 穿透参数 ──────────────────────────────────────
    # 物理穿透（百分比），取值范围 [0, 1]
    defence_penetration: float = 0.0
    # 物理穿透（固定值）
    defence_penetration_fixed: int = 0
    # 法术穿透（百分比），取值范围 [0, 1]
    res_penetration: float = 0.0
    # 法术穿透（固定值）
    res_penetration_fixed: int = 0


@dataclass
class CharacterData:
    """
    干员完整数据模型（对应 character_sample.json）
    精二满级、0潜能、满级模组的最终数值
    """
    character_id: str
    name: str
    nickname: List[str]

    # 基础属性（精二满级 + 信赖值，即实际可用攻击力）
    base_atk: int          # 攻击力（已含信赖）
    base_hp: int           # 最大生命值（已含信赖）
    base_def: int          # 防御力（已含信赖）
    base_res: int          # 法术抗性（已含信赖）
    atk_time: float        # 基础攻击间隔（秒）

    # 信赖加成（单独保留，方便日后扩展"0信赖"计算模式）
    confidence_atk: int = 0
    confidence_hp: int = 0
    confidence_def: int = 0
    confidence_res: int = 0

    # 默认攻击速度（无技能加成时）
    attack_speed: int = 100

    # 天赋与技能列表
    talents: List[TalentData] = field(default_factory=list)
    skills: List[SkillData] = field(default_factory=list)

    # 角色描述（可选，供 LLM 解析时参考）
    character_type: str = ""
    character_description: str = ""


@dataclass
class CalculationResult:
    """单个技能的计算结果，对应 PRD §5.5 数据字段"""
    character_id: str
    character_name: str
    skill_id: int
    skill_name: str
    skill_type: str          # "auto" | "manual"

    # 挂机榜：DPS / HPS
    auto_dps: Optional[float] = None
    auto_hps: Optional[float] = None

    # 决战榜：DPS、HPS、总伤、总治疗
    manual_dps: Optional[float] = None
    manual_hps: Optional[float] = None
    manual_damage_total: Optional[float] = None
    manual_heal_total: Optional[float] = None


@dataclass
class RankedOperator:
    """
    排名后的干员综合数据（最终输出到数据库的结构）
    对应 PRD §5.5 完整字段，含杯级评定结果
    """
    character_id: str
    name: str
    nickname: List[str]
    cup_level: str           # "超大杯·上" | "超大杯·中" | "超大杯·下" | "大杯" | "中杯"
    rank: int                # 综合总排名

    auto_dps: Optional[int] = None
    auto_dps_rank: Optional[int] = None
    auto_hps: Optional[int] = None
    auto_hps_rank: Optional[int] = None

    manual_dps: Optional[int] = None
    manual_dps_rank: Optional[int] = None
    manual_hps: Optional[int] = None
    manual_hps_rank: Optional[int] = None

    manual_damage_total: Optional[int] = None
    manual_damage_total_rank: Optional[int] = None
    manual_heal_total: Optional[int] = None
    manual_heal_total_rank: Optional[int] = None
