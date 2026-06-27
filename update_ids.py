import json
import os
from pathlib import Path

parsed_dir = Path("data/parsed_data")

count = 0
for file in parsed_dir.glob("*.json"):
    try:
        # 提取文件名前四位，如 "AA00_乌尔比安.json" -> "AA00"
        new_id = file.name[:4]
        
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 更新 character_id
        if data.get("character_id") != new_id:
            data["character_id"] = new_id
            
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            count += 1
            
    except Exception as e:
        print(f"Error processing {file.name}: {e}")

print(f"Successfully updated {count} files' character_id.")
