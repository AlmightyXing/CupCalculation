import os, glob, json, re, time
from pathlib import Path
from dotenv import load_dotenv
from google import genai

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
env_path = PROJECT_ROOT / "backend" / ".env"
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

parsed_dir = 'data/parsed_data'
op_dir = 'backend/function/logic/operators'

zh_to_en = {
    "重剑手": "Crusher", "无畏者": "Dreadnought", "钩索师": "Hookmaster", "领主": "Lord",
    "武者": "Fighter", "医师": "Physician", "投掷手": "Flinger", "炮手": "Artilleryman",
    "情报官": "IntelligenceOfficer", "哨戒铁卫": "SentinelDefender", "斗士": "Brawler",
    "中坚术师": "CoreCaster", "吟游者": "Bard", "傀儡师": "Dollkeeper", "巫役": "IncantationMedic",
    "塑灵术师": "Ritualist", "咒愈师": "CurseHealer", "扩散术师": "SplashCaster",
    "群愈师": "RingHealer", "尖兵": "Pioneer", "伏击客": "Ambusher", "护佑者": "Abjurer",
    "炼金师": "Alchemist", "剑豪": "Swordmaster", "疗养师": "Therapist", "削弱者": "Hexer",
    "策士": "Strategist", "阵法术师": "PhalanxCaster", "解放者": "Liberator", "守护者": "Guardian",
    "神射手": "Deadeye", "铁卫": "Protector", "行商": "Merchant", "怪杰": "Geek",
    "驭法铁卫": "ArtsProtector", "秘术师": "MysticCaster", "行医": "WanderingMedic",
    "术战者": "ArtsFighter", "速射手": "Marksman", "收割者": "Reaper", "处决者": "Executor",
    "重射手": "HeavyShooter", "教官": "Instructor", "召唤师": "Summoner", "本源铁卫": "PrimalProtector",
    "陷阱师": "Trapmaster", "守望者": "Watcher", "战术家": "Tactician", "散射手": "Spreadshooter",
    "推击手": "Pusher", "不屈者": "Juggernaut", "凝滞师": "DecelBinder", "本源术师": "PrimalCaster",
    "猎手": "Hunter", "强攻手": "Centurion", "轰击术师": "BlastCaster", "工匠": "Artificer",
    "冲锋手": "Charger", "决战者": "Duelist", "链术师": "ChainCaster", "撼地者": "Earthshaker",
    "回环射手": "Loopshooter", "攻城手": "Besieger", "驭械术师": "MechAccordCaster",
    "执旗手": "StandardBearer", "要塞": "Fortress"
}

critical_classes = {
    "Swordmaster", "Flinger", "Hunter", "Instructor", "PhalanxCaster", "Liberator", 
    "MechAccordCaster", "Spreadshooter", "Tactician"
}

with open('backend/function/logic/professions.py', 'r', encoding='utf-8') as f:
    professions_code = f.read()

REFACTOR_SYSTEM_PROMPT = """你是一个专门负责代码重构的高级 Python 专家。
当前项目是一个《明日方舟》干员 DPS 模拟器。
输入分为两部分：
1. 最新的父类定义 (`professions.py` 的截取片段)
2. 目前的干员文件代码。

【你的任务】：
干员文件代码最初生成时，父类的定义不完整，因此干员文件可能犯了以下错误：
1. 错误地继承了基类（比如把重剑手继承为了 Liberator，需要更正为对应的类名）。
2. 覆写了 `calculate_normal_hit` 或 `calculate_skill_damage`，但在覆写时忘记了加上父类特性的效果。
   例如，剑豪的普攻两连击需要在单次伤害的基础上 * 2，投掷手需要计算一次 100% 和一次 50% 物理伤害之和。如果干员自己覆写了普攻逻辑（如艾丽妮有无视防御），必须确保父类的 2 连击系数被乘进去！如果父类有特殊的倍率（如散射手 1.5），也必须体现！
3. 如果干员仅仅是 import 错误，你也需要修复 import。

【规则】：
请修复代码，你可以将父类里乘的系数或逻辑在干员代码中硬编码体现出来，或者使用 super()。保证最终 calculate_dps 或 calculate_skill_damage 的伤害和攻速是准确符合子职业设定的。
输出只能包含重构后的完整 Python 代码（包含 imports），不要任何 markdown 标记（如 ```python）。不要省略任何已有方法。
"""

def generate_gemini_response(prompt: str) -> str:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "system_instruction": REFACTOR_SYSTEM_PROMPT,
            "temperature": 0.1
        }
    )
    return response.text

def refactor_all():
    print("开始进行干员代码审查与批量重构...")
    count_refactored = 0
    for py_file in glob.glob(os.path.join(op_dir, '*.py')):
        base_name = os.path.basename(py_file).replace('.py', '').upper()
        json_path = os.path.join(parsed_dir, f'{base_name}.json')
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        char_type = data.get('character', {}).get('character_type', '')
        correct_en_name = zh_to_en.get(char_type, "UnknownProfession")
        
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        needs_llm_refactor = False
        
        match = re.search(r'class \w+\((\w+)\):', content)
        current_base = match.group(1) if match else None
        
        if current_base != correct_en_name:
            needs_llm_refactor = True
            
        if correct_en_name in critical_classes:
            if "def calculate_normal_hit" in content and "super().calculate_normal_hit" not in content:
                needs_llm_refactor = True
                
        if needs_llm_refactor:
            print(f"[{base_name}] 正在重构! 当前基类: {current_base}, 正确基类: {correct_en_name}")
            prompt = f"最新父类参考：\n{professions_code}\n\n当前干员代码：\n{content}\n\n该干员应继承的正确类为：{correct_en_name}。请确保 import 也被修正。"
            try:
                new_code = generate_gemini_response(prompt)
                
                new_code = new_code.strip()
                if new_code.startswith("```python"):
                    new_code = new_code[9:]
                elif new_code.startswith("```"):
                    new_code = new_code[3:]
                if new_code.endswith("```"):
                    new_code = new_code[:-3]
                    
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_code.strip() + "\n")
                
                print(f"  -> 重构完成并覆盖。")
                count_refactored += 1
                time.sleep(2)
            except Exception as e:
                print(f"  -> 重构失败: {e}")
                
    print(f"审查结束，共重构了 {count_refactored} 份干员代码。")

if __name__ == "__main__":
    refactor_all()
