import requests
import json
import time
import os
from pathlib import Path

# 添加 backend 到系统路径以支持模块导入
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from src.crawler.prts_crawler import crawl_operator
from src.crawler.llm_cleaner import clean_operator_text_to_json

def get_all_6star_operators():
    """从 ArknightsGameData 抓取所有 6 星干员名字"""
    print("正在从 GitHub 抓取明日方舟全量数据字典...")
    url = 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json'
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        six_stars = []
        for k, v in data.items():
            if v.get('rarity') == 'TIER_6' and v.get('isNotObtainable') == False:
                # 过滤掉一些特殊的前缀如阿米娅可能被标记，但6星一般都是标准干员
                six_stars.append(v['name'])
        
        # 去重并排序
        return sorted(list(set(six_stars)))
    except Exception as e:
        print(f"获取干员列表失败: {e}")
        return []

def batch_process():
    raw_dir = PROJECT_ROOT / "data" / "raw_data"
    parsed_dir = PROJECT_ROOT / "data" / "parsed_data"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    parsed_dir.mkdir(parents=True, exist_ok=True)
    
    operators = get_all_6star_operators()
    print(f"共发现 {len(operators)} 名 6星干员。")
    
    for i, op_name in enumerate(operators):
        print(f"\n[{i+1}/{len(operators)}] 开始处理干员：{op_name}")
        
        # 如果已经存在清洗过的 JSON，可以考虑跳过
        # 由于我们目前需要完整跑一次，可以强制覆盖或只跑未存在的
        # 这里加上简单的断点续传检测：如果 parse_data 里有包含该干员名字的文件，则跳过
        existing = list(parsed_dir.glob(f"*{op_name}*.json"))
        if existing:
            print(f"[{op_name}] 已存在清洗数据 {existing[0].name}，跳过...")
            continue
            
        try:
            # 1. 网页爬取并存入 raw
            raw_text = crawl_operator(op_name)
            if not raw_text:
                print(f"[{op_name}] 获取网页失败，跳过。")
                continue
                
            raw_path = raw_dir / f"{op_name}_raw.txt"
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(raw_text)
                
            # 2. 调用大模型清洗并存入 parsed_data
            # 为避免大模型并发限制，加上短暂睡眠
            time.sleep(2) 
            json_data = clean_operator_text_to_json(op_name, raw_text)
            
            char_id = json_data.get("character_id", op_name)
            output_path = parsed_dir / f"{char_id}.json"
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
                
            print(f"[{op_name}] 处理成功，已保存至 {output_path}")
            
        except Exception as e:
            print(f"[{op_name}] 处理期间发生错误: {e}")
            
if __name__ == "__main__":
    # 为了演示与测试，默认开启
    batch_process()
