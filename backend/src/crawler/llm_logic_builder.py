"""
使用 Gemini (google-genai) 自动补全干员的 Python 逻辑骨架
"""

import os
import json
import re
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 使用新版 SDK
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

env_path = PROJECT_ROOT / "backend" / ".env"
load_dotenv(dotenv_path=env_path, override=True)
PARSED_DIR = PROJECT_ROOT / "data" / "parsed_data"
LOGIC_DIR = PROJECT_ROOT / "backend" / "function" / "logic"
OPERATORS_DIR = LOGIC_DIR / "operators"

SYSTEM_PROMPT = """你是一个精通 Python 并且非常熟悉《明日方舟》伤害计算规则的高级游戏算法工程师。
你的任务是补全一个干员的 Python 业务逻辑代码骨架。

【上下文与核心规则】
1. 所有干员继承自 `Operator` 及其子类。干员有一个属性 `self.final_base_atk` 用于保存受信赖等影响后的最终基础攻击力（必须在 __init__ 中定义，由 base_atk + trust_atk 得来，你需要在 __init__ 中添加这一步，并调用 self.apply_talents()）。
2. 在 `apply_talents(self)` 中，根据 JSON 编写数值修改逻辑：
   - 只要天赋对提高伤害有帮助，**均纳入考虑**！
   - 如果天赋是**可叠加层数**的（如击杀叠攻击），必须直接按**最大层数**叠加到属性中。
3. `calculate_normal_hit(self, enemy, target_count=1) -> float`：
   - 计算单次普攻命中时的期望伤害。如果需要特殊的伤害类型计算，引入：`from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage`。
   - **注意**：无论技能或职业怎么描述群体攻击、对多名/两名敌人造成伤害，**严禁在代码中乘以任何目标数（如 `* 2` 或 `* 3`）**。最终的 `total_damage` 和 `dps` 必须严格是对**单个目标**造成的伤害！
4. `calculate_skill_damage(self, enemy, skill_index: int, target_count=1) -> dict`：
   - 必须返回字典格式：`{"total_damage": 总伤, "dps": 技能期间DPS}`
   - 使用 `actual_atk_interval = self.attack_interval * 100 / self.attack_speed` 获取实际攻击间隔。
   - **状态加成与瞬发伤害的顺序**：如果技能既有“攻击力+X%”的增益，又伴随“立即造成Y%攻击力的爆发伤害”，请注意：增益是先触发的！爆发伤害必须使用**强化后的攻击力**（例如 `(基础攻击力 * (1 + 增益比例)) * 爆发倍率`）来计算，切勿用未强化的攻击力计算爆发。
   - **瞬发伤害技能**（如拔刀）：`total_damage` = 技能爆发伤害。`dps` = `total_damage / actual_atk_interval`。
   - **增益类技能**（如攻击力+100%，持续15秒）：需要计算在技能持续期间(`duration`)，干员能打出多少次普攻（`duration / actual_atk_interval`）。`total_damage` = 普攻次数 * 强化后的单次普攻伤害。`dps` = 强化后的单次普攻伤害 / actual_atk_interval。如果该技能带有瞬发伤害，请将瞬发伤害也加到 `total_damage` 中。
   - **永续技能**（如持续时间无穷或duration=0/null）：`total_damage` = 0，重点是返回正确的 `dps` = 强化后的单次普攻伤害 / actual_atk_interval。
   - 无论描述如何，严禁将最终伤害乘以目标数。
5. 必须返回一份完整、可运行的 Python 代码。必须只输出一段 ```python ... ``` 代码块。
"""

USER_PROMPT_TEMPLATE = """【干员参考模板：艾丽妮】
以下是一个完美的范本，请参考其编码风格与结构设计：
```python
from backend.function.logic.professions import Swordmaster
from backend.function.logic.formulas import calculate_physical_damage

class Ii07艾丽妮(Swordmaster):
    \"\"\"
    干员：艾丽妮
    \"\"\"
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：审判之火 (物理伤害有50%概率无视50%防御力)
        self.prob_ignore_def = 0.5
        self.ignore_def_ratio = 0.5
        
        # 天赋 2：净化之剑 (攻击速度+18)
        self.attack_speed += 18
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        \"\"\"
        计算单次命中时的期望物理伤害（考虑审判之火天赋的无视防御概率）
        \"\"\"
        dmg_ignore = calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.ignore_def_ratio)
        dmg_normal = calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=0.0)
        return self.prob_ignore_def * dmg_ignore + (1 - self.prob_ignore_def) * dmg_normal

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (起风)：2次200%攻击力的物理伤害
            atk_val = self.final_base_atk * 2.0
            total_damage = self._calc_hit(atk_val, enemy) * 2
            return {{"total_damage": total_damage, "dps": total_damage / actual_atk_interval}}
            
        elif skill_index == 1:
            # 技能 2 (裂潮)：1次400%攻击力的物理伤害
            atk_val = self.final_base_atk * 4.0
            total_damage = self._calc_hit(atk_val, enemy)
            return {{"total_damage": total_damage, "dps": total_damage / actual_atk_interval}}
            
        elif skill_index == 2:
            # 技能 3 (判决)：1次300%攻击力 + 12次250%攻击力
            hit1_atk = self.final_base_atk * 3.0
            hit2_atk = self.final_base_atk * 2.5
            
            dmg1 = self._calc_hit(hit1_atk, enemy)
            dmg2 = self._calc_hit(hit2_atk, enemy) * 12
            
            total_damage = dmg1 + dmg2
            return {{"total_damage": total_damage, "dps": total_damage / actual_atk_interval}}
            
        return super().calculate_skill_damage(enemy, skill_index, target_count)
```

【待补全干员数据：{operator_name}】
对应的 JSON 数据如下：
```json
{json_data}
```

其目前的空骨架代码如下，请将其补全并输出完整代码：
```python
{stub_code}
```
"""

def extract_python_code(markdown_text: str) -> str:
    match = re.search(r"```python\s*(.*?)\s*```", markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

def build_logic_for_operator(target_id: str) -> bool:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("错误: 未找到 GEMINI_API_KEY。请在 .env 文件中设置。")
        return False
        
    client = genai.Client(api_key=api_key)
    
    # 查找 JSON
    json_path = PARSED_DIR / f"{target_id}.json"
    if not json_path.exists():
        print(f"找不到对应的 JSON 文件: {json_path}")
        return False
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 查找 Python 骨架
    py_path = OPERATORS_DIR / f"{target_id.lower()}.py"
    if not py_path.exists():
        print(f"找不到对应的 Python 文件: {py_path}")
        return False
        
    with open(py_path, "r", encoding="utf-8") as f:
        stub_code = f.read()
        
    print(f"正在调用 Gemini 补全干员 [{target_id}] 的业务逻辑...")
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        operator_name=data.get("name", "Unknown"),
        json_data=json.dumps(data, ensure_ascii=False, indent=2),
        stub_code=stub_code
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.0
            ),
        )
    except Exception as e:
        print(f"调用 API 失败: {e}")
        return False
    
    if not response.text:
        print("模型未返回任何结果。")
        return False
        
    final_code = extract_python_code(response.text)
    
    # 覆写原文件
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(final_code)
        
    print(f"成功更新 {py_path.name}！")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Logic Builder")
    parser.add_argument("--target", type=str, required=True, help="干员的文件基础ID，例如 AA00_乌尔比安")
    args = parser.parse_args()
    
    build_logic_for_operator(args.target)
