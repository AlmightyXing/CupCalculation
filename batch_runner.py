import os
import json
import time
from prts_scraper import get_operator_list, fetch_operator_html, parse_operator_data
from llm_extractor import extract_operator_data

RAW_DIR = "data/raw"
EXTRACTED_DIR = "data/extracted"

def setup_directories():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(EXTRACTED_DIR, exist_ok=True)

def process_all_operators():
    setup_directories()
    
    print("获取六星干员列表...")
    operators = get_operator_list()
    print(f"共获取到 {len(operators)} 名六星干员。")
    
    # 限制单次运行的数量或全量运行
    # 为了防止一次性跑完时间过长，可以自行调整切片例如 operators[:10]
    for idx, name in enumerate(operators):
        print(f"\n[{idx+1}/{len(operators)}] 正在处理干员: {name}")
        
        raw_file = os.path.join(RAW_DIR, f"{name}.json")
        extracted_file = os.path.join(EXTRACTED_DIR, f"{name}.json")
        
        # 1. 获取并保存原始文本数据
        if not os.path.exists(raw_file):
            print(f"  -> 抓取 {name} 的网页数据...")
            try:
                html = fetch_operator_html(name)
                data = parse_operator_data(html, name)
                with open(raw_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                time.sleep(1) # 礼貌性延时，防止对PRTS服务器造成压力
            except Exception as e:
                print(f"  -> 抓取 {name} 失败: {e}")
                continue
        else:
            print(f"  -> {name} 原始数据已存在，跳过抓取。")
            with open(raw_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
        # 2. 调用本地大模型提取结构化数据
        if not os.path.exists(extracted_file):
            print(f"  -> 使用 LLM 提取 {name} 的结构化数据...")
            result = extract_operator_data(data["raw_text"], name)
            
            if result:
                with open(extracted_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  -> 提取成功，已保存至 {extracted_file}")
            else:
                print(f"  -> 提取 {name} 失败。")
        else:
            print(f"  -> {name} 结构化数据已存在，跳过提取。")

if __name__ == "__main__":
    # 您可以在这里添加 try-except 块以防运行中断
    print("开始批量处理管线...")
    process_all_operators()
    print("所有可用干员处理完毕。")
