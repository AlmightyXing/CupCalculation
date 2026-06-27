"""
整合流程入口脚本：抓取单个干员信息并进行大模型清洗，保存为 JSON
"""

import argparse
import json
from pathlib import Path
from src.crawler.prts_crawler import crawl_operator
from src.crawler.llm_cleaner import clean_operator_text_to_json

def fetch_and_clean(operator_name: str, output_dir: Path):
    """
    抓取干员信息，利用 LLM 清洗并保存到 output_dir 中
    """
    print(f"[{operator_name}] 开始抓取网页数据...")
    try:
        raw_text = crawl_operator(operator_name)
    except Exception as e:
        print(f"[{operator_name}] 网页抓取失败: {e}")
        return
    
    if not raw_text:
        print(f"[{operator_name}] 未能从页面提取到有效文本")
        return
        
    print(f"[{operator_name}] 网页抓取成功，提取了 {len(raw_text)} 个字符")
    print(f"[{operator_name}] 正在调用大模型进行数据清洗...")
    
    try:
        json_data = clean_operator_text_to_json(operator_name, raw_text)
    except Exception as e:
        print(f"[{operator_name}] 大模型清洗失败: {e}")
        return
        
    char_id = json_data.get("character_id", operator_name)
    output_path = output_dir / f"{char_id}.json"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
        
    print(f"[{operator_name}] 数据提取成功！已保存至 {output_path}")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取单干员的基础信息并生成JSON")
    parser.add_argument("operator", type=str, help="干员名称，例如：玛恩纳、银灰")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/processed", help="输出目录")
    
    args = parser.parse_args()
    fetch_and_clean(args.operator, args.output)
