"""
利用大模型 (DeepSeek) 将抓取到的 PRTS 文本转化为结构化 JSON 数据
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)  # 强制使用 .env 文件中的值覆盖当前环境

# ── DeepSeek API 配置 ─────────────────────────────────────
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

SYSTEM_PROMPT = """你是一个精通《明日方舟》数据处理的AI。你的任务是将抓取到的网页原始文本转换为结构化的 JSON 数据。
请提取以下内容，并严格按照指定 JSON 格式输出：
- character_id: 干员ID (根据英文名推测，如 char_325_mlynar)。
- name: 干员名称。
- nickname: 昵称列表(留空列表即可)。
- character: 包含 character_type (如"解放者", "术师"等分支) 和 character_description (特性描述)。
- base_hp, base_atk, base_def, base_res: 精二满级(90级)无信赖的基础面板。
- atk_time: 基础攻击间隔（秒）。
- confidence_hp, confidence_atk, confidence_def, confidence_res: 满信赖(200%)时提供的属性加成。如果没有加成，填0。
- talents: 列表，含 talent_id (从0开始), talent_name (天赋名), talent_decription (天赋描述)。需要是最终精二潜能0时的天赋效果。
- skills: 列表，包含 skill_id (从0开始), skill_name (技能名), skill_type ("auto"或者"manual", 拥有永续特性或被动触发填auto, 否则填manual), duration (持续时间秒，永续/被动填 null), description (技能专精三的描述文本)。

注意：所有面板数据（hp/atk/def/res）要求提取**精二满级(90级)且不含信赖**的基础数值。信赖加成单独放在 confidence_* 字段。
如果原文没有提到某些字段（比如无该信赖加成），请使用 0 补全。
只输出合法的 JSON，不要输出 Markdown 标记或任何其他解释文本。"""

USER_PROMPT_TEMPLATE = """这是从 PRTS Wiki 上抓取到的【{operator_name}】的相关网页文本，其中混杂了页面各种信息。
请从中提取出精二满级、满信赖、专精三的干员数据，并按照约定的 JSON 结构输出。

【网页文本开始】
{text}
【网页文本结束】

请生成 JSON："""

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

def clean_operator_text_to_json(operator_name: str, raw_text: str) -> dict:
    """
    调用大模型，清洗干员文本为 JSON 对象
    """
    client = _build_client()
    user_prompt = USER_PROMPT_TEMPLATE.format(operator_name=operator_name, text=raw_text)
    
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
    try:
        data = json.loads(raw_json)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"大模型返回的不是有效的 JSON 格式: {e}\n原文: {raw_json}")
