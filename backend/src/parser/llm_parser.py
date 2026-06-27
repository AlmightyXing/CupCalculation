"""
DeepSeek API 解析器
将技能文字描述 → 结构化 SkillParams JSON

工作流：
  1. 读取 character_sample.json 格式的干员原始数据
  2. 分别为干员的 特性、天赋、技能 调用 DeepSeek Chat API
  3. 将解析结果进行数学合并，填充到 SkillData.skill_params 中
"""

import json
import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

from src.calculator.models import SkillParams, SkillData, CharacterData, TalentData

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

SYSTEM_PROMPT = """你是《明日方舟》伤害计算专家。
你的任务是将文字描述解析为结构化 JSON，用于伤害计算。

### 字段说明（所有字段均必须输出，无影响时填默认值）：
- ADDITION_ATK (float): 攻击力直接加算（绝对值，如额外+100攻击力）默认0.0
- MULTIPLIER_ATK (float): 攻击力直接乘算（如"+200%攻击力"填2.0，"+10%"填0.1，"+15%"填0.15）默认0.0
- FINAL_ADDITION_ATK (float): 攻击力最终加算（鼓舞效果）默认0.0
- FINAL_SCALER_ATK (float): 攻击力最终乘算倍率（如"提升至120%"填1.2，"降低至80%"填0.8）默认1.0
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
- 若含多种伤害类型，只填主要伤害类型（物理/法术优先）

只输出 JSON，不要任何解释文字。"""

TRAIT_PROMPT_TEMPLATE = """干员：{name}（{character_type}）
特性描述：{character_description}

请分析上述特性，输出该特性带来的常驻结构化伤害参数 JSON："""

TALENT_PROMPT_TEMPLATE = """干员：{name}（{character_type}）
天赋名：{talent_name}
天赋描述：{talent_description}

请分析上述天赋，输出该天赋在理想条件（如攻击敌人、周围存在多个敌人等最佳条件）下触发时，带来的常驻结构化伤害参数 JSON："""

SKILL_PROMPT_TEMPLATE = """干员：{name}（{character_type}）
技能名：{skill_name}
技能描述：{description}

请分析上述技能，输出该技能激活时带来的额外结构化伤害参数 JSON（此 Json 仅包含技能本身的修饰，不需要包含特性与天赋的修饰，它们会在其他地方被处理）："""


def _build_client() -> OpenAI:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "请设置环境变量 DEEPSEEK_API_KEY，例如：\n"
            "  $env:DEEPSEEK_API_KEY='your-api-key'\n"
        )
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def _call_llm_for_params(client: OpenAI, user_prompt: str) -> SkillParams:
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)

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


def _merge_params(*params_list: SkillParams) -> SkillParams:
    merged = SkillParams()
    for p in params_list:
        if not p:
            continue
        merged.ADDITION_ATK += p.ADDITION_ATK
        merged.MULTIPLIER_ATK += p.MULTIPLIER_ATK
        merged.FINAL_ADDITION_ATK += p.FINAL_ADDITION_ATK
        merged.FINAL_SCALER_ATK *= p.FINAL_SCALER_ATK
        
        if p.hits > merged.hits:
            merged.hits = p.hits
            
        if p.damage_type != "physical" and merged.damage_type == "physical":
            merged.damage_type = p.damage_type
            
        merged.attck_speed_addition += p.attck_speed_addition
        merged.attack_time_reduction += p.attack_time_reduction
        
        merged.defence_penetration += p.defence_penetration
        merged.defence_penetration_fixed += p.defence_penetration_fixed
        merged.res_penetration += p.res_penetration
        merged.res_penetration_fixed += p.res_penetration_fixed
        
    return merged


def _get_or_fetch(client: OpenAI, cache_file: Path, user_prompt: str, rate_limit_delay: float = 1.0) -> SkillParams:
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            return SkillParams(**cached)
        except Exception:
            pass

    params = _call_llm_for_params(client, user_prompt)
    
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
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=4), encoding="utf-8")
    time.sleep(rate_limit_delay)
    return params


def parse_character_skills(char: CharacterData, output_dir: Path, rate_limit_delay: float = 1.0) -> CharacterData:
    client = _build_client()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 解析特性
    trait_params = SkillParams()
    if char.character_description:
        prompt = TRAIT_PROMPT_TEMPLATE.format(
            name=char.name, 
            character_type=char.character_type, 
            character_description=char.character_description
        )
        cache_file = output_dir / f"{char.character_id}_trait.json"
        print(f"  [解析特性] {char.name} ...")
        trait_params = _get_or_fetch(client, cache_file, prompt, rate_limit_delay)
        
    # 2. 解析天赋
    talent_params_list = []
    for i, t in enumerate(char.talents):
        if not t.talent_decription:
            continue
        prompt = TALENT_PROMPT_TEMPLATE.format(
            name=char.name, 
            character_type=char.character_type, 
            talent_name=t.talent_name, 
            talent_description=t.talent_decription
        )
        cache_file = output_dir / f"{char.character_id}_talent{i}.json"
        print(f"  [解析天赋] {char.name} - {t.talent_name} ...")
        talent_params_list.append(_get_or_fetch(client, cache_file, prompt, rate_limit_delay))
        
    # 3. 解析技能并合并
    for skill in char.skills:
        prompt = SKILL_PROMPT_TEMPLATE.format(
            name=char.name, 
            character_type=char.character_type, 
            skill_name=skill.skill_name, 
            description=skill.description
        )
        cache_file = output_dir / f"{char.character_id}_skill{skill.skill_id}.json"
        print(f"  [解析技能] {char.name} - {skill.skill_name} ...")
        skill_only_params = _get_or_fetch(client, cache_file, prompt, rate_limit_delay)
        
        merged = _merge_params(trait_params, *talent_params_list, skill_only_params)
        skill.skill_params = merged

    return char
