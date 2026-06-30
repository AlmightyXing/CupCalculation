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
            
    if end_idx - start_idx > 1000:
        end_idx = start_idx + 1000
        
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

    skills_context = []
    for s in data["skills"]:
        skills_context.append({
            "skill_name": s.get("skill_name"),
            "description": s.get("description"),
            "current_duration": s.get("duration")
        })

    prompt = f"""干员名称: {name}
技能列表: {json.dumps(skills_context, ensure_ascii=False)}

以下是该干员的原始WIKI数据文本片段（包含技能的详细升级数据和技力回复类型）：
---
{raw_context}
---

任务说明：
由于之前数据解析的缺陷，部分没有持续时间的技能（如瞬发技能、弹药类技能、持续时间无限技能等）的 duration 被错误地填充了数字。
请你基于提供的“原始WIKI数据文本片段”以及“技能列表”中的描述，为每一个技能判断其真实的持续时间（专精三或最高等级时）：

规则：
1. **优先依据原始数据文本**：在原始数据中，技能数据通常会有“初始”、“消耗”、“持续”这三个字段名，随后跟着具体的数值。如果你在原文的最高等级数值区发现“持续”对应的数值为空白、不存在，或者为“-”，那么说明该技能没有持续时间，你必须返回 null。
2. **结合文本特征**：如果技能的 description 中包含“持续时间无限”、“装有x发弹药”、“打完后结束”等字眼，或者它是明显的瞬发单次/多次攻击（如“下次攻击”、“立即造成”、“发动2次斩击”等），则持续时间也没有意义，必须返回 null。
3. 否则，如果原始文本中明确给出了持续时间的秒数，请返回该秒数（整数）。

请严格返回一个 JSON 数组，顺序与给定的技能列表一致，格式示例（仅包含 duration 键，若是null请输出JSON的null）：
[
  {{"duration": null}},
  {{"duration": 15}},
  {{"duration": null}}
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
            skill["duration"] = enriched_data[i].get("duration")
            
        with lock:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
        return f"[OK] {name} - duration 修正完成"
    except Exception as e:
        return f"[ERROR] {name} - {str(e)}"

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "../data/parsed_data")
    files = glob.glob(os.path.join(data_dir, "*.json"))
    print(f"Found {len(files)} JSON files. Starting duration fix processing...")
    
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
