import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSED_DIR = PROJECT_ROOT / "data" / "parsed_data"
LOGIC_DIR = PROJECT_ROOT / "backend" / "function" / "logic"
PROFESSIONS_FILE = LOGIC_DIR / "professions.py"
OPERATORS_DIR = LOGIC_DIR / "operators"

# 建立拼音或英文映射字典，用于将中文职业映射为 Python 类名
PROFESSION_NAME_MAP = {
    "解放者": "Liberator",
    "重射手": "HeavyShooter",
    "领主": "Lord",
    "神射手": "Deadeye",
    "速射手": "Marksman",
    "阵法术师": "PhalanxCaster",
    "中坚术师": "CoreCaster",
    "陷阱师": "Trapmaster",
    # 可以继续补充
}

def ensure_dirs():
    OPERATORS_DIR.mkdir(parents=True, exist_ok=True)
    if not (OPERATORS_DIR / "__init__.py").exists():
        (OPERATORS_DIR / "__init__.py").touch()
        
    if not PROFESSIONS_FILE.exists():
        PROFESSIONS_FILE.write_text(
            "from backend.function.logic.base_operator import Operator\n\n", 
            encoding="utf-8"
        )

def get_class_name(zh_name: str) -> str:
    """根据中文职业名称获取合法的类名"""
    return PROFESSION_NAME_MAP.get(zh_name, "UnknownProfession")

def build_profession_class_if_not_exists(profession_zh: str):
    class_name = get_class_name(profession_zh)
    
    content = PROFESSIONS_FILE.read_text(encoding="utf-8")
    if f"class {class_name}(Operator):" in content:
        return class_name
        
    # 如果不存在，动态追加代码
    new_class_code = f"""
class {class_name}(Operator):
    \"\"\"
    职业：{profession_zh}
    \"\"\"
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1
"""
    with open(PROFESSIONS_FILE, "a", encoding="utf-8") as f:
        f.write(new_class_code)
        
    print(f"[Builder] 动态生成职业父类: {class_name} ({profession_zh})")
    return class_name

def build_operator_class(char_id: str, name: str, profession_zh: str):
    parent_class = get_class_name(profession_zh)
    file_name = f"{char_id.lower()}.py"
    file_path = OPERATORS_DIR / file_name
    
    if file_path.exists():
        return
        
    # 类名如 Char103Angel
    class_name_parts = [p.capitalize() for p in char_id.split('_')]
    class_name = "".join(class_name_parts)
    
    code = f"""from backend.function.logic.professions import {parent_class}

class {class_name}({parent_class}):
    \"\"\"
    干员：{name}
    \"\"\"
    def __init__(self, data: dict):
        super().__init__(data)
        self.apply_talents()
        
    def apply_talents(self):
        # TODO: 根据 self.raw_data 中的天赋实现逻辑
        pass
        
    def calculate_dps(self, enemy, skill_index: int = -1):
        # TODO: 实现具体技能的特殊 DPS 计算逻辑
        return super().calculate_dps(enemy, skill_index)
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[Builder] 动态生成干员类: {class_name} 位于 {file_name}")

def scan_and_build():
    """扫描所有已解析的 json，动态生成代码"""
    ensure_dirs()
    if not PARSED_DIR.exists():
        print("未找到 parsed_data 目录，请先运行爬虫。")
        return
        
    for json_file in PARSED_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            profession = data.get("character_type", "")
            char_id = data.get("character_id", "")
            name = data.get("name", "")
            
            if not profession or not char_id:
                continue
                
            # 1. 检查并生成职业父类
            build_profession_class_if_not_exists(profession)
            
            # 2. 生成具体干员类
            build_operator_class(char_id, name, profession)
            
        except Exception as e:
            print(f"处理文件 {json_file.name} 失败: {e}")

if __name__ == "__main__":
    scan_and_build()
