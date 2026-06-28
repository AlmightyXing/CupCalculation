import os
import glob
import time
from pathlib import Path
import sys

# 把项目根目录加到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.src.crawler.llm_logic_builder import build_logic_for_operator

PARSED_DIR = PROJECT_ROOT / "data" / "parsed_data"
LOG_FILE = PROJECT_ROOT / "logs" / "batch_progress.log"

def is_completed(target_id: str) -> bool:
    py_path = PROJECT_ROOT / "backend" / "function" / "logic" / "operators" / f"{target_id.lower()}.py"
    if not py_path.exists():
        return False
    with open(py_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 检查是否包含有效的返回字典格式，这是大模型生成的标志
    return "\"total_damage\":" in content

def main():
    json_files = glob.glob(str(PARSED_DIR / "*.json"))
    total = len(json_files)
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n--- 断点续传重启批量生成，共计 {total} 名干员 ---\n")
        
    for i, json_path in enumerate(json_files, 1):
        filename = os.path.basename(json_path)
        target_id = filename.split(".")[0]
        
        if is_completed(target_id):
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{i}/{total}] {target_id} 已经处理过，跳过。\n")
            continue
            
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{i}/{total}] 正在处理 {target_id}...\n")
            
        success = False
        retries = 3
        while retries > 0 and not success:
            success = build_logic_for_operator(target_id)
            if not success:
                retries -= 1
                if retries > 0:
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"  API调用失败，触发限流保护，等待65秒后重试... (剩余重试次数: {retries})\n")
                    time.sleep(65)
                else:
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"  {target_id} 处理失败！\n")
            else:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"  {target_id} 生成成功！\n")
                
        # API层级提升后，将常态休眠降至1.5秒，提高速度
        time.sleep(1.5)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("批量生成任务已全部完成！\n")

if __name__ == "__main__":
    main()
