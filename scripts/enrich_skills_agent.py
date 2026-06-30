import os
import json
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI
from threading import Lock

# Load environment variables
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

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return f"[ERROR] {file_path} - JSON decode error"

    if "skills" not in data or not data["skills"]:
        return f"[SKIP] {data.get('name', 'Unknown')} - No skills"

    # Check if we need to process
    needs_update = False
    for skill in data["skills"]:
        if "start_sp" not in skill:
            needs_update = True
            break
            
    if not needs_update:
        return f"[SKIP] {data.get('name')} - Skills already enriched"
        
    skills_context = []
    for skill in data["skills"]:
        skills_context.append({
            "skill_name": skill.get("skill_name"),
            "description": skill.get("description")
        })

    prompt = f"""干员名称: {data.get('name')}
技能列表: {json.dumps(skills_context, ensure_ascii=False)}

请为上述每个技能补充专精三（RANK III）状态下的四个字段：
- start_sp: 初始技力 (整数，若无填0，如果是被动技能也填0)
- consume_sp: 技力消耗 (整数，若无/被动技能填0)
- attack_supplement: 是否受击/攻击回复技力 (布尔值)
- auto_supplement: 是否自动回复技力 (布尔值)

请严格返回一个 JSON 数组，顺序与技能列表一致，格式示例：
[
  {{"start_sp": 0, "consume_sp": 35, "attack_supplement": false, "auto_supplement": true}}
]
必须只返回合法的JSON数组，不要包含任何额外的解释说明文字（不要使用markdown的```json包裹）。
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个精确的数据提取API，只返回合法的JSON数组。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        reply = response.choices[0].message.content.strip()
        # Remove potential markdown wrappers if the model ignores the instruction
        if reply.startswith("```json"):
            reply = reply[7:]
        if reply.startswith("```"):
            reply = reply[3:]
        if reply.endswith("```"):
            reply = reply[:-3]
        reply = reply.strip()
        
        enriched_data = json.loads(reply)
        
        if len(enriched_data) != len(data["skills"]):
            return f"[ERROR] {data.get('name')} - Length mismatch in response"

        # Update data
        for i, skill in enumerate(data["skills"]):
            skill["start_sp"] = enriched_data[i].get("start_sp", 0)
            skill["consume_sp"] = enriched_data[i].get("consume_sp", 0)
            skill["attack_supplement"] = enriched_data[i].get("attack_supplement", False)
            skill["auto_supplement"] = enriched_data[i].get("auto_supplement", True)
            
        with lock:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
        return f"[OK] {data.get('name')} - 技能解析并更新完成"
    except Exception as e:
        return f"[ERROR] {data.get('name')} - {str(e)}"

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "../data/parsed_data")
    files = glob.glob(os.path.join(data_dir, "*.json"))
    print(f"Found {len(files)} JSON files. Starting processing...")
    
    success = 0
    skipped = 0
    failed = 0
    
    # We use a max_workers of 5 to avoid triggering rate limits heavily
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
    print(f"Summary: {success} Updated, {skipped} Skipped, {failed} Failed.")

if __name__ == "__main__":
    main()
