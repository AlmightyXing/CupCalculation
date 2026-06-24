import ollama
import json
import os

# You mentioned using Ollama for deepseek-r1.
# Usually, the model name in Ollama for 14B might be `deepseek-r1:14b`
MODEL_NAME = "gemma4:e4b" 

def extract_operator_data(raw_text, operator_name):
    """
    Sends the raw text to DeepSeek-R1 via Ollama to extract structured JSON data.
    """
    system_prompt = """
    你是一个针对《明日方舟》数据的提取工具。
    你需要从给定的维基文本中提取出该干员在“精二满级、满信赖、零潜能、满级模组”状态下的基础面板、技能数据、天赋等信息。
    在处理数据时，请注意：
    1. 当描述中提到“攻击力提升至”或者“攻击力提升”加一个百分比数值时，该信息应被记录入atk_change中。
    2. 当描述中提到“造成相当于X%攻击力的伤害”时，该数值应被记录入multiplier中。
    3. 若技能描述中提到“自动触发”、“自动释放”或“持续时间无限”，则该技能应被归类为“挂机”技能，否则被归类为“决战”技能。
    4. 若技能描述中同时提到多种类型的伤害，则提及的所有伤害类型都应该被记录，用列表的形式存储。
    5. 角色的hp、atk、def、res属性均应计算精英2满级与信赖加成上限叠加后的结果。
    6. 只有当描述中提到“无视目标x点防御力/法术抗性”或“使目标防御力/法术抗性降低x点”时，x应被记录入fixed_armor_penetration或fixed_resistance_reduction中。
    7. 只有当描述中提到“无视目标x%的防御力/法术抗性”或“使目标防御力/法术抗性降低x%”时，x应被记录入percentage_armor_penetration或percentage_resistance_reduction中。
    8. 当描述中提到“造成伤害提升x%”时，将1+x%计入increase中；当描述中提到“造成伤害提升至X”时，将X计入increase中。
    请严格按照以下 JSON 格式输出，不要输出任何额外的解释和文字，只能输出合法的 JSON 字符串：
    {
        "name": "干员名称",
        "stats": {
            "hp": 0,
            "atk": 0,
            "def": 0,
            "res": 0,
            "atk_interval": 1.0
        },

        "features":{
            "name":"职业名",
            "description":"职业特性描述",
            "parsed_effects": {
                "atk_change":0.0,
                "multiplier":1.0,
                "increase": 1.0,
                "atk_interval_change": 0.0,
                "percentage_armor_penetration":0.0,
                "fixed_armor_penetration":0.0,
                "percentage_resistance_reduction":0.0,
                "fixed_resistance_reduction":0.0
                }
        },

        "talents": {
            "talent1":{
                "name":"天赋1名称",
                "description":"天赋1描述",
                "parsed_effects": {
                    "atk_change":0.0,
                    "multiplier":1.0,
                    "atk_interval_change": 0.0,
                    "percentage_armor_penetration":0.0,
                    "fixed_armor_penetration":0.0,
                    "percentage_resistance_reduction":0.0,
                    "fixed_resistance_reduction":0.0
                }
            },
            "talent2":{
                "name":"天赋2名称",
                "description":"天赋2描述",
                "parsed_effects": {
                    "atk_change":0.0,
                    "multiplier":1.0,
                    "atk_interval_change": 0.0,
                    "percentage_armor_penetration":0.0,
                    "fixed_armor_penetration":0.0,
                    "percentage_resistance_reduction":0.0,
                    "fixed_resistance_reduction":0.0
                }
            }
        },

        "skills": [
            {
                "name": "技能名称",
                "skill_type": "决战",
                "initial_sp": 0,               
                "sp_cost": 0,
                "duration": 0,
                "description": "技能详细描述",
                "damage":[
                    {
                        "type":"物理",
                        "atk_change":0.0,
                        "multiplier":1.0
                    }
                ],
                "parsed_effects": {
                    "hits": 1,
                    "atk_interval_change": 0.0,
                    "percentage_armor_penetration":0.0,
                    "fixed_armor_penetration":0.0,
                    "percentage_resistance_reduction":0.0,
                    "fixed_resistance_reduction":0.0
                }
            }
        ],
    }
    如果某些数据无法找到，请填入 null 或 0。
    """
    
    prompt = f"请提取以下关于干员 {operator_name} 的数据：\n\n{raw_text[:8000]}"
    
    try:
        print(f"Sending prompt to {MODEL_NAME} for {operator_name}...")
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        # Extract the JSON part from response
        # Deepseek-r1 might output <think> tags. We should strip them.
        content = response['message']['content']
        
        # Simple cleanup if there are think tags
        if '</think>' in content:
            content = content.split('</think>')[-1].strip()
            
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
            
        content = content.strip()
        
        parsed_json = json.loads(content)
        return parsed_json
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        return None

if __name__ == "__main__":
    # Test with the previously scraped text
    if os.path.exists("test_operator.json"):
        with open("test_operator.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        result = extract_operator_data(data["raw_text"], data["name"])
        print("Finish Thinking! Result has been saved in files.")
        # print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result:
            with open(f"extracted_{data['name']}.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print("test_operator.json not found. Run prts_scraper.py first.")
