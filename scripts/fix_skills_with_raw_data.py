import os
import json
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI
from threading import Lock

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    print("Error: DEEPSEEK_API_KEY not found in backend/.env")
    exit(1)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)
lock = Lock()

def get_raw_context(name):
    raw_path = os.path.join(os.path.dirname(__file__), f"../data/raw_data/{name}_raw.txt")
    if not os.path.exists(raw_path):
        # Try finding by wildcard if name is different
        search = glob.glob(os.path.join(os.path.dirname(__file__), f"../data/raw_data/*{name}*_raw.txt"))
        if not search:
            return None
        raw_path = search[0]
        
    try:
        with open(raw_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        with open(raw_path, 'r', encoding='gbk') as f:
            lines = f.readlines()
            
    # Find the skill section to save tokens
    start_idx = 0
    end_idx = len(lines)
    for i, line in enumerate(lines):
        if "技能1" in line or "技能（精英0开放" in line or "技能（精英1开放" in line:
            start_idx = max(0, i - 10)
            break
            
    for i in range(start_idx, len(lines)):
        if "后勤技能" in line or "潜能提升" in line or "精英化材料" in line:
            end_idx = min(len(lines), i + 20)
            break
            
    # If we couldn't narrow it down well, just return a bigger chunk
    if end_idx - start_idx > 800:
        end_idx = start_idx + 800
        
    return "".join(lines[start_idx:end_idx])

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return f"[ERROR] {file_path} - JSON decode error"

    if "skills" not in data or not data["skills"]:
        return f"[SKIP] {data.get('name', 'Unknown')} - No skills"

    name = data.get("name")
    raw_context = get_raw_context(name)
    if not raw_context:
        return f"[ERROR] {name} - Raw data not found"

    skill_names = [s.get("skill_name") for s in data["skills"]]

    prompt = f"""干员名称: {name}
目标技能列表: {json.dumps(skill_names, ensure_ascii=False)}

以下是该干员的原始WIKI数据文本片段（包含技能的详细升级数据和技力回复类型）：
---
{raw_context}
---

任务说明：
上面是一段爬虫抓取到的网页文本，里面穿插着各个技能的数据（比如“自动回复”、“受击回复”、“攻击回复”、“手动触发”、“自动触发”等）。
对于每个技能，紧跟在“描述”下方通常有类似：
初始技力
技力消耗
持续时间
等数值，越往下则是等级越高的数值（例如专精一、专精二、专精三）。

请你在上述文本中进行阅读理解，为“目标技能列表”中的每一个技能，提取其在最高等级（专精三，若无则取7级）时的四个核心属性：
1. start_sp: 初始技力 (整数，若无/被动填0)
2. consume_sp: 技力消耗 (整数，若无/被动填0)
3. attack_supplement: 技力回复方式是否为“受击回复”或“攻击回复” (布尔值)
4. auto_supplement: 技力回复方式是否为“自动回复” (布尔值)

如果确认为被动技能，consume_sp为0。
必须严格返回一个 JSON 数组，顺序与给定的目标技能列表一致，格式示例：
[
  {{"start_sp": 10, "consume_sp": 35, "attack_supplement": false, "auto_supplement": true}}
]
必须只返回合法的JSON数组，不要包含任何额外的解释说明文字（不要使用markdown的```json包裹）。
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个严谨的数据提取API，擅长从非结构化文本中提取数值。只输出JSON数组。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        reply = response.choices[0].message.content.strip()
        if reply.startswith("```json"):
            reply = reply[7:]
        if reply.startswith("```"):
            reply = reply[3:]
        if reply.endswith("```"):
            reply = reply[:-3]
        reply = reply.strip()
        
        enriched_data = json.loads(reply)
        
        if len(enriched_data) != len(data["skills"]):
            return f"[ERROR] {name} - Length mismatch in response (expected {len(data['skills'])}, got {len(enriched_data)})"

        for i, skill in enumerate(data["skills"]):
            skill["start_sp"] = enriched_data[i].get("start_sp", 0)
            skill["consume_sp"] = enriched_data[i].get("consume_sp", 0)
            skill["attack_supplement"] = enriched_data[i].get("attack_supplement", False)
            skill["auto_supplement"] = enriched_data[i].get("auto_supplement", True)
            
        with lock:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
        return f"[OK] {name} - 基于 raw_data 修正完成"
    except Exception as e:
        return f"[ERROR] {name} - {str(e)}"

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "../data/parsed_data")
    files = glob.glob(os.path.join(data_dir, "*.json"))
    print(f"Found {len(files)} JSON files. Starting raw_data fix processing...")
    
    success = 0
    skipped = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {executor.submit(process_file, f): f for f in files}
        
        for future in as_completed(future_to_file):
            result = future.result()
            print(result)
            if result.startswith("[OK]"):
                success += 1
            elif result.startswith("[SKIP]"):
                skipped += 1
            else:
                failed += 1
                
    print("-" * 30)
    print(f"Summary: {success} Fixed, {skipped} Skipped, {failed} Failed.")

if __name__ == "__main__":
    main()
