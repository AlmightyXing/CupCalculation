import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from src.crawler.prts_crawler import crawl_operator
from src.crawler.llm_cleaner import clean_operator_text_to_json

def fetch_single(op_name, display_num):
    print(f"Fetching {op_name}...")
    raw_text = crawl_operator(op_name)
    if not raw_text:
        print("Failed to get raw text")
        return
        
    print("Cleaning via LLM...")
    json_data = clean_operator_text_to_json(op_name, raw_text)
    
    # 按照新规则强制覆写 character_id 
    json_data["character_id"] = display_num
    
    out_path = PROJECT_ROOT / "data" / "parsed_data" / f"{display_num}_{op_name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
        
    print(f"Saved to {out_path}")

if __name__ == '__main__':
    fetch_single("乌尔比安", "AA00")
