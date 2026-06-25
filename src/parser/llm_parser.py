"""
DeepSeek API 解析器
将技能文字描述 → 结构化 SkillParams JSON

工作流：
  1. 读取 character_sample.json 格式的干员原始数据
  2. 逐个技能调用 DeepSeek Chat API，输出 damage_sample.json 格式的 JSON
  3. 将解析结果填充到 SkillData.skill_params 中
"""

import json
import os
import time
from pathlib import Path
from openai import OpenAI  # DeepSeek 兼容 OpenAI SDK

from src.calculator.models import SkillParams, SkillData, CharacterData

# ── DeepSeek API 配置 ─────────────────────────────────────
# 请将 API Key 放在环境变量 DEEPSEEK_API_KEY 中，不要硬编码
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# ── 提示词模板 ────────────────────────────────────────────
SYSTEM_PROMPT = """你是《明日方舟》伤害计算专家。
你的任务是将技能描述解析为结构化 JSON，用于伤害计算。

### 字段说明（所有字段均必须输出，无影响时填默认值）：
- ADDITION_ATK (float): 攻击力直接加算（绝对值，如额外+100攻击力）默认0.0
- MULTIPLIER_ATK (float): 攻击力直接乘算（如"+200%攻击力"填2.0）默认0.0
- FINAL_ADDITION_ATK (float): 攻击力最终加算（鼓舞效果）默认0.0
- FINAL_SCALER_ATK (float): 攻击力最终乘算倍率（如"提升至260%"填2.6，"200%攻击力"填2.0）默认1.0
- hits (int): 单次攻击打击数（如"二连击"填2）默认1
- damage_type (str): 伤害类型，只能是 "physical"/"magic"/"element"/"true"/"heal"
- attck_speed_addition (int): 攻击速度加算（正数加速）默认0
- attack_time_reduction (float): 攻击间隔修正（"+0.3"表示延长0.3秒，填0.3；"-0.1"填-0.1）默认0.0
- defence_penetration (float): 物理穿透百分比 [0,1]（如"无视20%防御"填0.2）默认0.0
- defence_penetration_fixed (int): 物理穿透固定值（如"无视200防御"填200）默认0
- res_penetration (float): 法术穿透百分比 [0,1]默认0.0
- res_penetration_fixed (int): 法术穿透固定值默认0

### 注意事项：
- "攻击力提升至X%"：FINAL_SCALER_ATK = X/100
- "+X%攻击力"：MULTIPLIER_ATK = X/100（直接乘算）
- "攻击力×X"：FINAL_SCALER_ATK = X
- 技能含多种伤害类型时，只填主要伤害类型（物理/法术优先）

只输出 JSON，不要任何解释文字。"""

USER_PROMPT_TEMPLATE = """干员：{name}（{character_type}）
技能名：{skill_name}
技能描述：{description}
天赋参考（若对攻击力有影响）：{talents_text}

请输出此技能激活时的结构化伤害参数 JSON："""


def _build_client() -> OpenAI:
    """构建 DeepSeek 客户端（兼容 OpenAI SDK）"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "请设置环境变量 DEEPSEEK_API_KEY，例如：\n"
            "  $env:DEEPSEEK_API_KEY='your-api-key'  (PowerShell)\n"
            "  set DEEPSEEK_API_KEY=your-api-key     (CMD)"
        )
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def _parse_skill_with_llm(
    client: OpenAI,
    char: CharacterData,
    skill: SkillData,
) -> SkillParams:
    """
    调用 DeepSeek API 解析单个技能，返回 SkillParams。
    """
    talents_text = "\n".join(
        f"  - {t.talent_name}：{t.talent_decription}"
        for t in char.talents
    ) or "无"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=char.name,
        character_type=char.character_type,
        skill_name=skill.skill_name,
        description=skill.description,
        talents_text=talents_text,
    )

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,  # 确定性输出
    )

    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)

    # 将字典映射到 SkillParams dataclass（允许缺少字段，使用默认值）
    return SkillParams(
        ADDITION_ATK=float(data.get("ADDITION_ATK", 0.0)),
        MULTIPLIER_ATK=float(data.get("MULTIPLIER_ATK", 0.0)),
        FINAL_ADDITION_ATK=float(data.get("FINAL_ADDITION_ATK", 0.0)),
        FINAL_SCALER_ATK=float(data.get("FINAL_SCALER_ATK", 1.0)),
        hits=int(data.get("hits", 1)),
        damage_type=str(data.get("damage_type", "physical")),
        attck_speed_addition=int(data.get("attck_speed_addition", 0)),
        attack_time_reduction=float(data.get("attack_time_reduction", 0.0)),
        defence_penetration=float(data.get("defence_penetration", 0.0)),
        defence_penetration_fixed=int(data.get("defence_penetration_fixed", 0)),
        res_penetration=float(data.get("res_penetration", 0.0)),
        res_penetration_fixed=int(data.get("res_penetration_fixed", 0)),
    )


def parse_character_skills(
    char: CharacterData,
    output_dir: Path,
    rate_limit_delay: float = 1.0,
) -> CharacterData:
    """
    为干员的所有技能调用 LLM 解析，并将结果保存为 JSON 文件。

    已有缓存文件的技能将跳过 API 调用（避免重复计费）。

    Args:
        char:             干员数据
        output_dir:       解析结果 JSON 的输出目录（data/processed/）
        rate_limit_delay: API 调用间隔（秒），避免触发限速

    Returns:
        已填充 skill_params 的 CharacterData
    """
    client = _build_client()
    output_dir.mkdir(parents=True, exist_ok=True)

    for skill in char.skills:
        cache_file = output_dir / f"{char.character_id}_skill{skill.skill_id}.json"

        # 命中缓存：直接读取，跳过 API 调用
        if cache_file.exists():
            print(f"  [缓存] {char.name} 技能{skill.skill_id}：{skill.skill_name}")
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            skill.skill_params = SkillParams(**cached)
            continue

        print(f"  [解析] {char.name} 技能{skill.skill_id}：{skill.skill_name} ...")
        try:
            params = _parse_skill_with_llm(client, char, skill)
            skill.skill_params = params

            # 保存缓存
            cache_data = {
                "ADDITION_ATK": params.ADDITION_ATK,
                "MULTIPLIER_ATK": params.MULTIPLIER_ATK,
                "FINAL_ADDITION_ATK": params.FINAL_ADDITION_ATK,
                "FINAL_SCALER_ATK": params.FINAL_SCALER_ATK,
                "hits": params.hits,
                "damage_type": params.damage_type,
                "attck_speed_addition": params.attck_speed_addition,
                "attack_time_reduction": params.attack_time_reduction,
                "defence_penetration": params.defence_penetration,
                "defence_penetration_fixed": params.defence_penetration_fixed,
                "res_penetration": params.res_penetration,
                "res_penetration_fixed": params.res_penetration_fixed,
            }
            cache_file.write_text(
                json.dumps(cache_data, ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
            print(f"    ✓ 已保存缓存到 {cache_file.name}")

        except Exception as e:
            print(f"    ✗ 解析失败：{e}")

        time.sleep(rate_limit_delay)

    return char
